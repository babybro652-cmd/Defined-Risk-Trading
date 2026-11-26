#!/usr/bin/env python3
"""Thanksgiving 11/26/26 per-game play charts: pick, line/price, our fair, edge."""
import sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

G = {
 'chi_det': ('CHI @ DET  1:00 PM ET  (CHI -1.5, total 56.5)', [
   ('DET +1.5 (side)', '-110', '55% / -122', '+3.4 pts (FPI DET by 1.9)', 55, 'Lean $0.50'),
   ('D\'Andre Swift anytime TD', 'take -105+', '56% / -126', 'only at -105 or longer', 56, 'BET at price $0.50'),
   ('Jahmyr Gibbs anytime TD', 'take -156+', '65% / -188', 'FD usually shorter: likely SKIP', 65, 'only at -156+'),
   ('Kyle Monangai anytime TD', 'take +170+', '41% / +142', 'only at +170 or longer', 41, 'small $0.20'),
   ('Swift first TD', 'take +891+', '12.1% / +726', 'only at +891 or longer', 12.1, '$0.20 at price'),
   ('Gibbs first TD', 'take +816+', '13.1% / +664', 'only at +816 or longer', 13.1, '$0.20 at price'),
   ('First scoring play', 'no edge', 'CHI TD 34.9% / +186', 'model = spread (x1.00)', 34.9, 'PASS'),
   ('Total 56.5', 'no model', '-', 'no edge', 0, 'PASS'),
 ]),
 'phi_dal': ('PHI @ DAL  4:30 PM ET  (DAL -8.5, total 49.5)', [
   ('DAL -8.5 (side)', '-110', '56% / -127', '+4.0 pts (FPI DAL by 12.5)', 56, 'Lean $0.50'),
   ('Javonte Williams anytime TD', 'take -143+', '63% / -171', 'only at -143 or longer', 63, 'BET at price $0.50'),
   ('Javonte Williams first TD', 'take +649+', '16.0% / +524', 'only at +649 or longer', 16.0, '$0.20 at price'),
   ('DAL TD first scoring play', 'take +189+', '41.5% / +141', 'x1.03 vs spread: thin', 41.5, '$0.20 only at +189+'),
   ('Saquon Barkley anytime TD', 'take +190+', '39% / +158', 'backup QB Milton cut', 39, 'small $0.20 at +190+'),
   ('Total 49.5', 'no model', '-', 'no edge', 0, 'PASS'),
 ]),
 'kc_buf': ('KC @ BUF  8:20 PM ET  (BUF -3, total 45.5)', [
   ('KC +3 / BUF -3 (side)', '-110', 'FPI BUF by 0.9', '2.1 pts: under 3, no lean', 0, 'PASS'),
   ('James Cook anytime TD', 'take -103+', '55% / -124', 'only at -103 or longer', 55, 'BET at price $0.50'),
   ('BUF TD first scoring play', 'take +235+', '35.9% / +179', 'x1.10 vs spread: best FS edge', 35.9, '$0.30 at +235+'),
   ('James Cook first TD', 'take +890+', '12.1% / +725', 'only at +890 or longer', 12.1, '$0.20 at price'),
   ('Emmett Johnson first TD', 'take +1275+', '8.7% / +1046', 'Walker out, RB1', 8.7, '$0.20 at price'),
   ('Total 45.5', 'no model', '-', 'no edge', 0, 'PASS'),
 ]),
}

def draw(key, out):
    title, rows = G[key]
    fig, ax = plt.subplots(figsize=(11, 0.62 * len(rows) + 1.6), dpi=130)
    ax.set_xlim(0, 100); ax.set_ylim(len(rows) + 0.4, -1.3); ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.text(0, -1.0, title, fontsize=13, weight='bold')
    hdr = [(0, 'Pick'), (27, 'Line / price'), (40, 'Our chance / fair'), (57, 'Edge'), (82, 'Play')]
    for x, h in hdr:
        ax.text(x, -0.3, h, fontsize=9.5, weight='bold', color='#444')
    for i, (p, line, fair, edge, ch, play) in enumerate(rows):
        y = i + 0.5
        if i % 2 == 0:
            ax.add_patch(plt.Rectangle((-0.5, y - 0.45), 101, 0.9, color='#f3f5f8', zorder=0))
        col = '#1a7f37' if ('BET' in play or 'Lean' in play or '$' in play) and 'PASS' not in play else '#9a9a9a'
        ax.text(0, y, p, fontsize=9.5, va='center')
        ax.text(27, y, line, fontsize=9.5, va='center')
        ax.text(40, y, fair, fontsize=9.5, va='center')
        ax.text(57, y, edge, fontsize=9, va='center')
        ax.text(82, y, play, fontsize=9.5, va='center', color=col, weight='bold')
    ax.text(0, len(rows) + 0.25, 'Take-at = fair x1.2. BET only at take-at or longer. Sides from ESPN FPI (sd 13.5, shrunk half), leans only. '
            'First TD/first score mostly noise.', fontsize=7.5, color='#666')
    fig.tight_layout(); fig.savefig(out); print(out)

if __name__ == '__main__':
    for k in (sys.argv[1:] or G):
        draw(k, f'/home/user/Defined-Risk-Trading/analysis/nfl/out/charts/thanksgiving_{k}.png')
