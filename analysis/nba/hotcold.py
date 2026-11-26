#!/usr/bin/env python3
"""NBA first basket HOT/COLD METER (Tim approved 11/22/26). TRACKING ONLY.

It never changes a pick, rank, fair price or the play list (same rule as StarTool: our model only).
It answers one question: is a run of hits or misses more than luck?

1. Model-level meter: hits vs expected (sum of our model chances) for
     top 3 overall, rank 1 / 2 / 3     (out/top3_log.csv, written by analysis/reports/top3_coverage.py)
     play list (bets)                 (top 3 in the play-list games of out/play_list_<date>.md; PLAY_GAMES below)
     team first basket top 2          (team_share in the committed fb_candidates.json, source_scorecard.COMMITS)
     method longshots                 (out/method_longshots_<date>.json picks, graded on data/fdmethod_<season>.json)
   Windows: last 7 days and season (since 11/4).
2. Player-level meter: every starter, 2026-27 regular season. First points (FT count) vs the sum of his chain-model
   chance in every game he started. The published fb_candidates only hold OUR PROJECTED fives, so the per-starter
   chances are rebuilt walk-forward with backtest_chain.run (no lookahead, actual starters and jumpers, games whose
   first scorer came off the bench kept). Also team first-shot attempts vs the model's first-shot share (role signal).
   Tag: two-sided Poisson-binomial p-value. "real" = p < 0.05 and 20+ starts; "watch" = p < 0.10, or p < 0.05 with
   under 20 starts; else "luck". With about 300 starters, about 15 will show p < 0.05 by chance alone.
3. Chart: out/charts/hotcold_<date>.png. Data: out/hotcold_<date>.json, out/hotcold_players.csv.

Run after each night's grade (after top3_coverage.py):
    python3 analysis/nba/hotcold.py 2026-11-21     # through that date (default: last date in COMMITS)
"""
import csv, datetime as dt, json, math, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(R, 'analysis', 'reports'))
import source_scorecard as sc  # noqa: E402

SEASON_FROM = '2026-11-04'     # model-level season window (first graded date)
PLAYER_FROM = '2026-10-20'     # player-level window (2026-27 regular season)
MIN_LIST = 5                   # starts needed for the chart's hottest / coldest lists
OUT = os.path.join(HERE, 'out')
norm = sc.norm

# Play-list games by date (from out/play_list_<date>.md, final rerun; exception games included while they were on
# the list). Later dates are parsed from the "Play list (tip 70%+): ..." line; games "off the play list" are dropped.
PLAY_GAMES = {
    '2026-11-14': ['DEN@NO', 'DAL@CLE', 'DET@MIA', 'CHI@MIN'],
    '2026-11-15': ['LAL@PHX', 'CHA@LAC', 'SA@UTAH', 'ATL@MIL'],
    '2026-11-16': ['CHI@CLE', 'HOU@MIA', 'PHX@DEN'],
    '2026-11-17': ['DET@SA', 'UTAH@LAC'],
    '2026-11-18': ['PHI@ORL', 'CHI@BKN', 'DET@NO'],
    '2026-11-19': ['GS@MEM', 'LAC@SA', 'NY@MIN'],
    '2026-11-20': ['ORL@BKN', 'IND@CLE', 'NO@OKC', 'SAC@LAL'],
    '2026-11-21': ['LAC@DAL', 'NO@SA'],
    '2026-11-22': ['OKC@MIA', 'DEN@CHI', 'BOS@GS'],   # OKC@MIA added at the 5:50 PM rerun (MIA 71%)
    '2026-11-25': ['CHI@CHA', 'CLE@NY', 'SAC@GS', 'SA@POR'],   # CHI@CHA added at the 6:35 PM check (CHI 72%)
}


def play_games(d):
    if d in PLAY_GAMES:
        return PLAY_GAMES[d]
    p = os.path.join(OUT, f'play_list_{d}.md')
    if not os.path.exists(p):
        return []
    s = open(p).read()
    m = re.search(r'Play list \(tip 70%\+\):(.*?)(Skipped|\n)', s)
    if not m:
        return []
    gs = [f'{a}@{h}' for a, h in re.findall(r'\b([A-Z]{2,4})@([A-Z]{2,4})\b', m.group(1))]
    off = {f'{a}@{h}' for a, h in re.findall(r'\b([A-Z]{2,4})@([A-Z]{2,4})\b[^.\n]*off the play list', s)}
    return [g for g in gs if g not in off]


# ---------- stats ----------
def pb_pmf(ps):
    f = [1.0]
    for p in ps:
        g = [0.0] * (len(f) + 1)
        for k, v in enumerate(f):
            g[k] += v * (1 - p)
            g[k + 1] += v * p
        f = g
    return f


def pval(ps, hits):
    """Two-sided p-value for `hits` successes, independent chances ps (Poisson-binomial, doubled smaller tail)."""
    if not ps:
        return 1.0
    f = pb_pmf(ps)
    lo = sum(f[:hits + 1])
    hi = sum(f[hits:])
    return min(1.0, 2 * min(lo, hi))


def tag(p, n):
    if p < 0.05 and n >= 20:
        return 'real'
    if p < 0.10:
        return 'watch'
    return 'luck'


def summarize(items):
    """items: [(p, hit)] -> dict hits, exp, n, z, pval."""
    ps = [p for p, _ in items]
    h = sum(1 for _, x in items if x)
    e = sum(ps)
    var = sum(p * (1 - p) for p in ps)
    z = (h - e) / math.sqrt(var) if var > 0 else 0.0
    return dict(n=len(items), hits=h, exp=round(e, 2), z=round(z, 2), pval=round(pval(ps, h), 3))


# ---------- results ----------
def results():
    out = {}
    for s in ('2026-27',):
        gj = json.load(open(os.path.join(HERE, 'data', f'games_{s}.json')))
        op = json.load(open(os.path.join(HERE, 'data', f'opening_{s}.json')))
        fdp = os.path.join(HERE, 'data', f'fdmethod_{s}.json')
        fdm = json.load(open(fdp)) if os.path.exists(fdp) else {}
        for g in gj.values():
            if not isinstance(g, dict) or not g.get('fp'):
                continue
            nm = g['nm']
            played = {norm(nm[p[0]]) for p in g['pl'] if p[0] in nm}
            tp = {t: norm(nm.get(pid, '?')) for t, pid in op.get(g['id'], {}).get('tp', {}).items()}
            fm = fdm.get(g['id'], {}).get('fp')
            out[(g['date'], f"{g['away']}@{g['home']}")] = dict(
                fp=norm(nm[g['fp'][0]]), played=played, tp=tp,
                method=(norm(nm.get(fm[2], '?')), fm[1]) if fm else None)
    return out


RES = results()


def model_level(D):
    cats = defaultdict(list)   # name -> [(date, p, hit)]
    t3 = list(csv.DictReader(open(os.path.join(OUT, 'top3_log.csv'))))
    for r in t3:
        if r['result'] == 'Void' or r['date'] > D:
            continue
        x = (r['date'], float(r['p']), r['result'] == 'W')
        cats['Top 3 overall'].append(x)
        cats[f"Rank {r['rank']}"].append(x)
        if r['game'].replace(' ', '') in play_games(r['date']):
            cats['Play list (bets)'].append(x)
    # team first basket top 2 (team_share; before 11/8 the share of the team's game chance)
    for d, c in sorted(sc.COMMITS.items()):
        if d > D:
            continue
        rows = [r for r in json.loads(sc.show(c, 'analysis/nba/out/fb_candidates.json')) if r.get('inj') != 'Out']
        by = defaultdict(list)
        for r in rows:
            by[(r['tm'], r['opp'])].append(r)
        for (tm, opp), rs in by.items():
            z = sum(r['p_v2'] for r in rs)
            g = RES.get((d, f'{tm}@{opp}')) or RES.get((d, f'{opp}@{tm}'))
            if not g or tm not in g['tp']:
                continue
            for r in sorted(rs, key=lambda r: -r.get('team_share', r['p_v2'] / z))[:2]:
                n = norm(r['player'])
                if n not in g['played']:
                    continue
                cats['Team FB top 2'].append((d, r.get('team_share', r['p_v2'] / z), g['tp'][tm] == n))
    # method longshots (player + method)
    for f in sorted(os.listdir(OUT)):
        m = re.match(r'method_longshots_(\d{4}-\d\d-\d\d)\.json$', f)
        if not m or m.group(1) > D:
            continue
        d = m.group(1)
        for k in json.load(open(os.path.join(OUT, f))).get('picks', []):
            g = RES.get((d, k['game'].replace(' ', '')))
            if not g or not g['method'] or norm(k['player']) not in g['played']:
                continue
            cats['Method longshots'].append((d, k['p'], g['method'] == (norm(k['player']), k['key'])))
    d7 = (dt.date.fromisoformat(D) - dt.timedelta(days=6)).isoformat()
    order = ['Top 3 overall', 'Rank 1', 'Rank 2', 'Rank 3', 'Play list (bets)', 'Team FB top 2', 'Method longshots']
    out = []
    for k in order:
        xs = cats.get(k, [])
        out.append(dict(cat=k, d7=summarize([(p, h) for d, p, h in xs if d >= d7]),
                        season=summarize([(p, h) for d, p, h in xs if d >= SEASON_FROM])))
    return out, d7


# ---------- player level ----------
def player_level(D):
    import backtest_chain as bc
    import chain_model as cm
    bc.KEEP_BENCH = True
    orig = cm.game_probs
    LOG = []

    def wrap(teams, pt, c=cm.CH):
        LOG.append({x['pid']: q for T in teams for x, q in zip(T.P, T.q1)})
        return orig(teams, pt, c)

    cm.game_probs = wrap
    try:
        recs = bc.run({'chain': {}})
    finally:
        cm.game_probs = orig
        bc.KEEP_BENCH = False
    assert len(LOG) == len(recs)
    P = defaultdict(lambda: dict(items=[], sh=0, shx=0.0, name='', tm=''))
    games = bench = 0
    for r, q1 in zip(recs, LOG):
        d = r['d']
        if d < PLAYER_FROM or d > D:
            continue
        g = r['g']
        games += 1
        bench += r['win'] not in r['tmof']
        for pid, p in r['probs']['chain'].items():
            tm = r['tmof'][pid]
            x = P[pid]
            x['items'].append((p, r['win'] == pid))
            x['sh'] += g['ts'].get(tm) == pid
            x['shx'] += q1[pid]
            x['name'], x['tm'] = g['nm'].get(pid, pid), tm
    rows = []
    for pid, x in P.items():
        s = summarize(x['items'])
        rows.append(dict(player=x['name'], tm=x['tm'], starts=s['n'], hits=s['hits'], exp=s['exp'], z=s['z'],
                         pval=s['pval'], tag=tag(s['pval'], s['n']), fs=x['sh'], fs_exp=round(x['shx'], 2)))
    rows.sort(key=lambda r: -r['z'])
    return rows, games, bench


# ---------- chart ----------
def chart(D, ML, d7, PL, games, bench, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['text.parse_math'] = False
    BG = '#0f1420'; CARD = '#1a2233'; TXT = '#e8ecf3'; MUTED = '#9aa4b5'; GOLD = '#f5c542'
    BLUE = '#5aa9ff'; GREEN = '#4cd38a'; RED = '#ff6b6b'
    H = 100
    fig = plt.figure(figsize=(7.2, 12.0), dpi=200); fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(4.5, H); ax.axis('off')
    day = dt.date.fromisoformat(D).strftime('%a %m/%d').upper()
    ax.text(4, 98, f'FIRST BASKET HOT / COLD METER  •  THROUGH {day}', color=TXT, fontsize=14, weight='bold', va='center')
    ax.text(4, 96.4, 'Tracking only. Never changes a pick, rank, fair or the play list (our model only).',
            color=GOLD, fontsize=7.6, va='center')
    ax.text(4, 95.0, 'Hits vs expected (sum of our model chances). Bar = hits / expected, center line = on model.',
            color=MUTED, fontsize=7.4, va='center')
    # model-level
    y = 92.4
    ax.text(4, y, 'MODEL', color=BLUE, fontsize=9.5, weight='bold', va='center')
    lab7 = f"LAST 7 DAYS ({dt.date.fromisoformat(d7).strftime('%m/%d')}-{dt.date.fromisoformat(D).strftime('%m/%d')})"
    ax.text(33, y, lab7, color=MUTED, fontsize=7.4, weight='bold', va='center')
    ax.text(67, y, 'SEASON (SINCE 11/04)', color=MUTED, fontsize=7.4, weight='bold', va='center')
    y -= 2.4
    for i, m in enumerate(ML):
        ax.add_patch(plt.Rectangle((3, y - 2.0), 94, 4.0, fc=CARD if i % 2 == 0 else BG, ec='none'))
        ax.text(4.5, y, m['cat'], color=TXT, fontsize=8.6, weight='bold', va='center')
        for x0, s in ((33, m['d7']), (67, m['season'])):
            if not s['n']:
                ax.text(x0, y, 'no picks', color=MUTED, fontsize=7.4, va='center')
                continue
            ratio = s['hits'] / s['exp'] if s['exp'] else 0
            col = GREEN if s['hits'] > s['exp'] else (RED if s['hits'] < s['exp'] else MUTED)
            w = 26
            ax.add_patch(plt.Rectangle((x0, y - 1.55), w, 0.9, fc='#2c3850', ec='none'))
            ax.add_patch(plt.Rectangle((x0, y - 1.55), w * min(ratio, 2) / 2, 0.9, fc=col, ec='none'))
            ax.plot([x0 + w / 2] * 2, [y - 1.8, y - 0.4], color=TXT, lw=0.8)
            t = 'luck' if s['pval'] >= 0.10 else ('watch' if s['pval'] >= 0.05 else 'real')
            ax.text(x0, y + 0.55, f"{s['hits']} vs {s['exp']:.1f}  ({s['n']})", color=col if col != MUTED else TXT,
                    fontsize=8.2, weight='bold', va='center')
            ax.text(x0 + w, y + 0.55, t, color=GOLD if t != 'luck' else MUTED, fontsize=7, va='center', ha='right')
        y -= 4.2
    ax.text(4, y + 0.6, '(n) = picks graded. Tag from a two-sided p-value: luck p 0.10+, watch under 0.10, real under 0.05.',
            color=MUTED, fontsize=6.8, va='center')
    # player-level
    y -= 2.6
    ax.text(4, y, 'PLAYERS (every starter, 2026-27 season, model chance with the actual fives)', color=BLUE,
            fontsize=9.5, weight='bold', va='center')
    y -= 2.0
    cols = [(4.5, 'Player', 'left'), (52, 'GS', 'right'), (62, 'Hits', 'right'), (72, 'Exp', 'right'),
            (85, '1st shot', 'right'), (96, 'Tag', 'right')]

    def table(title, rows, color, y):
        ax.text(4, y, title, color=color, fontsize=9, weight='bold', va='center')
        y -= 1.9
        for x, h, ha in cols:
            ax.text(x, y, h, color=MUTED, fontsize=7.2, weight='bold', va='center', ha=ha)
        y -= 1.8
        for i, r in enumerate(rows):
            if i % 2 == 0:
                ax.add_patch(plt.Rectangle((3, y - 0.85), 94, 1.7, fc=CARD, ec='none'))
            tg = r['tag']
            vals = [f"{r['player']} ({r['tm']})", r['starts'], r['hits'], f"{r['exp']:.1f}", f"{r['fs']} / {r['fs_exp']:.1f}", tg]
            for (x, _, ha), v in zip(cols, vals):
                c = TXT
                if v == tg:
                    c = GOLD if tg == 'real' else (BLUE if tg == 'watch' else MUTED)
                ax.text(x, y, str(v), color=c, fontsize=7.8, va='center', ha=ha)
            y -= 1.75
        return y - 1.2

    Q = [r for r in PL if r['starts'] >= MIN_LIST]
    y = table(f'HOTTEST 10 (most above expected, {MIN_LIST}+ starts)', Q[:10], GREEN, y)
    y = table(f'COLDEST 10 (most below expected, {MIN_LIST}+ starts)', Q[::-1][:10], RED, y)
    ax.text(4, y, f'1st shot = team first-shot attempts / model expected (role signal). {games} games; first scorer came off',
            color=MUTED, fontsize=6.8, va='center')
    ax.text(4, y - 1.4, f'the bench in {bench}. With {len(PL)} starters, about {round(len(PL) * 0.05)} show p under 0.05 by chance; "real" also needs 20+ starts.',
            color=MUTED, fontsize=6.8, va='center')
    ax.text(4, y - 2.8, 'First basket is mostly noise. Points, threes and SOG are the steadier plays.',
            color=MUTED, fontsize=6.8, va='center')
    fig.savefig(path, facecolor=BG)
    plt.close(fig)


def main():
    D = sys.argv[1] if len(sys.argv) > 1 else max(sc.COMMITS)
    ML, d7 = model_level(D)
    PL, games, bench = player_level(D)
    os.makedirs(os.path.join(OUT, 'charts'), exist_ok=True)
    path = os.path.join(OUT, 'charts', f'hotcold_{D}.png')
    chart(D, ML, d7, PL, games, bench, path)
    with open(os.path.join(OUT, 'hotcold_players.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(PL[0]))
        w.writeheader(); w.writerows(PL)
    json.dump(dict(through=D, d7_from=d7, model=ML, games=games, bench_first=bench,
                   hot=[r for r in PL if r['starts'] >= MIN_LIST][:10],
                   cold=[r for r in PL if r['starts'] >= MIN_LIST][::-1][:10], flagged=[r for r in PL if r['tag'] != 'luck']),
              open(os.path.join(OUT, f'hotcold_{D}.json'), 'w'), indent=1)
    print(f'HOT/COLD METER through {D} (tracking only)')
    for m in ML:
        a, b = m['d7'], m['season']
        print(f"  {m['cat']:<18} 7d {a['hits']} vs {a['exp']:.1f} ({a['n']}, p {a['pval']:.2f})   "
              f"season {b['hits']} vs {b['exp']:.1f} ({b['n']}, p {b['pval']:.2f})")
    tot_h = sum(r['hits'] for r in PL); tot_e = sum(r['exp'] for r in PL)
    print(f'  Players: {len(PL)} starters, {games} games, bench first scorer {bench}; starters total {tot_h} vs {tot_e:.1f}')
    for r in PL:
        if r['tag'] != 'luck':
            print(f"  {r['tag']:<5} {r['player']} ({r['tm']}) GS {r['starts']} hits {r['hits']} exp {r['exp']} "
                  f"p {r['pval']} 1st shot {r['fs']}/{r['fs_exp']}")
    print('Chart:', path)


if __name__ == '__main__':
    main()
