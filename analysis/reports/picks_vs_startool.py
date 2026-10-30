#!/usr/bin/env python3
"""Season-to-date picks review (10/30/26): our first-basket model vs StarTool, calibration, jumper fix and blend
backtests, Bets tab categories, Tim's played P/L.

  python3 analysis/reports/picks_vs_startool.py <bets.csv> <startool.txt>

bets.csv: Bets tab export (first column = sheet row, then A..K). startool.txt: one line per NBA card,
date|game|tipA|tipH|away list|home list, each list "Name pct,Name pct" (top 5 per team as printed).
Writes analysis/reports/out/summary.json and the chart PNG.
"""
import csv, json, math, os, re, sys, unicodedata, random
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'nba'))
import backtest_fb as bt  # noqa: E402
from build_nba_tab import V2  # noqa: E402

OUT = {}


def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|iii|ii)\b', '', s)
    return re.sub(r'[^a-z]', '', s)


def dec(o):
    o = float(o)
    return 1 + (o / 100 if o > 0 else 100 / -o)


def fair_from_p(p):
    return -100 * p / (1 - p) if p >= .5 else 100 * (1 - p) / p


# ---------------------------------------------------------------- walk-forward model records (26-27 + 25-26 Dec on)
bt.run({'cur': dict(V2, ramp=True)}, team=True)
REC = [r for r in bt.REC if r['k'] == 'cur']
AF = 0.64


def jumper_adjust(r, bw=1.0, bl=1.0):
    """Pregame price with a jumper share boost bw when his team wins the tip and bl when it loses."""
    g = r['g']
    jm = {tm: pid for pid, tm in g['tip']['j']}
    out = {}
    for tm in r['st']:
        pts = r['pt'][tm]
        ptip = min(1, max(0, (pts - (1 - AF)) / (2 * AF - 1)))
        pids = [p[0] for p in r['st'][tm]]
        sh = {p: r['probs'][p] / pts for p in pids}
        S = sum(sh.values())
        j = jm.get(tm)
        res = defaultdict(float)
        for scen_p, b in ((ptip * AF, bw), ((1 - ptip) * (1 - AF), bl)):
            if j in sh:
                sj = min(sh[j] * b, S * .9)
                k = (S - sj) / (S - sh[j])
                s2 = {p: (sj if p == j else v * k) for p, v in sh.items()}
            else:
                s2 = sh
            for p, v in s2.items():
                res[p] += scen_p * v
        out.update(res)
    return out


def ll_of(recs, fn):
    ll = 0
    for r in recs:
        pr = fn(r)
        w = r['g']['fb'][0]
        ll -= math.log(max(pr[w] / sum(pr.values()), 1e-6))
    return ll / len(recs)


s25 = [r for r in REC if r['d'] < '2026-07-01']
s26 = [r for r in REC if r['d'] >= '2026-07-01']
grid = {}
for bw in (1.0, 1.1, 1.2, 1.3, 1.4):
    for bl in (1.0, 0.95, 0.9):
        grid[f'{bw}/{bl}'] = (ll_of(s25, lambda r: jumper_adjust(r, bw, bl)), ll_of(s26, lambda r: jumper_adjust(r, bw, bl)))
OUT['jumper_grid'] = {k: [round(a, 4), round(b, 4)] for k, (a, b) in grid.items()}
OUT['n_games'] = {'25-26': len(s25), '26-27': len(s26)}


def summarize(recs, fn, label):
    bins = [(0, .08), (.08, .11), (.11, .14), (.14, .17), (.17, 1)]
    cal = {f'{a:.0%}-{b:.0%}': [0, 0.0, 0] for a, b in bins}
    top_hit = rk_sum = 0
    jumper = {'n': 0, 'pred': 0, 'act': 0}
    for r in recs:
        pr = fn(r)
        w = r['g']['fb'][0]
        order = sorted(pr, key=pr.get, reverse=True)
        top_hit += order[0] == w
        rk_sum += order.index(w) + 1
        jset = {pid for pid, tm in r['g']['tip']['j']}
        for p, v in pr.items():
            for a, b in bins:
                if a <= v < b:
                    c = cal[f'{a:.0%}-{b:.0%}']; c[0] += 1; c[1] += v; c[2] += p == w
            if p in jset:
                jumper['n'] += 1; jumper['pred'] += v; jumper['act'] += p == w
    n = len(recs)
    return {'label': label, 'games': n, 'top_hit': top_hit, 'top_pred': round(sum(max(fn(r).values()) for r in recs), 2),
            'mean_rank': round(rk_sum / n, 2),
            'calibration': {k: {'n': c[0], 'pred': round(c[1] / c[0], 3) if c[0] else None, 'hits': c[2],
                                'hit_rate': round(c[2] / c[0], 3) if c[0] else None} for k, c in cal.items()},
            'jumper': {'n': jumper['n'], 'pred': round(jumper['pred'], 1), 'act': jumper['act']}}


OUT['model_26'] = summarize(s26, lambda r: r['probs'], 'current model, 26-27')
OUT['model_25'] = summarize(s25, lambda r: r['probs'], 'current model, 25-26 Dec-Apr')
OUT['model_26_j12'] = summarize(s26, lambda r: jumper_adjust(r, 1.2, 0.95), 'jumper x1.2/x0.95, 26-27')

# ---------------------------------------------------------------- tip and position facts, 26-27 regular season
games = json.load(open(os.path.join(ROOT, 'nba', 'data', 'games_2026-27.json')))
G26 = [g for g in games.values() if g['type'] == 2 and g['fb'] and g['tip']]
tipfirst = sum(g['tip']['w'] == g['fb'][1] for g in G26)
pos = Counter(); jump_fb = 0; fb_on_first_shot = 0
for g in G26:
    w = g['fb'][0]
    pp = {p[0]: p[6] for p in g['pl']}
    pos[pp.get(w, '?')] += 1
    jump_fb += w in {pid for pid, tm in g['tip']['j']}
    fb_on_first_shot += g['ts'].get(g['fb'][1]) == w and g.get('tsm', {}).get(g['fb'][1])
OUT['tip'] = {'games': len(G26), 'tip_winner_scored_first': tipfirst, 'fb_by_espn_pos': dict(pos),
              'fb_by_jumper': jump_fb}

# ---------------------------------------------------------------- StarTool cards
ST = []
for line in open(sys.argv[2]):
    d, gm, ta, th, a, h = line.rstrip('\n').split('|')
    lst = []
    for side in (a, h):
        for it in side.split(','):
            nm, pc = it.rsplit(' ', 1)
            lst.append((nm, float(pc) / 100))
    ST.append({'date': d, 'game': gm, 'list': lst})
FE = {(r['date'], r['game']): r for r in csv.DictReader(open(os.path.join(ROOT, 'first_events', 'log.csv'))) if r['sport'] == 'NBA'}
recidx = {}
for r in s26:
    recidx[(r['d'], f"{r['g']['away']} @ {r['g']['home']}")] = r

STARS = {}   # star/bomb per game from the out/startool/<date>.md notes (S then B per team)
SB = """2026-10-22|CLE @ PHI|Donovan Mitchell,James Harden|Jaylen Brown,Joel Embiid
2026-10-22|DEN @ OKC|Nikola Jokic,Jamal Murray|Shai Gilgeous-Alexander,Jalen Williams"""
st_rows = []
for c in ST:
    fe = FE.get((c['date'], c['game']))
    if not fe:
        continue
    scorer = re.sub(r' \([A-Z]+\)$', '', fe['first_score'])
    lst = sorted(c['list'], key=lambda x: -x[1])
    names = [norm(n) for n, _ in lst]
    st_rank = names.index(norm(scorer)) + 1 if norm(scorer) in names else 11
    st_p = dict((norm(n), p) for n, p in lst)
    row = {'date': c['date'], 'game': c['game'], 'scorer': scorer, 'st_rank': st_rank,
           'st_top': lst[0][0], 'st_top_p': lst[0][1], 'st_top_hit': norm(lst[0][0]) == norm(scorer),
           'st_p_scorer': st_p.get(norm(scorer))}
    r = recidx.get((c['date'], c['game']))
    if r:
        nm = r['g']['nm']
        pr = r['probs']
        order = sorted(pr, key=pr.get, reverse=True)
        w = r['g']['fb'][0]
        row.update(our_rank=order.index(w) + 1, our_top=nm[order[0]], our_top_p=round(pr[order[0]], 3),
                   our_top_hit=order[0] == w, our_p_scorer=round(pr[w], 3))
        # distributions over the 10 actual starters, both renormalized; unlisted starters get a floor
        starters = [p[0] for tm in r['st'] for p in r['st'][tm]]
        ours = {p: pr[p] for p in starters}
        s = sum(ours.values()); ours = {p: v / s for p, v in ours.items()}
        row['_ours'] = ours; row['_w'] = w
        row['_st_raw'] = {p: st_p.get(norm(nm.get(p, ''))) for p in starters}
        row['st_listed_starters'] = sum(v is not None for v in row['_st_raw'].values())
    st_rows.append(row)


def st_dist(row, floor):
    raw = {p: (v if v is not None else floor) for p, v in row['_st_raw'].items()}
    s = sum(raw.values())
    return {p: v / s for p, v in raw.items()}


both = [x for x in st_rows if '_ours' in x]
blend = {}
for floor in (0.02, 0.03, 0.04):
    for w in [i / 10 for i in range(11)]:
        ll = 0
        for x in both:
            sd = st_dist(x, floor)
            p = w * x['_ours'][x['_w']] + (1 - w) * sd[x['_w']]
            ll -= math.log(p)
        blend[f'floor{floor}_w{w}'] = round(ll / len(both), 4)
OUT['blend'] = blend
# bootstrap: ours (w=1) vs StarTool (w=0) vs 50/50, floor 0.03
random.seed(7)


def llg(x, w, floor=0.03):
    return -math.log(w * x['_ours'][x['_w']] + (1 - w) * st_dist(x, floor)[x['_w']])


diffs = []
for _ in range(4000):
    smp = [random.choice(both) for _ in both]
    diffs.append(sum(llg(x, 0) - llg(x, 1) for x in smp) / len(smp))
diffs.sort()
OUT['boot_st_minus_ours'] = [round(diffs[100], 4), round(diffs[2000], 4), round(diffs[3900], 4)]
# per-game: who ranked the actual scorer higher
cmp = Counter()
for x in both:
    cmp['ours' if x['our_rank'] < x['st_rank'] else 'startool' if x['st_rank'] < x['our_rank'] else 'tie'] += 1
OUT['startool'] = {
    'cards': len(st_rows), 'with_model': len(both),
    'st_top_hits': sum(x['st_top_hit'] for x in st_rows), 'st_top_pred': round(sum(x['st_top_p'] for x in st_rows), 2),
    'our_top_hits_same_games': sum(x['our_top_hit'] for x in both),
    'our_top_pred_same_games': round(sum(x['our_top_p'] for x in both), 2),
    'st_top_hits_same_games': sum(x['st_top_hit'] for x in both),
    'st_mean_rank_all': round(sum(x['st_rank'] for x in st_rows) / len(st_rows), 2),
    'st_unlisted': sum(x['st_rank'] == 11 for x in st_rows),
    'st_mean_rank_same': round(sum(x['st_rank'] for x in both) / len(both), 2),
    'our_mean_rank_same': round(sum(x['our_rank'] for x in both) / len(both), 2),
    'rank_compare': dict(cmp),
    'st_in_top2': sum(x['st_rank'] <= 2 for x in both), 'our_in_top2': sum(x['our_rank'] <= 2 for x in both),
    'st_in_top4': sum(x['st_rank'] <= 4 for x in both), 'our_in_top4': sum(x['our_rank'] <= 4 for x in both),
    'st_sum_listed': round(sum(sum(p for _, p in c['list']) for c in ST) / len(ST), 3),
    'games': [{k: v for k, v in x.items() if not k.startswith('_')} for x in st_rows]}

# ---------------------------------------------------------------- Bets tab
rows = list(csv.reader(open(sys.argv[1])))[1:]


def money(s):
    s = s.strip()
    if not s or s in ('-',) or 'DIV' in s:
        return None
    neg = s.startswith('(')
    v = float(re.sub(r'[^0-9.]', '', s) or 0)
    return -v if neg else v


def odds_of(r):
    F, E = r[6].strip(), r[5]
    if re.fullmatch(r'-?\d+(\.\d+)?', F):
        return float(F), 'slip'
    if r[4].strip().lower() in ('spread', 'total', 'moneyline'):
        return -110.0, 'fair'
    m = re.search(r'FD ([+-]\d+)', E)
    if m:
        return float(m.group(1)), 'slip'
    m = re.search(r'(?:fair|break-even)(?: about)? ([+-]\d+)', E)
    if m:
        return float(m.group(1)), 'fair'
    m = re.search(r'\((?:est |model )?(\d+(?:\.\d+)?)%', E) or re.search(r'(\d+(?:\.\d+)?)% (?:blend|of starts)', E)
    if m:
        return fair_from_p(float(m.group(1)) / 100), 'fair'
    return None, None


def prob_of(r):
    E = r[5]
    m = (re.search(r'est (\d+(?:\.\d+)?)%', E) or re.search(r'(\d+(?:\.\d+)?)% (?:blend|of starts|shrunk)', E)
         or re.search(r'\((?:model |center: est |about )?(\d+(?:\.\d+)?)%', E) or re.search(r'= (\d+(?:\.\d+)?)%', E))
    if m:
        return float(m.group(1)) / 100
    m = re.search(r'(?:fair|break-even)(?: about)? ([+-]\d+)', E)
    if m and r[4].strip().lower() not in ('spread', 'total', 'moneyline'):
        return 1 / dec(m.group(1))
    return None


def category(r):
    sp, D, E = r[2], r[4], r[5]
    Dl, El = D.lower(), E.lower()
    if any(k in Dl for k in ('parlay', 'round robin', 'sgp')):
        return f'{sp} parlay/RR'
    if sp == 'NBA':
        if Dl.startswith('first basket m'):
            return 'NBA FB method'
        if Dl == 'team first basket':
            return 'NBA team FB'
        if Dl == 'first basket':
            return 'NBA first basket'
        return {'points': 'NBA points', 'threes': 'NBA threes'}.get(Dl, 'NBA other')
    if sp == 'NHL':
        if 'goal' in Dl and 'first' in Dl:
            return 'NHL first goal'
        if 'anytime' in Dl:
            return 'NHL anytime goal'
        if 'sog' in Dl or 'shots' in Dl:
            return 'NHL SOG 2+' if 'over 1.5' in El or '2+ sog' in El else 'NHL SOG 3+'
    if sp in ('NFL', 'NCAAF'):
        lab = 'NFL' if sp == 'NFL' else 'CFB'
        if Dl == 'anytime td':
            return f'{lab} anytime TD'
        if Dl in ('first td',):
            return f'{lab} first TD'
        if Dl == '2+ tds':
            return f'{lab} 2+ TDs'
        if Dl == 'receptions' or (Dl == 'player prop' and 'rec' in El and 'yds' not in El):
            return f'{lab} receptions'
        if Dl == 'player prop':
            return f'{lab} yards'
        return f'{lab} sides/totals'
    if sp in ('UCL', 'Soccer'):
        return 'Soccer SOT' if 'shots on' in Dl or Dl == 'sot' else 'Soccer goals/sides'
    return f'{sp} other'


def tim_own(r):
    return bool(re.search(r"\(Tim[,')]|Tim's", r[5])) or r[0] == '368'


cats = defaultdict(lambda: {'n': 0, 'w': 0, 'void': 0, 'pl': 0.0, 'slip': 0, 'fair': 0, 'none': 0, 'pl_slip': 0.0, 'n_slip': 0})
tim = defaultdict(lambda: {'n': 0, 'w': 0, 'stake': 0.0, 'pl': 0.0, 'est': 0})
fb_logged = []
# P/L estimates where the sheet has no odds/payout (see report): 368 RR 2s Adebayo +500 x Fox +700 at $0.10;
# 482 RR 3s Adebayo x Murray (Doncic void) at fair +472/+510; CFB anytime TDs at -300; Tuch first goal at +900
EST = {'368': 4.80 - 2.40, '482': 0.1 * dec(472) * dec(510) - 1.10, '463': 0.2 * 9}
EST.update({str(k): 0.2 / 3 for k in range(324, 329)})
for r in rows:
    r += [''] * 12
    res = r[9].strip()
    if res not in ('W', 'L', 'Void', 'Push'):
        continue
    cat = category(r)
    H = r[8].strip()
    o, src = odds_of(r)
    # our picks: Pick / No rows and placed rows that are ours (not Tim's own adds); parlays are Tim's
    if H in ('Pick', 'No') or (H == 'Yes' and not tim_own(r) and 'parlay' not in cat):
        if 'parlay' in cat and H != 'Pick':
            pass
        else:
            c = cats[cat]
            if res in ('Void', 'Push'):
                c['void'] += 1
            else:
                c['n'] += 1; c['w'] += res == 'W'
                pp = prob_of(r)
                if pp is not None:
                    c['n_p'] = c.get('n_p', 0) + 1; c['exp'] = c.get('exp', 0) + pp; c['w_p'] = c.get('w_p', 0) + (res == 'W')
                if o is not None:
                    pl = 0.2 * (dec(o) - 1) if res == 'W' else -0.2
                    c['pl'] += pl; c[src] += 1
                    if src == 'slip':
                        c['pl_slip'] += pl; c['n_slip'] += 1
                else:
                    c['none'] += 1
            if cat == 'NBA first basket' and res in ('W', 'L'):
                m = re.search(r'est (\d+(?:\.\d+)?)%', r[5])
                fb_logged.append({'row': r[0], 'date': r[1], 'pick': r[5][:40], 'est': float(m.group(1)) / 100 if m else None,
                                  'odds': o, 'src': src, 'res': res})
    if H == 'Yes':
        t = tim[(r[2], cat if 'parlay' not in cat else f'{r[2]} parlay/RR', 'own' if tim_own(r) else 'ours')]
        stake = money(r[7]) or 0
        if res in ('Void', 'Push'):
            continue
        t['n'] += 1; t['w'] += res == 'W'; t['stake'] += stake
        k = money(r[11])
        if r[0] in EST and res == 'W':
            t['pl'] += EST[r[0]]; t['est'] += 1
        elif k is not None:
            t['pl'] += k
        elif res == 'L':
            t['pl'] -= stake
        else:
            if o is None and r[4].strip().lower() in ('spread', 'total', 'moneyline'):
                o, src = -110, 'fair'
            if o is None:
                t['unk'] = t.get('unk', 0) + 1; t['unk_rows'] = t.get('unk_rows', '') + r[0] + ' '
            else:
                t['pl'] += stake * (dec(o) - 1); t['est'] += src != 'slip'
OUT['cats'] = {k: dict(v, pl=round(v['pl'], 2), pl_slip=round(v['pl_slip'], 2), exp=round(v.get('exp', 0), 2)) for k, v in sorted(cats.items())}
OUT['tim'] = {' | '.join(k): dict(v, pl=round(v['pl'], 2), stake=round(v['stake'], 2)) for k, v in sorted(tim.items())}
OUT['fb_logged'] = fb_logged

os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
json.dump(OUT, open(os.path.join(HERE, 'out', 'summary.json'), 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in OUT.items() if k not in ('startool', 'fb_logged')}, indent=1, default=str))
print(json.dumps({k: v for k, v in OUT['startool'].items() if k != 'games'}, indent=1))

# ---------------------------------------------------------------- extras: star/bomb, logged picks, CV blend, jumper detail
SBF = sys.argv[3] if len(sys.argv) > 3 else None
fbo = [x['odds'] for x in fb_logged if x['src'] == 'slip']
fbo.sort()
MED = fbo[len(fbo) // 2] if fbo else 550
OUT['fb_slip_median_odds'] = MED
OUT['fb_slip_n'] = len(fbo)
if SBF:
    sb = {}
    for line in open(SBF):
        d, gm, stars, bombs = line.rstrip('\n').split('|')
        sb[(d, gm)] = (stars.split(','), bombs.split(','))
    agg = {'star': [0, 0, 0.0], 'bomb': [0, 0, 0.0]}
    for c in ST:
        key = (c['date'], c['game'])
        fe = FE.get(key)
        if key not in sb or not fe:
            continue
        scorer = norm(re.sub(r' \([A-Z]+\)$', '', fe['first_score']))
        pc = {norm(n): p for n, p in c['list']}
        for lab, names in zip(('star', 'bomb'), sb[key]):
            for n in names:
                a = agg[lab]; a[0] += 1; a[1] += norm(n) == scorer; a[2] += pc.get(norm(n), 0)
    OUT['star_bomb'] = {k: {'n': v[0], 'hits': v[1], 'expected': round(v[2], 1),
                            'roi_at_median_slip': round((v[1] * dec(MED) - v[0]) / v[0], 3)} for k, v in agg.items()}
# our logged first-basket picks: expected (est, else from fair odds) vs hits, ROI at slip odds where logged else fair
ex = 0; hits = 0; n = 0; pl_s = 0; n_s = 0; w_s = 0
for x in fb_logged:
    p = x['est'] if x['est'] else (1 / dec(x['odds']) if x['odds'] else None)
    if p is None:
        continue
    n += 1; ex += p; hits += x['res'] == 'W'
    if x['src'] == 'slip':
        n_s += 1; w_s += x['res'] == 'W'; pl_s += (dec(x['odds']) - 1) if x['res'] == 'W' else -1
OUT['fb_logged_summary'] = {'n': n, 'hits': hits, 'expected': round(ex, 2), 'slip_n': n_s, 'slip_w': w_s,
                            'slip_roi': round(pl_s / n_s, 3) if n_s else None,
                            'roi_at_median_slip_all': round((hits * dec(MED) - n) / n, 3)}
# top pick ROI per list on the 50 shared games at the median slip price
def top_roi(key):
    h = sum(x[key] for x in both)
    return {'n': len(both), 'hits': h, 'roi': round((h * dec(MED) - len(both)) / len(both), 3)}
bl_hits = 0
for x in both:
    sd = st_dist(x, 0.03)
    bd = {p: 0.5 * x['_ours'][p] + 0.5 * sd[p] for p in sd}
    bl_hits += max(bd, key=bd.get) == x['_w']
OUT['top_pick_roi'] = {'ours': top_roi('our_top_hit'), 'startool': top_roi('st_top_hit'),
                       'blend50': {'n': len(both), 'hits': bl_hits, 'roi': round((bl_hits * dec(MED) - len(both)) / len(both), 3)}}
# leave-one-day-out choice of w (floor 3%)
days = sorted({x['date'] for x in both})
cv_ll = 0; cv_w = []
for dday in days:
    tr = [x for x in both if x['date'] != dday]; te = [x for x in both if x['date'] == dday]
    bw = min((i / 10 for i in range(11)), key=lambda w: sum(llg(x, w) for x in tr))
    cv_w.append(bw); cv_ll += sum(llg(x, bw) for x in te)
OUT['blend_cv'] = {'ll': round(cv_ll / len(both), 4), 'weights_by_fold': cv_w, 'ours_only': round(sum(llg(x, 1) for x in both) / len(both), 4),
                   'st_only': round(sum(llg(x, 0) for x in both) / len(both), 4), 'uniform': round(math.log(10), 4)}
diffs = []
for _ in range(4000):
    smp = [random.choice(both) for _ in both]
    diffs.append(sum(llg(x, 1) - llg(x, 0.5) for x in smp) / len(smp))
diffs.sort()
OUT['boot_ours_minus_blend50'] = [round(diffs[100], 4), round(diffs[2000], 4), round(diffs[3900], 4)]
# jumper detail in 26-27
jd = Counter()
for g in G26:
    jm = {tm: pid for pid, tm in g['tip']['j']}
    w, wt = g['fb'][0], g['fb'][1]
    if jm.get(wt) == w:
        jd['jumper_fb_team_won_tip' if g['tip']['w'] == wt else 'jumper_fb_team_lost_tip'] += 1
        jd['jumper_fb_on_team_first_shot'] += g['ts'].get(wt) == w
    jd['games_tipwin'] += 1
OUT['jumper_detail'] = dict(jd)
json.dump(OUT, open(os.path.join(HERE, 'out', 'summary.json'), 'w'), indent=1, default=str)
for k in ('fb_slip_median_odds', 'fb_slip_n', 'star_bomb', 'fb_logged_summary', 'top_pick_roi', 'blend_cv', 'boot_ours_minus_blend50', 'jumper_detail'):
    print(k, json.dumps(OUT.get(k)))
