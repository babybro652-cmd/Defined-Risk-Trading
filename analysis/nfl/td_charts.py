"""Week TD charts: anytime TD (top 20) and first TD (top 15 + each game's top pick).

Usage: python3 analysis/nfl/td_charts.py --week 10
Reads out/week_shortlist.csv (anytime chance from build_tracker.py) plus the status overrides below.

First TD method (no builder output): each player's TD rate r = -ln(1 - anytime chance) (Poisson).
Team TD rate = implied total x 0.11 (about 1 TD per 9 points). Player first-TD chance =
r / (both teams' TD rate) x P(game has a TD) = r / L x (1 - e^-L). If a team's listed players
sum past 85% of its TD rate they are scaled down to 85% (kick/defense TDs and the rest of the roster).
"""
import argparse, csv, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# Game-day overrides (Sun 11/15). Inactives: DET-NE posted 8:00 AM ET.
OUT_NOW = {"Josh Jacobs", "Puka Nacua"}
ACTIVE_CONFIRMED = {"Amon-Ra St. Brown": "Active (ribs), inactives in",
                    "Rhamondre Stevenson": "Active (knee), inactives in",
                    "A.J. Brown": "Active, inactives in"}
WINDOWS = [("9:30 AM", "Sun 9:30 AM ET (Munich)"), ("1:00 PM", "Sun 1 PM ET"),
           ("4:0", "Sun 4 PM window"), ("4:2", "Sun 4 PM window"),
           ("Sun 8:20", "SNF 8:20 PM"), ("Mon", "MNF Mon 8:15 PM")]
WIN_ORDER = ["Sun 9:30 AM ET (Munich)", "Sun 1 PM ET", "Sun 4 PM window", "SNF 8:20 PM", "MNF Mon 8:15 PM"]
INACTIVE_TIME = {"Sun 1 PM ET": "11:30 AM", "Sun 4 PM window": "2:35 PM", "SNF 8:20 PM": "6:50 PM",
                 "MNF Mon 8:15 PM": "Mon 6:45 PM"}


def american(p):
    if p <= 0: return "-"
    if p >= 0.5: return f"-{round(100 * p / (1 - p))}"
    return f"+{round(100 * (1 - p) / p)}"


def take_at(p, mode="dec"):
    """dec: fair decimal x1.2 (first TD). profit: fair profit x1.2 (anytime; matches the shortlist's Take-at)."""
    dec = 1 / p * 1.2 if mode == "dec" else 1 + (1 / p - 1) * 1.2
    return f"+{round((dec - 1) * 100)}" if dec >= 2 else f"-{round(100 / (dec - 1))}"


def window(game):
    for key, lab in WINDOWS:
        if key in game: return lab
    return None


def load():
    rows = []
    for r in csv.DictReader(open(os.path.join(OUT, "week_shortlist.csv"))):
        w = window(r["Week 10 game"])
        if w is None or "Thu" in r["Week 10 game"]: continue
        st = r["Injury status"]
        if r["Player"] in OUT_NOW: st = "Out"
        if st in ("Out", "IR", "Doubtful", "PUP"): continue
        if r["Player"] in ACTIVE_CONFIRMED: st = ACTIVE_CONFIRMED[r["Player"]]
        elif st == "Questionable": st = f"Q, unconfirmed (inactives {INACTIVE_TIME.get(w, 'TBD')})"
        else: st = ""
        g = r["Week 10 game"].split(" (")[0].replace(" VS ", " @ ")
        p = float(r["New TD chance"].rstrip("%")) / 100
        rows.append(dict(name=r["Player"], team=r["Team"], pos=r["Pos"], game=g, win=w, opp=r["Opponent"],
                         rank=r["Opp rank vs pos (2026)"], p=p, imp=float(r["Team implied total"]),
                         opp_imp=float(r["Opp implied total"]), status=st, qb=r["QB flag"]))
    return rows


def first_td(rows):
    for r in rows: r["rate"] = -math.log(1 - r["p"])
    teams = {}
    for r in rows: teams.setdefault(r["team"], []).append(r)
    for t, lst in teams.items():
        lam = lst[0]["imp"] * 0.11
        s = sum(x["rate"] for x in lst)
        k = min(1.0, 0.85 * lam / s)
        for x in lst: x["rate_adj"] = x["rate"] * k
    for r in rows:
        L = (r["imp"] + r["opp_imp"]) * 0.11
        r["pf"] = r["rate_adj"] / L * (1 - math.exp(-L))
        r["team_first"] = r["imp"] / (r["imp"] + r["opp_imp"]) * (1 - math.exp(-L))


BG, INK, MUTED, BAR, BAR2, WARN, GRID = "#ffffff", "#1d1d1f", "#6b6b70", "#2f6fd6", "#9cbcf0", "#c2410c", "#e6e6ea"


def draw_rows(ax, items, key, title, subtitle, note, show_rank=True, mode="dec"):
    groups = [(w, [x for x in items if x["win"] == w]) for w in WIN_ORDER]
    groups = [g for g in groups if g[1]]
    n = sum(len(g[1]) for g in groups) + len(groups) + 0.35 * sum(1 for x in items if x["status"])
    y = n
    ax.set_xlim(0, 1); ax.set_ylim(-0.6, n + 0.6); ax.axis("off")
    maxp = max(x[key] for x in items)
    for w, lst in groups:
        ax.text(0.0, y, w.upper(), fontsize=11, weight="bold", color=MUTED, va="center")
        y -= 1
        for x in lst:
            y0 = y
            ax.text(0.0, y + 0.16, f"{x['name']}", fontsize=12.5, weight="bold", color=INK, va="center")
            sub = f"{x['team']} {x['pos']}  {x['game']}"
            if show_rank: sub += f"  |  {x['opp']} #{x['rank']} vs {x['pos']}"
            if x["qb"]: sub += "  |  backup QB"
            ax.text(0.0, y - 0.24, sub, fontsize=9.5, color=MUTED, va="center")
            if x["status"]:
                ax.text(0.0, y - 0.55, x["status"], fontsize=9.5, color=WARN if x["status"].startswith("Q") else "#15803d",
                        weight="bold", va="center")
                y -= 0.35
            bx, bw = 0.47, 0.25
            ax.add_patch(plt.Rectangle((bx, y0 - 0.2), bw, 0.4, color=GRID, lw=0))
            ax.add_patch(plt.Rectangle((bx, y0 - 0.2), bw * x[key] / maxp, 0.4,
                                       color=BAR2 if x["status"].startswith("Q") else BAR, lw=0))
            ax.text(bx + bw + 0.01, y0, f"{x[key] * 100:.0f}%", fontsize=12.5, weight="bold", color=INK, va="center")
            ax.text(0.86, y0, american(x[key]), fontsize=12, color=INK, va="center", ha="center")
            ax.text(0.96, y0, take_at(x[key], mode), fontsize=12, color=INK, va="center", ha="center", weight="bold")
            y -= 1
    ax.text(0.86, n + 0.1, "Fair", fontsize=10, color=MUTED, ha="center", weight="bold")
    ax.text(0.96, n + 0.1, "Take at", fontsize=10, color=MUTED, ha="center", weight="bold")
    ax.set_title(title, fontsize=17, weight="bold", color=INK, loc="left", pad=34)
    ax.text(0, 1.0, subtitle, transform=ax.transAxes, fontsize=10, color=MUTED, va="bottom")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--week", type=int, default=10); a = ap.parse_args()
    rows = load(); first_td(rows)
    os.makedirs(os.path.join(OUT, "charts"), exist_ok=True)
    plt.rcParams["font.family"] = "DejaVu Sans"

    top = sorted(rows, key=lambda x: -x["p"])[:20]
    fig = plt.figure(figsize=(8, 17), facecolor=BG)
    ax = fig.add_axes([0.04, 0.07, 0.92, 0.86])
    draw_rows(ax, top, "p", f"NFL Week {a.week}: Anytime TD, top 20",
              "Sun 11/15 + Mon. Take at = fair payout x1.2 (as on shortlist). Def #1 = softest.", "", mode="profit")
    fig.text(0.04, 0.025, "Rules: RB / goal-line QB first. WR/TE only at +250 or longer, small stake. Skip shorter than -300.\n"
             "Out: Jacobs, Puka, Evans, Henderson, Ferguson, Hockenson, MHJ. Q players: bet only once listed active.\n"
             "Model chances, not promises. Small stakes.", fontsize=9.5, color=MUTED)
    p1 = os.path.join(OUT, "charts", f"td_wk{a.week}_anytime.png"); fig.savefig(p1, dpi=200, facecolor=BG); plt.close(fig)

    topf = sorted(rows, key=lambda x: -x["pf"])[:15]
    games = {}
    for r in rows: games.setdefault(r["game"], []).append(r)
    best = []
    for g, lst in games.items():
        b = max(lst, key=lambda x: x["pf"])
        home = g.split(" @ ")[1]
        tf = {x["team"]: x["team_first"] for x in lst}
        best.append((WIN_ORDER.index(b["win"]), g, b, tf))
    best.sort(key=lambda t: (t[0], t[1]))
    fig = plt.figure(figsize=(8, 19), facecolor=BG)
    ax = fig.add_axes([0.04, 0.38, 0.92, 0.56])
    draw_rows(ax, topf, "pf", f"NFL Week {a.week}: First TD, top 15",
              "Chance to score the game's first TD. Take at = fair decimal x1.2. Mostly noise, \\$0.10-0.50.", "",
              show_rank=True)
    ax2 = fig.add_axes([0.04, 0.085, 0.92, 0.27]); ax2.axis("off")
    ax2.set_xlim(0, 1); ax2.set_ylim(-0.5, len(best) + 1)
    ax2.text(0, len(best) + 0.6, "Most likely first TD scorer, each game", fontsize=14, weight="bold", color=INK)
    ax2.text(0.62, len(best) - 0.2, "Chance", fontsize=9.5, color=MUTED, weight="bold", ha="center")
    ax2.text(0.76, len(best) - 0.2, "Fair", fontsize=9.5, color=MUTED, weight="bold", ha="center")
    ax2.text(0.90, len(best) - 0.2, "Take at", fontsize=9.5, color=MUTED, weight="bold", ha="center")
    y = len(best) - 1
    for _, g, b, tf in best:
        lead = max(tf, key=tf.get)
        ax2.text(0, y + 0.12, f"{g}", fontsize=10.5, weight="bold", color=INK, va="center")
        ax2.text(0, y - 0.3, f"{lead} first TD {tf[lead] * 100:.0f}%", fontsize=8.5, color=MUTED, va="center")
        nm = b["name"] + (" (Q)" if b["status"].startswith("Q") else "")
        ax2.text(0.27, y, nm, fontsize=10.5, color=INK, va="center")
        ax2.text(0.62, y, f"{b['pf'] * 100:.1f}%", fontsize=10.5, color=INK, va="center", ha="center", weight="bold")
        ax2.text(0.76, y, american(b["pf"]), fontsize=10.5, color=INK, va="center", ha="center")
        ax2.text(0.90, y, take_at(b["pf"]), fontsize=10.5, color=INK, va="center", ha="center", weight="bold")
        y -= 1
    fig.text(0.04, 0.02, "Method: player TD rate = -ln(1 - anytime chance). Team TD rate = implied total x 0.11.\n"
             "First TD chance = player rate / both teams' TD rate x P(any TD). Team split follows implied totals.\n"
             "No opening-drive or script adjustment. Bet only at take-at or longer.", fontsize=9.5, color=MUTED)
    p2 = os.path.join(OUT, "charts", f"td_wk{a.week}_first.png"); fig.savefig(p2, dpi=200, facecolor=BG); plt.close(fig)
    print(p1, p2)
    for x in top: print("ANY", x["name"], x["game"], f"{x['p']:.3f}", american(x["p"]), take_at(x["p"], "profit"), x["status"])
    for x in topf: print("FIRST", x["name"], x["game"], f"{x['pf']:.3f}", american(x["pf"]), take_at(x["pf"]), x["status"])
    for _, g, b, tf in best: print("GAME", g, b["name"], f"{b['pf']:.3f}", american(b["pf"]), take_at(b["pf"]))


if __name__ == "__main__":
    main()
