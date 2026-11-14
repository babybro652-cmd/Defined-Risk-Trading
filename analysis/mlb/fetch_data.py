#!/usr/bin/env python3
"""Pull MLB home run inputs from free public sources.

Sources
  - Baseball Savant custom + batted-ball leaderboards (CSV): barrel%, hard-hit%,
    launch angle, xISO, xSLG, FB%, pull-air rate, for hitters and pitchers.
  - Baseball Savant Statcast park factors (HR index by batter hand, 3-year rolling).
  - MLB Stats API: season hitting / pitching lines, vs LHP / RHP splits, venues
    (lat/long, field azimuth, roof), player handedness, schedules and boxscores.

Raw downloads go to analysis/mlb/raw/ (gitignored). Cleaned tables go to
analysis/mlb/data/ (committed).

Usage
  python3 analysis/mlb/fetch_data.py                 # leaderboards, splits, parks (2023-2026)
  python3 analysis/mlb/fetch_data.py --seasons 2027  # add a new season
  python3 analysis/mlb/fetch_data.py --games 2026    # parse every boxscore of a season
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
DATA = os.path.join(HERE, "data")
UA = {"User-Agent": "Mozilla/5.0 (research script)"}
SAVANT = "https://baseballsavant.mlb.com"
STATS = "https://statsapi.mlb.com/api/v1"


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8-sig")
        except Exception as e:  # noqa: BLE001
            if i == tries - 1:
                raise
            time.sleep(2 + 3 * i)


def get_json(url):
    return json.loads(get(url))


def write_csv(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"  wrote {os.path.relpath(path, HERE)} ({len(rows)} rows)")


def fnum(x):
    try:
        return float(str(x).replace("%", ""))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- Savant
BAT_SEL = "pa,home_run,barrel,batted_ball,barrel_batted_rate,hard_hit_percent,launch_angle_avg,exit_velocity_avg,sweet_spot_percent,xiso,xslg,flyballs_percent,pull_percent"
PIT_SEL = "pa,home_run,p_formatted_ip,barrel,batted_ball,barrel_batted_rate,hard_hit_percent,launch_angle_avg,flyballs_percent,xiso,xslg"


def savant_custom(kind, year):
    sel = BAT_SEL if kind == "batter" else PIT_SEL
    url = f"{SAVANT}/leaderboard/custom?year={year}&type={kind}&filter=&min=1&selections={sel}&chart=false&csv=true"
    txt = get(url)
    with open(os.path.join(RAW, f"savant_custom_{kind}_{year}.csv"), "w") as f:
        f.write(txt)
    return list(csv.DictReader(io.StringIO(txt)))


def savant_battedball(kind, year):
    url = f"{SAVANT}/leaderboard/batted-ball?type={kind}&season%5B%5D={year}&min=1&csv=true"
    txt = get(url)
    with open(os.path.join(RAW, f"savant_bb_{kind}_{year}.csv"), "w") as f:
        f.write(txt)
    return {int(r["id"]): r for r in csv.DictReader(io.StringIO(txt))}


def savant_parks(year):
    out = []
    for side in ("L", "R"):
        url = f"{SAVANT}/leaderboard/statcast-park-factors?type=year&year={year}&batSide={side}&stat=index_hr&condition=All&rolling=3"
        html = get(url)
        m = re.search(r"var data = (\[.*?\]);", html, re.S)
        if not m:
            print(f"  park factors {year} {side}: no data block")
            continue
        for r in json.loads(m.group(1)):
            out.append({"year": year, "bat_side": side, "venue_id": int(r["venue_id"]),
                        "venue": r["venue_name"], "team": r["name_display_club"],
                        "years": r.get("year_range"), "n_pa": r.get("n_pa"),
                        "hr_index": fnum(r.get("index_hr")), "hardhit_index": fnum(r.get("index_hardhit")),
                        "runs_index": fnum(r.get("index_runs"))})
    return out


# ---------------------------------------------------------------- Stats API
def season_lines(group, year):
    url = f"{STATS}/stats?stats=season&group={group}&season={year}&playerPool=ALL&limit=5000&sportId=1"
    return get_json(url)["stats"][0]["splits"]


def platoon_splits(group, year):
    url = f"{STATS}/stats?stats=statSplits&group={group}&season={year}&sitCodes=vl,vr&playerPool=ALL&limit=5000&sportId=1"
    return get_json(url)["stats"][0]["splits"]


def build_hitters(years):
    rows = []
    for y in years:
        print(f"hitters {y}")
        cust = savant_custom("batter", y)
        bb = savant_battedball("batter", y)
        lines = {s["player"]["id"]: s for s in season_lines("hitting", y)}
        spl = {}
        for s in platoon_splits("hitting", y):
            spl.setdefault(s["player"]["id"], {})[s["split"]["code"]] = s["stat"]
        seen = set()
        for r in cust:
            pid = int(r["player_id"])
            seen.add(pid)
            b = bb.get(pid, {})
            ln = lines.get(pid, {})
            st = ln.get("stat", {})
            sp = spl.get(pid, {})
            pa = fnum(r["pa"]) or 0
            hr = fnum(r["home_run"]) or 0
            air = fnum(b.get("air_rate"))
            pull_air = fnum(b.get("pull_air_rate"))
            vl, vr = sp.get("vl", {}), sp.get("vr", {})
            rows.append({
                "season": y, "player_id": pid, "name": r["last_name, first_name"],
                "team": ln.get("team", {}).get("name", ""), "team_id": ln.get("team", {}).get("id", ""),
                "pa": int(pa), "hr": int(hr), "hr_pa": round(hr / pa, 4) if pa else "",
                "bbe": r.get("batted_ball"), "barrels": r.get("barrel"),
                "barrel_pa": round((fnum(r.get("barrel")) or 0) / pa, 4) if pa else "",
                "barrel_pct": r["barrel_batted_rate"], "hardhit_pct": r["hard_hit_percent"],
                "launch_angle": r["launch_angle_avg"], "ev_avg": r["exit_velocity_avg"],
                "sweet_spot_pct": r["sweet_spot_percent"], "fb_pct": r["flyballs_percent"],
                "pull_pct": r["pull_percent"],
                "pull_air_pct": round(100 * pull_air, 1) if pull_air is not None else "",
                "pull_pct_on_air": round(100 * pull_air / air, 1) if air and pull_air is not None else "",
                "xiso": r["xiso"], "xslg": r["xslg"],
                "iso": st.get("slg") and round(fnum(st.get("slg")) - fnum(st.get("avg")), 3),
                "pa_vl": vl.get("plateAppearances", 0), "hr_vl": vl.get("homeRuns", 0),
                "pa_vr": vr.get("plateAppearances", 0), "hr_vr": vr.get("homeRuns", 0),
            })
        # Stats API hitters missing from Savant (tiny samples)
        for pid, ln in lines.items():
            if pid in seen:
                continue
            st = ln["stat"]
            pa = st.get("plateAppearances", 0)
            if not pa:
                continue
            sp = spl.get(pid, {})
            vl, vr = sp.get("vl", {}), sp.get("vr", {})
            rows.append({"season": y, "player_id": pid, "name": ln["player"]["fullName"],
                         "team": ln.get("team", {}).get("name", ""), "team_id": ln.get("team", {}).get("id", ""), "pa": pa, "hr": st.get("homeRuns", 0),
                         "hr_pa": round(st.get("homeRuns", 0) / pa, 4),
                         "pa_vl": vl.get("plateAppearances", 0), "hr_vl": vl.get("homeRuns", 0),
                         "pa_vr": vr.get("plateAppearances", 0), "hr_vr": vr.get("homeRuns", 0)})
    return rows


HIT_FIELDS = ["season", "player_id", "name", "team", "team_id", "pa", "hr", "hr_pa", "bbe", "barrels", "barrel_pa",
              "barrel_pct", "hardhit_pct", "launch_angle", "ev_avg", "sweet_spot_pct", "fb_pct", "pull_pct",
              "pull_air_pct", "pull_pct_on_air", "xiso", "xslg", "iso", "pa_vl", "hr_vl", "pa_vr", "hr_vr"]


def build_pitchers(years):
    rows = []
    for y in years:
        print(f"pitchers {y}")
        cust = savant_custom("pitcher", y)
        bb = savant_battedball("pitcher", y)
        lines = {s["player"]["id"]: s for s in season_lines("pitching", y)}
        spl = {}
        for s in platoon_splits("pitching", y):
            spl.setdefault(s["player"]["id"], {})[s["split"]["code"]] = s["stat"]
        for r in cust:
            pid = int(r["player_id"])
            b = bb.get(pid, {})
            ln = lines.get(pid, {})
            st = ln.get("stat", {})
            sp = spl.get(pid, {})
            bf = fnum(r["pa"]) or 0
            hr = fnum(r["home_run"]) or 0
            bbe = fnum(r.get("batted_ball")) or 0
            fb_rate = fnum(b.get("fb_rate"))
            fb_n = fb_rate * fnum(b.get("bbe") or 0) if fb_rate is not None else None
            outs = st.get("outs")
            ip = outs / 3 if outs else None
            vl, vr = sp.get("vl", {}), sp.get("vr", {})
            rows.append({
                "season": y, "player_id": pid, "name": r["last_name, first_name"],
                "team": ln.get("team", {}).get("name", ""), "team_id": ln.get("team", {}).get("id", ""),
                "gs": st.get("gamesStarted", ""), "g": st.get("gamesPitched", ""),
                "ip": round(ip, 1) if ip else r["p_formatted_ip"], "bf": int(bf), "hr": int(hr),
                "hr_bf": round(hr / bf, 4) if bf else "",
                "hr9": round(9 * hr / ip, 2) if ip else "",
                "hr_fb": round(hr / fb_n, 3) if fb_n else "",
                "barrels": r.get("barrel"), "barrel_bf": round((fnum(r.get("barrel")) or 0) / bf, 4) if bf else "",
                "barrel_pct": r["barrel_batted_rate"], "hardhit_pct": r["hard_hit_percent"],
                "launch_angle": r["launch_angle_avg"], "fb_pct": r["flyballs_percent"],
                "fb_rate_bb": round(100 * fb_rate, 1) if fb_rate is not None else "",
                "xiso": r["xiso"], "xslg": r["xslg"],
                "bf_vl": vl.get("battersFaced", 0), "hr_vl": vl.get("homeRuns", 0),
                "bf_vr": vr.get("battersFaced", 0), "hr_vr": vr.get("homeRuns", 0),
            })
    return rows


PIT_FIELDS = ["season", "player_id", "name", "team", "team_id", "gs", "g", "ip", "bf", "hr", "hr_bf", "hr9", "hr_fb",
              "barrels", "barrel_bf", "barrel_pct", "hardhit_pct", "launch_angle", "fb_pct", "fb_rate_bb",
              "xiso", "xslg", "bf_vl", "hr_vl", "bf_vr", "hr_vr"]


def build_venues(year):
    d = get_json(f"{STATS}/venues?sportId=1&season={year}&hydrate=location,fieldInfo")
    rows = []
    for v in d["venues"]:
        loc, fi = v.get("location", {}), v.get("fieldInfo", {})
        c = loc.get("defaultCoordinates", {})
        rows.append({"venue_id": v["id"], "venue": v["name"], "city": loc.get("city"),
                     "lat": c.get("latitude"), "lon": c.get("longitude"),
                     "azimuth": loc.get("azimuthAngle"), "elevation_ft": loc.get("elevation"),
                     "roof": fi.get("roofType"), "lf": fi.get("leftLine"), "cf": fi.get("center"),
                     "rf": fi.get("rightLine")})
    return rows


def people_hands(ids):
    out = {}
    ids = sorted(set(ids))
    for i in range(0, len(ids), 150):
        chunk = ",".join(str(x) for x in ids[i:i + 150])
        for p in get_json(f"{STATS}/people?personIds={chunk}")["people"]:
            out[p["id"]] = {"player_id": p["id"], "name": p["fullName"],
                            "bats": p.get("batSide", {}).get("code", ""),
                            "throws": p.get("pitchHand", {}).get("code", "")}
    return out


# ---------------------------------------------------------------- games
def parse_box(pk, date, venue_id, box):
    info = {i.get("label"): i.get("value", "") for i in box.get("info", [])}
    g = {"game_pk": pk, "date": date, "venue_id": venue_id,
         "weather": info.get("Weather", "").rstrip("."), "wind": info.get("Wind", "").rstrip("."),
         "teams": {}}
    for side in ("away", "home"):
        t = box["teams"][side]
        bats = []
        for pid in t.get("batters", []):
            p = t["players"].get(f"ID{pid}")
            if not p:
                continue
            bo = p.get("battingOrder")
            st = p.get("stats", {}).get("batting", {})
            if not bo or not st:
                continue
            bats.append([pid, int(bo), st.get("plateAppearances", 0), st.get("homeRuns", 0)])
        pits = []
        for pid in t.get("pitchers", []):
            st = t["players"][f"ID{pid}"].get("stats", {}).get("pitching", {})
            pits.append([pid, st.get("battersFaced", 0), st.get("homeRuns", 0), st.get("outs", 0)])
        g["teams"][side] = {"team_id": t["team"]["id"], "team": t["team"].get("abbreviation") or t["team"]["name"],
                            "bat": bats, "pit": pits}
    return g


def fetch_games(season):
    sched = get_json(f"{STATS}/schedule?sportId=1&season={season}&gameType=R&startDate={season}-03-01&endDate={season}-11-30")
    games = [x for d in sched["dates"] for x in d["games"]
             if x["status"]["detailedState"] in ("Final", "Completed Early", "Game Over")]
    path = os.path.join(RAW, f"games_{season}.json")
    cache = {}
    if os.path.exists(path):
        cache = {g["game_pk"]: g for g in json.load(open(path))}
    todo = [x for x in games if x["gamePk"] not in cache]
    print(f"season {season}: {len(games)} final games, {len(todo)} to fetch")

    def one(x):
        box = get_json(f"{STATS}/game/{x['gamePk']}/boxscore")
        return parse_box(x["gamePk"], x["officialDate"], x["venue"]["id"], box)

    done = 0
    with ThreadPoolExecutor(6) as ex:
        for g in ex.map(one, todo):
            cache[g["game_pk"]] = g
            done += 1
            if done % 250 == 0:
                print(f"  {done}/{len(todo)}")
                json.dump(list(cache.values()), open(path, "w"))
    out = sorted(cache.values(), key=lambda g: (g["date"], g["game_pk"]))
    json.dump(out, open(path, "w"))
    # compact copy for the repo (the model reads it when raw/ is empty)
    import gzip
    with gzip.open(os.path.join(DATA, f"games_{season}.json.gz"), "wt") as z:
        json.dump(out, z, separators=(",", ":"))
    print(f"  saved raw/games_{season}.json and data/games_{season}.json.gz ({len(out)} games)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seasons", default="2022,2023,2024,2025,2026")
    ap.add_argument("--games", default="", help="comma list of seasons to pull boxscores for")
    ap.add_argument("--skip-leaderboards", action="store_true")
    a = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)
    years = [int(x) for x in a.seasons.split(",") if x]

    if not a.skip_leaderboards:
        hit = build_hitters(years)
        write_csv(os.path.join(DATA, "hitters.csv"), hit, HIT_FIELDS)
        pit = build_pitchers(years)
        write_csv(os.path.join(DATA, "pitchers.csv"), pit, PIT_FIELDS)
        parks = []
        for y in years:
            parks += savant_parks(y)
        write_csv(os.path.join(DATA, "park_factors.csv"), parks,
                  ["year", "bat_side", "venue_id", "venue", "team", "years", "n_pa", "hr_index",
                   "hardhit_index", "runs_index"])
        write_csv(os.path.join(DATA, "venues.csv"), build_venues(max(years)),
                  ["venue_id", "venue", "city", "lat", "lon", "azimuth", "elevation_ft", "roof", "lf", "cf", "rf"])

    ids = set()
    for s in [int(x) for x in a.games.split(",") if x]:
        for g in fetch_games(s):
            for t in g["teams"].values():
                ids.update(b[0] for b in t["bat"])
                ids.update(p[0] for p in t["pit"])
    hp = os.path.join(DATA, "hands.csv")
    if os.path.exists(hp):
        for r in csv.DictReader(open(hp)):
            ids.add(int(r["player_id"]))
    for f in ("hitters.csv", "pitchers.csv"):
        p = os.path.join(DATA, f)
        if os.path.exists(p):
            ids.update(int(r["player_id"]) for r in csv.DictReader(open(p)))
    print(f"handedness for {len(ids)} players")
    hands = people_hands(ids)
    write_csv(hp, sorted(hands.values(), key=lambda r: r["player_id"]), ["player_id", "name", "bats", "throws"])


if __name__ == "__main__":
    sys.exit(main())
