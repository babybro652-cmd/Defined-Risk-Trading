#!/usr/bin/env python3
"""First basket METHOD longshots, FanDuel format: PLAYER + METHOD only (Tim's correction 11/18/26).

FanDuel's "Method of First Basket" market lists one player plus one method per option, e.g.
"Bam Adebayo - Dunk +3500", "Bam Adebayo - Free Throw +3000", "Bam Adebayo - Layup +2700",
"Bam Adebayo - Other +1200", "Bam Adebayo - Three Point Field Goal +2000". There is no game-level
"DET@NO Free throw" bet, so this script never outputs one.

Methods (fd_method.py): Dunk, Layup, Other, Three Point Field Goal, Free Throw.
  Other = every made 2 that is not a dunk or layup: jump shots, pullups, step-backs, fadeaways,
  floaters, hooks, bank shots and tip shots (ESPN "Tip Shot"). Layup includes finger rolls and
  putback / alley-oop layups; Dunk includes alley-oop and putback dunks.

Per starter:
  P(he scores the game's first points)    = p_v2 from out/fb_candidates.json (chain model, FT counts)
  his event mix  = made dunks, layups, other 2s, 3s and FT trips (2026-27 games x3, 2025-26 x1),
                   shrunk toward his position's mix with K_MIX pseudo events
  first-points calibration: each method x (league first-points rate / league event rate), renormalized
                   (FT trips and dunks are rarer on the opening trips than over a whole game)
  his own first-points methods (as the game's first scorer) shrunk in with K_FIRST pseudo games
  P(player + method) = P(first points) x P(method | he scores first)
Fair = 1 / p; take-at = fair decimal x1.2.

Picks: the 4 most likely player + method combos in the play-list games (max 2 per game, 1 per player),
staked $0.50 / $0.20 / $0.20 / $0.10.

Usage: python3 analysis/nba/method_longshots.py 2026-11-18 --games "PHI@ORL,CHI@BKN,DET@NO" [--json out.json]
       python3 analysis/nba/method_longshots.py --check     # out-of-sample method log loss
"""
import json, math, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fd_method import FD, FD_LAB, load as fd_load

K_MIX, K_FIRST, W_CUR = 20, 40, 3
STAKES = (0.50, 0.20, 0.20, 0.10)


def am(p):
    d = 1 / p
    return f'+{round((d - 1) * 100):,}' if d >= 2 else f'-{round(100 / (d - 1))}'


def take(p):
    return am(p / 1.2)


def norm(d):
    s = sum(d.values())
    return {k: v / s for k, v in d.items()}


class MethodModel:
    def __init__(self, seasons, pos_of):
        self.mix, self.first = {}, {}
        lg_ev, lg_fp = Counter(), Counter()
        posmix = {p: Counter() for p in 'GFC'}
        for c, w in seasons:
            for g in c.values():
                if g['fp']:
                    lg_fp[g['fp'][1]] += w
                    self.first.setdefault(g['fp'][2], Counter())[g['fp'][1]] += w
                for pid, mk in g['mk'].items():
                    e = self.mix.setdefault(pid, Counter())
                    ps = (pos_of.get(pid) or 'F')[:1]; ps = ps if ps in posmix else 'F'
                    for m, v in zip(FD, mk):
                        e[m] += w * v; lg_ev[m] += w * v; posmix[ps][m] += w * v
        self.lg_fp = norm(lg_fp); self.lg_ev = norm(lg_ev)
        self.posmix = {p: norm(v) for p, v in posmix.items()}
        self.scale = {m: self.lg_fp[m] / self.lg_ev[m] for m in FD}

    def split(self, pid, pos):
        ps = (pos or 'F')[:1]; ps = ps if ps in self.posmix else 'F'
        mix = self.mix.get(pid, Counter()); n = sum(mix.values())
        sm = {m: (mix[m] + K_MIX * self.posmix[ps][m]) / (n + K_MIX) for m in FD}
        prior = norm({m: sm[m] * self.scale[m] for m in FD})
        f = self.first.get(pid, Counter()); nf = sum(f.values())
        return {m: (f[m] + K_FIRST * prior[m]) / (nf + K_FIRST) for m in FD}


def pos_map():
    roster = json.load(open(os.path.join(HERE, 'data', 'rosters.json')))
    return roster, {k: v['pos'] for k, v in roster.items()}


def check():
    """Fit on 2025-26, score the method of each 2026-27 game's first points given the scorer."""
    _, pos_of = pos_map()
    M = MethodModel([(fd_load('2025-26', False), 1)], pos_of)
    ll = Counter(); n = 0
    for g in fd_load('2026-27', False).values():
        if not g['fp']:
            continue
        _, m, pid = g['fp']; ps = (pos_of.get(pid) or 'F')[:1]; ps = ps if ps in M.posmix else 'F'
        n += 1
        for key, d in (('league', M.lg_fp), ('position', norm({k: M.posmix[ps][k] * M.scale[k] for k in FD})),
                       ('player model', M.split(pid, pos_of.get(pid)))):
            ll[key] -= math.log(d[m])
    print(f'{n} games (2026-27 first points, fit on 2025-26). Method log loss given the scorer:')
    for k, v in ll.items():
        print(f'  {k:<13} {v / n:.3f}')


def main(date, games, out_json=None):
    cands = json.load(open(os.path.join(HERE, 'out', 'fb_candidates.json')))
    roster, pos_of = pos_map()
    pid_of = {(v['name'], v['tm']): k for k, v in roster.items()}
    M = MethodModel([(fd_load('2025-26', False), 1), (fd_load('2026-27', False), W_CUR)], pos_of)
    print('League first points: ' + ', '.join(f'{FD_LAB[m]} {M.lg_fp[m]:.1%}' for m in FD))
    out = []
    for gm in games:
        a, h = gm.split('@')
        rows = []
        for c in [c for c in cands if c['tm'] in (a, h)]:
            pid = pid_of.get((c['player'], c['tm']))
            sp = M.split(pid, pos_of.get(pid))
            rows.append({'player': c['player'], 'tm': c['tm'], 'p_first': c['p_v2'],
                         'split': sp, 'p': {m: c['p_v2'] * sp[m] for m in FD}})
        rows.sort(key=lambda r: -r['p_first'])
        out.append({'game': f'{a} @ {h}', 'players': rows})
        print(f'\n{a} @ {h}')
        for r in rows:
            print(f"  {r['player']:<24} {r['tm']:<4} FB {r['p_first']:5.1%}  " +
                  '  '.join(f"{FD_LAB[m][:5]} {r['p'][m]:4.1%} {am(r['p'][m]):>7}" for m in FD))
    combos = sorted(((r['p'][m], g['game'], r['player'], m) for g in out for r in g['players'] for m in FD),
                    reverse=True)
    picks, per_game, used = [], Counter(), set()
    for p, g, pl, m in combos:
        if per_game[g] < 2 and pl not in used:
            picks.append({'game': g, 'player': pl, 'method': FD_LAB[m], 'key': m, 'p': p,
                          'fair': am(p), 'take': take(p), 'stake': STAKES[len(picks)]})
            per_game[g] += 1; used.add(pl)
        if len(picks) == len(STAKES):
            break
    print('\nPicks (player + method, FanDuel format):')
    for k in picks:
        print(f"  {k['player']} - {k['method']} ({k['game']}), ${k['stake']:.2f}: est {k['p']:.1%}, "
              f"fair {k['fair']}, take {k['take']}")
    if out_json:
        json.dump({'date': date, 'format': 'player + method (FanDuel Method of First Basket)',
                   'league_first_points': M.lg_fp, 'games': out, 'picks': picks}, open(out_json, 'w'), indent=1)


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--check' in a:
        check()
    else:
        g = a[a.index('--games') + 1].split(',') if '--games' in a else []
        main(a[0], g, a[a.index('--json') + 1] if '--json' in a else None)
