#!/usr/bin/env python3
"""MLB anytime home run model.

P(HR >= 1) for each starting batter in a game:
  1. Expected PA by lineup slot (home / away), split into PA vs the starter and
     vs the bullpen using the starter's expected batters faced.
  2. Per-PA HR rate = batter skill x pitcher (log5 odds ratio vs league),
     with platoon multipliers, the park HR index for the batter's hand, and
     a weather multiplier (temperature, wind out to CF).
       - Batter skill: Marcel-weighted prior seasons (5/4/3) of HR/PA, barrels/PA,
         xISO and pulled air balls/PA, park neutral, shrunk to average, then
         updated with this season's HR to date.
       - Pitcher: same with HR/BF, barrels/BF, FB%, xISO.
       - Bullpen: the opponent's relief HR rate (last season prior + this season).
  3. P = 1 - (1-p_sp)^n_sp * (1-p_bp)^n_bp, times a calibration constant.

Fair odds = 1/P. Take-at = fair decimal x 1.2 (Tim's rule).

Commands
  python3 hr_model.py backtest --fit 2025 --test 2026   # fit on 2025, score 2026
  python3 hr_model.py fit --season 2026                 # params for next season
  python3 hr_model.py picks --date 2027-03-26           # live slate (or a 2026 date as a replay)
"""
import argparse
import csv
import datetime as dt
import gzip
import json
import math
import os
import re
import sys
import urllib.request
from collections import defaultdict

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "out")
PARAMS = os.path.join(DATA, "model_params.json")
PRIOR_W = {1: 5.0, 2: 4.0, 3: 3.0}
PLATOON_K_BAT = 1000.0   # PA of league-average platoon added to a batter's own split
PLATOON_K_PIT = 1500.0   # BF for a pitcher
SP_BF_SD = 4.5
TAKE_MULT = 1.2
UA = {"User-Agent": "Mozilla/5.0 (research script)"}


def fnum(x, d=None):
    try:
        if x is None or x == "":
            return d
        return float(str(x).replace("%", ""))
    except ValueError:
        return d


def dec_to_american(d):
    if d <= 1:
        return 0
    return round((d - 1) * 100) if d >= 2 else round(-100 / (d - 1))


def fmt_am(a):
    return f"+{a}" if a > 0 else str(a)


# ------------------------------------------------------------------ data store
class Store:
    def __init__(self):
        self.hit, self.pit = {}, {}
        for r in csv.DictReader(open(os.path.join(DATA, "hitters.csv"))):
            self.hit.setdefault(int(r["season"]), {})[int(r["player_id"])] = r
        for r in csv.DictReader(open(os.path.join(DATA, "pitchers.csv"))):
            self.pit.setdefault(int(r["season"]), {})[int(r["player_id"])] = r
        self.hands = {}
        for r in csv.DictReader(open(os.path.join(DATA, "hands.csv"))):
            self.hands[int(r["player_id"])] = (r["bats"] or "R", r["throws"] or "R", r["name"])
        self.parks = {}
        for r in csv.DictReader(open(os.path.join(DATA, "park_factors.csv"))):
            self.parks[(int(r["year"]), int(r["venue_id"]), r["bat_side"])] = fnum(r["hr_index"], 100) / 100
        self.venues = {int(r["venue_id"]): r for r in csv.DictReader(open(os.path.join(DATA, "venues.csv")))}
        self._games = {}
        self.lg = {}
        for y, rows in self.hit.items():
            pa = sum(fnum(r["pa"], 0) for r in rows.values())
            hr = sum(fnum(r["hr"], 0) for r in rows.values())
            bar = sum(fnum(r.get("barrels"), 0) for r in rows.values())
            self.lg[y] = {"hr_pa": hr / pa, "barrel_pa": bar / pa,
                          "xiso": wmean(rows.values(), "xiso", "pa"),
                          "pullair_pa": sum(fnum(r.get("pull_air_pct"), 0) / 100 * fnum(r.get("bbe"), 0)
                                            for r in rows.values()) / pa}
        self.lgp = {}
        for y, rows in self.pit.items():
            bf = sum(fnum(r["bf"], 0) for r in rows.values())
            self.lgp[y] = {"hr_bf": sum(fnum(r["hr"], 0) for r in rows.values()) / bf,
                           "barrel_bf": sum(fnum(r.get("barrels"), 0) for r in rows.values()) / bf,
                           "fb": wmean(rows.values(), "fb_pct", "bf"), "xiso": wmean(rows.values(), "xiso", "bf")}

    def games(self, season):
        if season not in self._games:
            p = os.path.join(RAW, f"games_{season}.json")
            z = os.path.join(DATA, f"games_{season}.json.gz")
            if os.path.exists(p):
                self._games[season] = json.load(open(p))
            elif os.path.exists(z):
                self._games[season] = json.load(gzip.open(z, "rt"))
            else:
                self._games[season] = []
        return self._games[season]

    def hand(self, pid):
        return self.hands.get(pid, ("R", "R", str(pid)))

    def pf(self, year, venue, side):
        """Park HR index (1.0 = average) from the 3-year table ending `year`."""
        for y in (year, year - 1, year + 1, year - 2):
            if side == "S":
                a, b = self.parks.get((y, venue, "L")), self.parks.get((y, venue, "R"))
                if a and b:
                    return (a + b) / 2
            elif (y, venue, side) in self.parks:
                return self.parks[(y, venue, side)]
        return 1.0

    def home_venue(self, season):
        """team_id -> home venue for a season (most common home venue in its games)."""
        for s in (season, season + 1, season - 1, season + 2, season + 3, season + 4):
            g = self.games(s)
            if g:
                cnt = defaultdict(lambda: defaultdict(int))
                for x in g:
                    cnt[x["teams"]["home"]["team_id"]][x["venue_id"]] += 1
                return {t: max(v, key=v.get) for t, v in cnt.items()}
        return {}


def wmean(rows, key, wkey):
    num = den = 0.0
    for r in rows:
        v, w = fnum(r.get(key)), fnum(r.get(wkey), 0)
        if v is not None and w:
            num += v * w
            den += w
    return num / den if den else 0.0


# ------------------------------------------------------------------ stage A: season priors
def season_feats(store, kind, S):
    """Marcel-weighted, park-neutral, league-relative features from seasons S-1..S-3."""
    acc = defaultdict(lambda: defaultdict(float))
    tab = store.hit if kind == "bat" else store.pit
    for k, w in PRIOR_W.items():
        y = S - k
        if y not in tab:
            continue
        hv = store.home_venue(y)
        L = store.lg[y]
        LP = store.lgp[y]
        for pid, r in tab[y].items():
            n = fnum(r["pa"] if kind == "bat" else r["bf"], 0)
            if not n:
                continue
            bats, throws, _ = store.hand(pid)
            ven = hv.get(int(r["team_id"])) if r.get("team_id") else None
            pf = store.pf(y, ven, bats if kind == "bat" else "S") if ven else 1.0
            neut = (1 + pf) / 2
            a = acc[pid]
            a["n"] += w * n
            a["w"] = max(a["w"], w)
            hr = fnum(r["hr"], 0) / neut
            if kind == "bat":
                a["hr"] += w * hr / L["hr_pa"]
                if r.get("barrels") not in (None, ""):
                    a["nb"] += w * n
                    a["bar"] += w * fnum(r["barrels"], 0) / L["barrel_pa"]
                    a["pull"] += w * fnum(r.get("pull_air_pct"), 0) / 100 * fnum(r.get("bbe"), 0) / L["pullair_pa"]
                    a["xiso"] += w * n * fnum(r.get("xiso"), L["xiso"]) / L["xiso"]
                # platoon (raw counts, all prior seasons, no weights)
                for s in ("vl", "vr"):
                    a["pa_" + s] += fnum(r.get("pa_" + s), 0)
                    a["hr_" + s] += fnum(r.get("hr_" + s), 0)
                    a["exp_" + s] += fnum(r.get("pa_" + s), 0) * L["hr_pa"]
            else:
                a["hr"] += w * hr / LP["hr_bf"]
                if r.get("barrels") not in (None, ""):
                    a["nb"] += w * n
                    a["bar"] += w * fnum(r["barrels"], 0) / LP["barrel_bf"]
                    a["fb"] += w * n * fnum(r.get("fb_pct"), LP["fb"]) / LP["fb"]
                    a["xiso"] += w * n * fnum(r.get("xiso"), LP["xiso"]) / LP["xiso"]
                for s in ("vl", "vr"):
                    a["bf_" + s] += fnum(r.get("bf_" + s), 0)
                    a["hr_" + s] += fnum(r.get("hr_" + s), 0)
                    a["exp_" + s] += fnum(r.get("bf_" + s), 0) * LP["hr_bf"]
                gs = fnum(r.get("gs"), 0)
                a["gs"] += gs
    out = {}
    for pid, a in acc.items():
        n = a["n"]
        f = {"n": n / 5.0, "hr": a["hr"] / n}
        if a["nb"]:
            f["bar"] = a["bar"] / a["nb"]
            f["xiso"] = a["xiso"] / a["nb"]
            f["third"] = (a["pull"] if kind == "bat" else a["fb"]) / a["nb"]
        else:
            f["bar"] = f["xiso"] = f["third"] = f["hr"]
        for k in ("pa_vl", "pa_vr", "bf_vl", "bf_vr", "hr_vl", "hr_vr", "exp_vl", "exp_vr", "gs"):
            f[k] = a.get(k, 0.0)
        out[pid] = f
    return out


FEATS = ("hr", "bar", "xiso", "third")


def design(feats, K):
    X = []
    for f in feats:
        w = f["n"] / (f["n"] + K)
        X.append([1.0] + [w * f[k] + (1 - w) * 1.0 for k in FEATS])
    return np.array(X)


def fit_prior(store, kind, S):
    """Fit next-season HR rate index (target season S) on prior features."""
    feats = season_feats(store, kind, S)
    tab = store.hit[S] if kind == "bat" else store.pit[S]
    hv = store.home_venue(S)
    lg = store.lg[S]["hr_pa"] if kind == "bat" else store.lgp[S]["hr_bf"]
    rows, ys, ws, rook = [], [], [], [0.0, 0.0]
    for pid, r in tab.items():
        n = fnum(r["pa"] if kind == "bat" else r["bf"], 0)
        if n < 50:
            continue
        ven = hv.get(int(r["team_id"])) if r.get("team_id") else None
        bats = store.hand(pid)[0]
        pf = store.pf(S, ven, bats if kind == "bat" else "S") if ven else 1.0
        y = fnum(r["hr"], 0) / ((1 + pf) / 2) / n / lg
        if pid in feats:
            rows.append(feats[pid])
            ys.append(y)
            ws.append(n)
        else:
            rook[0] += y * n
            rook[1] += n
    ys, ws = np.array(ys), np.array(ws)
    best = None
    for K in (50, 100, 150, 200, 300, 400, 600, 800, 1200, 1600):
        X = design(rows, K)
        W = np.sqrt(ws)
        beta, *_ = np.linalg.lstsq(X * W[:, None], ys * W, rcond=None)
        sse = float(np.sum(ws * (ys - X @ beta) ** 2))
        if best is None or sse < best[0]:
            best = (sse, K, beta)
    sse, K, beta = best
    base = float(np.sum(ws * (ys - np.average(ys, weights=ws)) ** 2))
    return {"K": K, "beta": [float(b) for b in beta], "rookie": rook[0] / rook[1] if rook[1] else 0.8,
            "r2": 1 - sse / base, "n_players": len(rows)}


def prior_index(feats_by_pid, fit):
    out = {}
    beta = np.array(fit["beta"])
    for pid, f in feats_by_pid.items():
        x = design([f], fit["K"])[0]
        out[pid] = max(0.05, float(x @ beta))
    return out


# ------------------------------------------------------------------ weather
def parse_weather(weather, wind, azimuth=None):
    """Boxscore / feed strings -> (temp F, wind out-to-CF mph, indoor flag)."""
    w = (weather or "").lower()
    indoor = ("dome" in w) or ("roof closed" in w)
    m = re.search(r"(-?\d+)\s*degrees", w)
    temp = float(m.group(1)) if m else 72.0
    out = 0.0
    wd = (wind or "").lower()
    m = re.search(r"(\d+)\s*mph", wd)
    mph = float(m.group(1)) if m else 0.0
    if "out to cf" in wd:
        out = mph
    elif "out to lf" in wd or "out to rf" in wd:
        out = 0.7 * mph
    elif "in from cf" in wd:
        out = -mph
    elif "in from lf" in wd or "in from rf" in wd:
        out = -0.7 * mph
    if indoor:
        temp, out = 72.0, 0.0
    return temp, out, indoor


def wind_out_component(speed_mph, from_deg, azimuth):
    """Wind blowing FROM `from_deg` (meteorological). Azimuth = bearing home plate -> CF."""
    toward = (from_deg + 180) % 360
    return speed_mph * math.cos(math.radians(toward - azimuth))


# ------------------------------------------------------------------ season state (shared by backtest and live)
class SeasonState:
    def __init__(self, store, S, fits):
        self.store, self.S = store, S
        self.yp = S - 1 if (S - 1) in store.lg else S
        self.lg = store.lg[self.yp]["hr_pa"]
        bfe = season_feats(store, "bat", S)
        pfe = season_feats(store, "pit", S)
        self.bfeat, self.pfeat = bfe, pfe
        self.bidx = prior_index(bfe, fits["bat"])
        self.pidx = prior_index(pfe, fits["pit"])
        self.brook, self.prook = fits["bat"]["rookie"], fits["pit"]["rookie"]
        self._platoon_tables(S)
        prev = store.games(S - 1)
        slot_src = prev if prev else store.games(S)
        self.slot_pa = self._slot_pa(slot_src)
        # starter BF and bullpen priors from last season's games
        self.sp_prior, self.lg_sp_bf, self.bp_prior, self.r_share = self._prev_pitching(prev or store.games(S))
        self.acc_b = defaultdict(lambda: [0.0, 0.0])   # hr, park-weighted pa
        self.acc_p = defaultdict(lambda: [0.0, 0.0])
        self.acc_sp = defaultdict(lambda: [0, 0.0])    # starts, bf
        self.acc_bp = defaultdict(lambda: [0.0, 0.0])  # team relief hr, park-weighted bf
        self.lg_td = [0.0, 0.0]                         # league hr, pa this season to date

    def _platoon_tables(self, S):
        """League HR/PA multiplier by batter hand x pitcher hand, prior seasons."""
        st = self.store
        cnt = defaultdict(lambda: [0.0, 0.0])
        tot = [0.0, 0.0]
        for k in PRIOR_W:
            y = S - k
            for pid, r in st.hit.get(y, {}).items():
                b = st.hand(pid)[0]
                for s, t in (("vl", "L"), ("vr", "R")):
                    pa, hr = fnum(r.get("pa_" + s), 0), fnum(r.get("hr_" + s), 0)
                    cnt[(b, t)][0] += hr
                    cnt[(b, t)][1] += pa
                    tot[0] += hr
                    tot[1] += pa
        lg = tot[0] / tot[1]
        self.m = {k: (v[0] / v[1]) / lg if v[1] else 1.0 for k, v in cnt.items()}
        # pitcher side: pitcher hand x effective batter side
        cntp = defaultdict(lambda: [0.0, 0.0])
        totp = [0.0, 0.0]
        for k in PRIOR_W:
            y = S - k
            for pid, r in st.pit.get(y, {}).items():
                t = st.hand(pid)[1]
                for s, e in (("vl", "L"), ("vr", "R")):
                    bf, hr = fnum(r.get("bf_" + s), 0), fnum(r.get("hr_" + s), 0)
                    cntp[(t, e)][0] += hr
                    cntp[(t, e)][1] += bf
                    totp[0] += hr
                    totp[1] += bf
        lgp = totp[0] / totp[1]
        self.mp = {k: (v[0] / v[1]) / lgp if v[1] else 1.0 for k, v in cntp.items()}

    @staticmethod
    def _slot_pa(games):
        s = defaultdict(lambda: [0.0, 0])
        for g in games:
            for side in ("away", "home"):
                for pid, bo, pa, hr in g["teams"][side]["bat"]:
                    if bo % 100 == 0:
                        s[(side, bo // 100)][0] += pa
                        s[(side, bo // 100)][1] += 1
        return {k: v[0] / v[1] for k, v in s.items() if v[1]}

    def _prev_pitching(self, games):
        sp = defaultdict(lambda: [0, 0.0])
        bp = defaultdict(lambda: [0.0, 0.0])
        rbf = [0.0, 0.0]
        allbf = [0.0, 0.0]
        for g in games:
            for side in ("away", "home"):
                t = g["teams"][side]
                if not t["pit"]:
                    continue
                pid, bf, hr, outs = t["pit"][0]
                sp[pid][0] += 1
                sp[pid][1] += bf
                for p2, bf2, hr2, o2 in t["pit"][1:]:
                    bp[t["team_id"]][0] += hr2
                    bp[t["team_id"]][1] += bf2
                    rbf[0 if self.store.hand(p2)[1] == "R" else 1] += bf2
                for p2, bf2, hr2, o2 in t["pit"]:
                    allbf[0] += hr2
                    allbf[1] += bf2
        lg_sp = sum(v[1] for v in sp.values()) / max(1, sum(v[0] for v in sp.values()))
        lg_rate = allbf[0] / allbf[1] if allbf[1] else 0.03
        bp_idx = {}
        for tid, (hr, bf) in bp.items():
            raw = (hr / bf) / lg_rate if bf else 1.0
            bp_idx[tid] = 0.5 * raw + 0.5  # half regression on last season's pen
        return sp, lg_sp, bp_idx, rbf[0] / max(1, sum(rbf))

    def lg_now(self):
        """League HR/PA: last season blended with this season to date (30k PA of prior)."""
        k = 30000.0
        return (self.lg * k + self.lg_td[0]) / (k + self.lg_td[1])

    # -- player estimates
    def bat_index(self, pid, Kb):
        prior = self.bidx.get(pid, self.brook)
        hr, pfpa = self.acc_b[pid]
        return (prior * Kb + hr / self.lg) / (Kb + pfpa)

    def pit_index(self, pid, Kp):
        prior = self.pidx.get(pid, self.prook)
        hr, pfbf = self.acc_p[pid]
        return (prior * Kp + hr / self.lg) / (Kp + pfbf)

    def bp_index(self, tid, Kbp):
        prior = self.bp_prior.get(tid, 1.0)
        hr, pfbf = self.acc_bp[tid]
        return (prior * Kbp + hr / self.lg) / (Kbp + pfbf)

    def sp_bf(self, pid):
        ps = self.sp_prior.get(pid, [0, 0.0])
        n, bf = self.acc_sp[pid]
        k = 5.0
        return (self.lg_sp_bf * k + ps[1] * 0.5 + bf) / (k + ps[0] * 0.5 + n)

    def bat_platoon(self, pid, throws):
        bats = self.store.hand(pid)[0]
        m = self.m.get((bats, throws), 1.0)
        f = self.bfeat.get(pid)
        if not f:
            return m
        s = "vl" if throws == "L" else "vr"
        idx = self.bidx.get(pid, self.brook)
        exp = f["exp_" + s] * idx * m
        ek = PLATOON_K_BAT * self.lg * idx * m
        # own split relative to own overall
        tot_exp = (f["exp_vl"] * self.m.get((bats, "L"), 1) + f["exp_vr"] * self.m.get((bats, "R"), 1)) * idx
        tot_obs = f["hr_vl"] + f["hr_vr"]
        scale = (tot_obs + ek) / (tot_exp + ek) if tot_exp + ek else 1.0
        ratio = (f["hr_" + s] + ek * scale) / (exp * scale + ek * scale) if exp + ek else 1.0
        return m * ratio

    def pit_platoon(self, pid, eff_side):
        f = self.pfeat.get(pid)
        if not f:
            return 1.0
        throws = self.store.hand(pid)[1]
        s = "vl" if eff_side == "L" else "vr"
        mp = self.mp.get((throws, eff_side), 1.0)
        idx = self.pidx.get(pid, self.prook)
        e_l = f["exp_vl"] * idx * self.mp.get((throws, "L"), 1)
        e_r = f["exp_vr"] * idx * self.mp.get((throws, "R"), 1)
        tot_obs = f["hr_vl"] + f["hr_vr"]
        ek = PLATOON_K_PIT * self.lg * idx * mp
        scale = (tot_obs + ek) / (e_l + e_r + ek)
        exp = (e_l if s == "vl" else e_r) * scale
        return (f["hr_" + s] + ek * scale) / (exp + ek * scale)

    # -- rows
    def rows_for_game(self, g, venue_id, temp, wind_out, indoor, date):
        rows = []
        for side, opp in (("away", "home"), ("home", "away")):
            t, o = g["teams"][side], g["teams"][opp]
            if not o["pit"]:
                continue
            sp = o["pit"][0][0]
            sp_throws = self.store.hand(sp)[1]
            mu = self.sp_bf(sp)
            for pid, bo, pa, hr in t["bat"]:
                if bo % 100 != 0:
                    continue
                slot = bo // 100
                bats, _, name = self.store.hand(pid)
                eff = bats if bats != "S" else ("R" if sp_throws == "L" else "L")
                n = self.slot_pa.get((side, slot), 4.0)
                # PA vs starter: count slot appearances within the starter's BF
                n_sp = 0.0
                for j in range(6):
                    k = slot + 9 * j
                    n_sp += 0.5 * math.erfc((k - 0.5 - mu) / (SP_BF_SD * math.sqrt(2)))
                n_sp = min(n_sp, n)
                bp_mix = self.r_share * self.bat_platoon(pid, "R") + (1 - self.r_share) * self.bat_platoon(pid, "L")
                rows.append({
                    "date": date, "game_pk": g.get("game_pk"), "side": side, "team": t["team"], "opp": o["team"],
                    "team_id": t["team_id"], "opp_id": o["team_id"], "pid": pid, "name": name, "slot": slot,
                    "bats": bats, "sp": sp, "sp_name": self.store.hand(sp)[2], "sp_throws": sp_throws,
                    "b_prior": self.bidx.get(pid, self.brook), "b_hr": self.acc_b[pid][0], "b_pfpa": self.acc_b[pid][1],
                    "p_prior": self.pidx.get(sp, self.prook), "p_hr": self.acc_p[sp][0], "p_pfbf": self.acc_p[sp][1],
                    "bp_prior": self.bp_prior.get(o["team_id"], 1.0), "bp_hr": self.acc_bp[o["team_id"]][0],
                    "bp_pfbf": self.acc_bp[o["team_id"]][1],
                    "plat_b": self.bat_platoon(pid, sp_throws), "plat_p": self.pit_platoon(sp, eff), "plat_bp": bp_mix,
                    "pf": self.store.pf(self.S - 1, venue_id, eff), "n": n, "n_sp": n_sp,
                    "temp": temp, "wind": wind_out, "indoor": int(indoor), "lg": self.lg_now(),
                    "pa": pa, "hr": hr, "y": int(hr > 0),
                })
        return rows

    def update(self, g):
        v = g["venue_id"]
        for side, opp in (("away", "home"), ("home", "away")):
            t, o = g["teams"][side], g["teams"][opp]
            sp_throws = self.store.hand(o["pit"][0][0])[1] if o["pit"] else "R"
            for pid, bo, pa, hr in t["bat"]:
                bats = self.store.hand(pid)[0]
                eff = bats if bats != "S" else ("R" if sp_throws == "L" else "L")
                pf = self.store.pf(self.S - 1, v, eff)
                self.acc_b[pid][0] += hr
                self.acc_b[pid][1] += pa * pf
                self.lg_td[0] += hr
                self.lg_td[1] += pa
            pfa = self.store.pf(self.S - 1, v, "S")
            for i, (pid, bf, hr, outs) in enumerate(o["pit"]):
                self.acc_p[pid][0] += hr
                self.acc_p[pid][1] += bf * pfa
                if i == 0:
                    self.acc_sp[pid][0] += 1
                    self.acc_sp[pid][1] += bf
                else:
                    self.acc_bp[o["team_id"]][0] += hr
                    self.acc_bp[o["team_id"]][1] += bf * pfa


def season_rows(store, S, fits):
    st = SeasonState(store, S, fits)
    games = store.games(S)
    rows = []
    by_date = defaultdict(list)
    for g in games:
        by_date[g["date"]].append(g)
    for d in sorted(by_date):
        for g in by_date[d]:
            ven = store.venues.get(g["venue_id"], {})
            temp, wind, indoor = parse_weather(g["weather"], g["wind"])
            rows += st.rows_for_game(g, g["venue_id"], temp, wind, indoor, d)
        for g in by_date[d]:
            st.update(g)
    return rows, st


# ------------------------------------------------------------------ stage B: game model
PNAMES = ["log_Kb", "log_Kp", "log_Kbp", "alpha", "bT", "bW", "log_c", "gamma"]
P0 = [math.log(300), math.log(400), math.log(1500), 1.0, 0.01, 0.01, 0.0, 1.0]


def arrays(rows):
    keys = ["b_prior", "b_hr", "b_pfpa", "p_prior", "p_hr", "p_pfbf", "bp_prior", "bp_hr", "bp_pfbf",
            "plat_b", "plat_p", "plat_bp", "pf", "n", "n_sp", "temp", "wind", "indoor", "lg", "y"]
    return {k: np.array([r[k] for r in rows], dtype=float) for k in keys}


def predict(A, p):
    Kb, Kp, Kbp = (math.exp(min(x, 9.0)) for x in p[:3])
    gamma = p[7] if len(p) > 7 else 1.0
    alpha, bT, bW, c = p[3], p[4], p[5], math.exp(p[6])
    lg = A["lg"]  # league HR/PA now (last season blended with this season to date)
    bi = (A["b_prior"] * Kb + A["b_hr"] / lg) / (Kb + A["b_pfpa"])
    pi = (A["p_prior"] * Kp + A["p_hr"] / lg) / (Kp + A["p_pfbf"])
    bpi = (A["bp_prior"] * Kbp + A["bp_hr"] / lg) / (Kbp + A["bp_pfbf"])
    env = np.power(A["pf"], alpha) * np.exp(bT * (A["temp"] - 72) + bW * A["wind"]) * c

    def log5(b, q):
        ob = b / (1 - b)
        oq = q / (1 - q)
        ol = lg / (1 - lg)
        o = ob * oq / ol
        return o / (1 + o)

    rb_sp = np.clip(lg * bi * A["plat_b"], 1e-4, 0.5)
    rp = np.clip(lg * pi * A["plat_p"], 1e-4, 0.5)
    rb_bp = np.clip(lg * bi * A["plat_bp"], 1e-4, 0.5)
    rbp = np.clip(lg * bpi, 1e-4, 0.5)
    # gamma < 1 pulls extreme matchups back toward league (fixes top-end overconfidence)
    p_sp = np.clip(lg * np.power(log5(rb_sp, rp) / lg, gamma) * env, 1e-5, 0.6)
    p_bp = np.clip(lg * np.power(log5(rb_bp, rbp) / lg, gamma) * env, 1e-5, 0.6)
    n_bp = np.maximum(A["n"] - A["n_sp"], 0)
    q = 1 - np.power(1 - p_sp, A["n_sp"]) * np.power(1 - p_bp, n_bp)
    return np.clip(q, 1e-4, 0.95)


TOP_KNEE, TOP_SLOPE = 0.16, 0.75


def top_adjust(q):
    """Top-end haircut for picks. 2026 out-of-sample: daily top picks priced at 25-28%
    hit 21-22%. Above 16% keep only 75% of the excess."""
    q = np.asarray(q, dtype=float)
    return np.where(q > TOP_KNEE, TOP_KNEE + (q - TOP_KNEE) * TOP_SLOPE, q)


def logloss(y, q):
    return float(-np.mean(y * np.log(q) + (1 - y) * np.log(1 - q)))


def fit_game(A):
    def obj(p):
        return logloss(A["y"], predict(A, p))
    r = minimize(obj, P0, method="Nelder-Mead", options={"maxiter": 3000, "xatol": 1e-3, "fatol": 1e-7})
    return [float(x) for x in r.x], r.fun


def fit_all(store, S):
    fits = {"bat": fit_prior(store, "bat", S), "pit": fit_prior(store, "pit", S)}
    rows, _ = season_rows(store, S, fits)
    A = arrays(rows)
    p, ll = fit_game(A)
    return {"season_fit": S, "fits": fits, "game_params": p, "param_names": PNAMES,
            "train_logloss": ll, "train_rows": len(rows)}


# ------------------------------------------------------------------ backtest report
def report(rows, q, label):
    y = np.array([r["y"] for r in rows], dtype=float)
    base = np.full_like(q, y.mean())
    lines = [f"## {label}", "",
             f"Starters scored: {len(y)} batter-games, {len(set(r['date'] for r in rows))} dates. "
             f"Actual HR rate {100 * y.mean():.1f}%, model mean {100 * q.mean():.1f}%.", "",
             f"Log loss {logloss(y, q):.4f} vs {logloss(y, base):.4f} for a flat rate "
             f"(skill {100 * (1 - logloss(y, q) / logloss(y, base)):.1f}%). "
             f"Brier {np.mean((q - y) ** 2):.4f} vs {np.mean((base - y) ** 2):.4f}.", "",
             "| Model P(HR) | Batter-games | Predicted | Actual |", "|---|---|---|---|"]
    cal = []
    edges = [0, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.23, 1]
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (q >= lo) & (q < hi)
        if m.sum() == 0:
            continue
        cal.append({"lo": lo, "hi": hi, "n": int(m.sum()), "pred": float(q[m].mean()), "act": float(y[m].mean())})
        lab = f"{100 * lo:.0f}-{100 * hi:.0f}%" if hi < 1 else f"{100 * lo:.0f}%+"
        lines.append(f"| {lab} | {m.sum()} | {100 * q[m].mean():.1f}% | {100 * y[m].mean():.1f}% |")
    lines += ["", "Top-N picks per day (all games that day, ranked by model P):", "",
              "| N per day | Picks | Predicted | Hit rate | Avg fair |", "|---|---|---|---|---|"]
    by_date = defaultdict(list)
    for i, r in enumerate(rows):
        by_date[r["date"]].append(i)
    topn = []
    for N in (1, 3, 5, 10):
        idx = []
        for d, ii in by_date.items():
            ii = sorted(ii, key=lambda i: -q[i])[:N]
            idx += ii
        idx = np.array(idx)
        pr, ac = q[idx].mean(), y[idx].mean()
        topn.append({"N": N, "picks": len(idx), "pred": float(pr), "act": float(ac)})
        lines.append(f"| {N} | {len(idx)} | {100 * pr:.1f}% | {100 * ac:.1f}% | {fmt_am(dec_to_american(1 / pr))} |")
    return "\n".join(lines), cal, topn


def cmd_backtest(a):
    store = Store()
    print(f"fitting on {a.fit}")
    P = fit_all(store, a.fit)
    print(json.dumps({k: P[k] for k in ("game_params", "train_logloss")}, indent=1))
    print("bat prior", P["fits"]["bat"], "\npit prior", P["fits"]["pit"])
    fits = {"bat": fit_prior(store, "bat", a.fit), "pit": fit_prior(store, "pit", a.fit)}
    rows, _ = season_rows(store, a.test, fits)
    A = arrays(rows)
    q = predict(A, P["game_params"])
    txt, cal, topn = report(rows, q, f"Backtest {a.test} (fit on {a.fit}, priors from {a.test - 3}-{a.test - 1})")
    # simple comparison: no in-season, no pitcher, no park, no weather
    p_simple = list(P["game_params"])
    p_simple[3] = 0.0
    p_simple[4] = p_simple[5] = 0.0
    p_simple[7] = 1.0
    A2 = dict(A)
    A2["p_prior"] = np.ones_like(A["p_prior"])
    A2["p_hr"] = np.zeros_like(A["p_hr"])
    A2["plat_p"] = np.ones_like(A["plat_p"])
    A2["bp_prior"] = np.ones_like(A["bp_prior"])
    A2["bp_hr"] = np.zeros_like(A["bp_hr"])
    q2 = predict(A2, p_simple)
    y = A["y"]
    txt += (f"\n\nBatter-only version (same batter skill and lineup PA; no pitcher, bullpen, park or weather): "
            f"log loss {logloss(y, q2):.4f} vs full {logloss(y, q):.4f}.")
    qa = top_adjust(q)
    txt2, cal2, topn2 = report(rows, qa, f"Same {a.test} backtest with the top-end haircut used for picks")
    txt += "\n\n" + txt2
    print(txt)
    os.makedirs(os.path.join(HERE, "backtest"), exist_ok=True)
    with open(os.path.join(HERE, "backtest", f"results_{a.test}.txt"), "w") as f:
        f.write(txt + "\n\nFit params: " + json.dumps(P["game_params"]) + "\n")
    with open(os.path.join(HERE, "backtest", f"calibration_{a.test}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["lo", "hi", "n", "pred", "act"])
        w.writeheader()
        w.writerows(cal)
    with open(os.path.join(HERE, "backtest", f"topn_{a.test}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["N", "picks", "pred", "act"])
        w.writeheader()
        w.writerows(topn)
    if a.save_picks:
        with open(os.path.join(RAW, f"backtest_rows_{a.test}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "team", "opp", "name", "slot", "sp_name", "temp", "wind", "pf", "p", "hr"])
            for r, qq in zip(rows, q):
                w.writerow([r["date"], r["team"], r["opp"], r["name"], r["slot"], r["sp_name"], r["temp"], r["wind"],
                            round(r["pf"], 2), round(float(qq), 4), r["hr"]])


def cmd_fit(a):
    store = Store()
    P = fit_all(store, a.season)
    json.dump(P, open(PARAMS, "w"), indent=1)
    print(f"wrote {PARAMS}")
    print(json.dumps(P, indent=1))


# ------------------------------------------------------------------ live picks
STATS = "https://statsapi.mlb.com/api/v1"


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def nws_weather(lat, lon, when_utc):
    """api.weather.gov hourly forecast -> (temp F, wind mph, wind-from degrees)."""
    pts = get_json(f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}")
    fc = get_json(pts["properties"]["forecastHourly"])
    best = None
    for p in fc["properties"]["periods"]:
        t = dt.datetime.fromisoformat(p["startTime"])
        gap = abs((t - when_utc).total_seconds())
        if best is None or gap < best[0]:
            best = (gap, p)
    p = best[1]
    temp = float(p["temperature"]) if p.get("temperatureUnit", "F") == "F" else float(p["temperature"]) * 9 / 5 + 32
    m = re.findall(r"\d+", p.get("windSpeed", "0"))
    mph = max(float(x) for x in m) if m else 0.0
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    d = p.get("windDirection", "N")
    deg = dirs.index(d) * 22.5 if d in dirs else 0.0
    return temp, mph, deg


def live_games(date, store, S):
    """Schedule with probable pitchers + lineups. Falls back to the last lineup a team used."""
    d = get_json(f"{STATS}/schedule?sportId=1&date={date}&hydrate=probablePitcher,lineups,weather,venue,team")
    out = []
    last_lineup = {}
    for g in store.games(S):
        if g["date"] < date:
            for side in ("away", "home"):
                t = g["teams"][side]
                last_lineup[t["team_id"]] = [b[:2] for b in t["bat"] if b[1] % 100 == 0]
    for dd in d.get("dates", []):
        for x in dd["games"]:
            g = {"game_pk": x["gamePk"], "venue_id": x["venue"]["id"], "teams": {}, "time": x["gameDate"],
                 "weather": x.get("weather", {}), "notes": []}
            lu = x.get("lineups", {})
            for side in ("away", "home"):
                tm = x["teams"][side]
                tid = tm["team"]["id"]
                pp = tm.get("probablePitcher", {}).get("id")
                key = "awayPlayers" if side == "away" else "homePlayers"
                if lu.get(key):
                    bat = [[p["id"], 100 * (i + 1), 0, 0] for i, p in enumerate(lu[key])]
                    src = "confirmed"
                else:
                    bat = [[pid, bo, 0, 0] for pid, bo in last_lineup.get(tid, [])]
                    src = "projected (last lineup)"
                abbr = tm["team"].get("abbreviation") or tm["team"]["name"]
                g["teams"][side] = {"team_id": tid, "team": abbr, "bat": bat,
                                    "pit": [[pp, 0, 0, 0]] if pp else [], "lineup": src}
            out.append(g)
    return out


def game_weather(g, store, override):
    if g["game_pk"] in override:
        return override[g["game_pk"]]
    ven = store.venues.get(g["venue_id"], {})
    w = g.get("weather") or {}
    if w.get("temp"):
        return parse_weather(f"{w['temp']} degrees, {w.get('condition', '')}", w.get("wind", ""))
    roof = (ven.get("roof") or "").lower()
    if roof == "dome":
        return 72.0, 0.0, True
    try:
        when = dt.datetime.fromisoformat(g["time"].replace("Z", "+00:00"))
        temp, mph, deg = nws_weather(float(ven["lat"]), float(ven["lon"]), when)
        out = wind_out_component(mph, deg, float(ven["azimuth"]))
        # retractable roofs: assume closed below 60F (team calls vary; check the feed on game day)
        if roof == "retractable" and temp < 60:
            return 72.0, 0.0, True
        return temp, out, False
    except Exception as e:  # noqa: BLE001
        g["notes"].append(f"weather unavailable ({e.__class__.__name__}); neutral used")
        return 72.0, 0.0, False


def cmd_picks(a):
    store = Store()
    if not os.path.exists(PARAMS):
        sys.exit("run `hr_model.py fit --season <last full season>` first")
    P = json.load(open(PARAMS))
    S = int(a.date[:4])
    replay = (not a.live) and any(g["date"] == a.date for g in store.games(S))
    st = SeasonState(store, S, P["fits"])
    for g in store.games(S):
        if g["date"] < a.date:
            st.update(g)
    override = {}
    if a.weather:
        for item in a.weather.split(";"):
            pk, t, w = item.split(",")
            override[int(pk)] = (float(t), float(w), False)
    if replay:
        games = [dict(g, notes=[], time="") for g in store.games(S) if g["date"] == a.date]
        for g in games:
            g["teams"] = {s: dict(t, pit=t["pit"][:1], lineup="replay") for s, t in g["teams"].items()}
    else:
        games = live_games(a.date, store, S)
    rows, notes = [], []
    for g in games:
        if replay:
            temp, wind, indoor = parse_weather(g["weather"], g["wind"])
        else:
            temp, wind, indoor = game_weather(g, store, override)
        rr = st.rows_for_game(g, g["venue_id"], temp, wind, indoor, a.date)
        for r in rr:
            r["lineup"] = g["teams"][r["side"]]["lineup"]
            r["venue"] = store.venues.get(g["venue_id"], {}).get("venue", "")
        rows += rr
        notes += [f"{g['teams']['away']['team']} at {g['teams']['home']['team']}: {n}" for n in g["notes"]]
        for s in ("away", "home"):
            if not g["teams"][s]["pit"]:
                notes.append(f"{g['teams'][s]['team']}: no probable pitcher yet; opposing hitters skipped")
    if not rows:
        print("no games / lineups for", a.date)
        return
    q = top_adjust(predict(arrays(rows), P["game_params"]))
    order = np.argsort(-q)
    os.makedirs(OUT, exist_ok=True)
    csvp = os.path.join(OUT, f"picks_{a.date}.csv")
    with open(csvp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "game", "team", "slot", "batter", "bats", "opp_sp", "sp_throws", "venue", "temp", "wind_out",
                    "park_hr", "p_hr", "fair", "take_at", "lineup", "actual_hr"])
        for i in order:
            r = rows[i]
            fair = 1 / q[i]
            w.writerow([a.date, f"{r['team'] if r['side'] == 'away' else r['opp']} at {r['opp'] if r['side'] == 'away' else r['team']}",
                        r["team"], r["slot"], r["name"], r["bats"], r["sp_name"], r["sp_throws"], r["venue"],
                        r["temp"], round(r["wind"], 1), round(r["pf"], 2), round(float(q[i]), 4),
                        fmt_am(dec_to_american(fair)), fmt_am(dec_to_american(fair * TAKE_MULT)), r["lineup"],
                        r["hr"] if replay else ""])
    md = [f"# MLB anytime HR shortlist {a.date}", "",
          "Fair = 1 / model chance. Take at = fair decimal x1.2; bet only at that price or longer. Small stakes.", "",
          "| # | Batter | Team | Slot | vs SP | Park | Temp/Wind out | P(HR) | Fair | Take at |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k, i in enumerate(order[: a.top]):
        r = rows[i]
        fair = 1 / q[i]
        hit = f" ({'HR' if r['hr'] else 'no'})" if replay else ""
        md.append(f"| {k + 1} | {r['name']}{hit} | {r['team']} | {r['slot']} | {r['sp_name']} ({r['sp_throws']}) | "
                  f"{r['pf']:.2f} | {r['temp']:.0f}F / {r['wind']:+.0f} | {100 * q[i]:.1f}% | "
                  f"{fmt_am(dec_to_american(fair))} | {fmt_am(dec_to_american(fair * TAKE_MULT))} |")
    if notes:
        md += ["", "Notes:"] + [f"- {n}" for n in notes]
    srcs = sorted(set(r["lineup"] for r in rows))
    md += ["", f"Lineups: {', '.join(srcs)}."]
    mdp = os.path.join(OUT, f"shortlist_{a.date}.md")
    open(mdp, "w").write("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"\nwrote {csvp}\nwrote {mdp}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("backtest")
    b.add_argument("--fit", type=int, default=2025)
    b.add_argument("--test", type=int, default=2026)
    b.add_argument("--save-picks", action="store_true")
    f = sub.add_parser("fit")
    f.add_argument("--season", type=int, required=True)
    p = sub.add_parser("picks")
    p.add_argument("--date", required=True)
    p.add_argument("--top", type=int, default=15)
    p.add_argument("--live", action="store_true", help="use the live schedule/lineups even for a past date")
    p.add_argument("--weather", default="", help="override: 'gamePk,tempF,windOutMph;...'")
    a = ap.parse_args()
    {"backtest": cmd_backtest, "fit": cmd_fit, "picks": cmd_picks}[a.cmd](a)


if __name__ == "__main__":
    main()
