#!/usr/bin/env python3
"""First basket METHOD longshots (11/17/26, Tim): how the game's first points are scored, FanDuel style
(3-pointer, layup, dunk, jump shot (2), free throw).

Per game:
  team part   = fb_method game split (team offense x opponent defense, shrunk, weighted by P(team scores first))
  player part = sum over starters of P(he scores the first points) x his split (FT share from his team's split,
                FG part from fb_method player_split: his shot mix + first-FG history)
  blend       = 0.5 team + 0.5 player, then shrunk 25% toward the league first-points rates (both seasons)
  rim -> dunk / layup with the player-weighted dunk share of rim makes (rimsplit caches, 26-27 x3),
                each player shrunk toward the league with 15 pseudo makes, scaled so the league average
                matches the league dunk share of rim FIRST points (29%).
Player + method combo: P(he scores first) x (1 - team FT share) x his rim share x his dunk share.
Fair = 1 / p; take-at = fair decimal x1.2.

Usage: python3 analysis/nba/method_longshots.py 2026-11-17 [--json out.json]
"""
import json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fb_method as FM

W_TEAM, SHRINK, K_DUNK, W_CUR = 0.5, 0.25, 15, 3
LAB = {'3': '3-pointer', 'layup': 'Layup', 'dunk': 'Dunk', 'j2': 'Jump shot (2)', 'ft': 'Free throw'}


def am(p):
    d = 1 / p
    return f'+{round((d - 1) * 100)}' if d >= 2 else f'-{round(100 / (d - 1))}'


def take(p):
    return am(p / 1.2)


def main(date, out_json=None):
    cands = json.load(open(os.path.join(HERE, 'out', 'fb_candidates.json')))
    sv = json.load(open(os.path.join(HERE, 'out', 'sheet_values.json')))['NBA']
    roster = json.load(open(os.path.join(HERE, 'data', 'rosters.json')))
    pid_of = {(v['name'], v['tm']): (k, v['pos']) for k, v in roster.items()}
    # P(away scores first) from the tip table rows "AWAY @ HOME time"
    pfirst = {}
    for r in sv:
        if r and isinstance(r[0], str) and ' @ ' in r[0] and isinstance(r[4] if len(r) > 4 else None, float) \
                and isinstance(r[3], float):
            a, rest = r[0].split(' @ '); h = rest.split()[0]
            pfirst.setdefault((a, h), r[4])
    MM = FM.Model(FM.load_all(W_CUR))
    # league first-points rates and dunk shares from the rimsplit caches
    lg, dk = Counter(), [0.0, 0.0]
    fp_d = [0.0, 0.0]
    rk = {}
    for season, w in (('2025-26', 1), ('2026-27', W_CUR)):
        c = json.load(open(os.path.join(HERE, 'data', f'rimsplit_{season}.json')))
        for g in c.values():
            if g['fp']:
                lg[g['fp'][2]] += w
                if g['fp'][1] == 'rim':
                    fp_d[0 if g['fp'][2] == 'dunk' else 1] += w
            for pid, (d, l) in g['rk'].items():
                e = rk.setdefault(pid, [0.0, 0.0]); e[0] += w * d; e[1] += w * l
                dk[0] += w * d; dk[1] += w * l
    n = sum(lg.values()); lgp = {m: lg[m] / n for m in LAB}
    lg_rim = {'rim': lgp['dunk'] + lgp['layup'], 'j2': lgp['j2'], '3': lgp['3'], 'ft': lgp['ft']}
    dunk_all = dk[0] / sum(dk); dunk_first = fp_d[0] / sum(fp_d); scale = dunk_first / dunk_all

    def dshare(pid):
        d, l = rk.get(pid, [0, 0])
        return min(0.95, scale * (d + K_DUNK * dunk_all) / (d + l + K_DUNK))

    games = []
    for (a, h), paf in pfirst.items():
        gc = [c for c in cands if c['tm'] in (a, h)]
        if not gc:
            continue
        team = MM.game_split(a, h, paf)
        tsp = {a: MM.team_split(a, h), h: MM.team_split(h, a)}
        pl = Counter(); rimw = []; tot = 0; combos = []
        for c in gc:
            pid, pos = pid_of.get((c['player'], c['tm']), (None, 'F'))
            post = MM.player_split(pid, pos)[0] if pid else MM.posfirst[(pos or 'F')[:1]]
            p = c['p_v2']; ft = tsp[c['tm']]['ft']; tot += p
            pl['ft'] += p * ft
            for m in FM.METHODS:
                pl[m] += p * (1 - ft) * post[m]
            ds = dshare(pid)
            rimw.append((p * (1 - ft) * post['rim'], ds))
            combos.append((c['player'], c['tm'], p, p * (1 - ft) * post['rim'] * ds,
                           p * (1 - ft) * post['rim'] * (1 - ds), p * (1 - ft) * post['3'], p * (1 - ft) * post['j2']))
        pl = {m: v / tot for m, v in pl.items()}
        bl = {m: (1 - SHRINK) * (W_TEAM * team[m] + (1 - W_TEAM) * pl[m]) + SHRINK * lg_rim[m] for m in lg_rim}
        s = sum(bl.values()); bl = {m: v / s for m, v in bl.items()}
        dg = sum(w * d for w, d in rimw) / sum(w for w, _ in rimw)
        dg = (1 - SHRINK) * dg + SHRINK * dunk_first
        res = {'3': bl['3'], 'layup': bl['rim'] * (1 - dg), 'dunk': bl['rim'] * dg, 'j2': bl['j2'], 'ft': bl['ft']}
        tipfav = a if paf > 0.5 else h
        games.append({'game': f'{a} @ {h}', 'p_away_first': paf, 'methods': res, 'team': team, 'player': pl,
                      'dunk_share': dg,
                      'combos': sorted(combos, key=lambda x: -x[3])[:4]})
    print(f'League first points (25-26 + 26-27 x{W_CUR}): ' + ', '.join(f'{LAB[m]} {lgp[m]:.1%}' for m in LAB)
          + f'; dunk share of rim first points {dunk_first:.0%}')
    for g in games:
        print(f"\n{g['game']}  (P away first {g['p_away_first']:.0%}; dunk share of rim {g['dunk_share']:.0%})")
        for m in LAB:
            p = g['methods'][m]
            print(f'  {LAB[m]:<14} {p:5.1%}  fair {am(p):>6}  take {take(p):>6}')
        for nm, tm, p, pd, pla, p3, pj in g['combos'][:2]:
            print(f'  combo {nm} ({tm}) first basket dunk {pd:.1%} fair {am(pd)} take {take(pd)}; '
                  f'layup {pla:.1%} fair {am(pla)}')
    if out_json:
        json.dump({'date': date, 'games': games}, open(out_json, 'w'), indent=1)


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[a.index('--json') + 1] if '--json' in a else None)
