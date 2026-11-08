# NFL Week 9: Sunday 11/8 and Monday 11/9/2026 (TD model v2, rebuilt Sun 11/8 afternoon)

Rebuilt Sun 11/8 with `python3 analysis/nfl/build_tracker.py --week 9 --slate 9` (2025 + 2026 Weeks 1 to 8, TNF JAX @ BAL, and CIN vs ATL).
The Anytime TD numbers below come from the new TD model v2 (`analysis/nfl/td_model.py`, backtest in `analysis/nfl/README.md`):
hit rate shrunk toward a position and usage prior, Vegas implied team total, goal-line (inside 5) share, red-zone and WR/TE red-zone-target share,
logistic fit on earlier games only, and a backup-QB cut. Spread and totals are ESPN/DraftKings as of Sun 11/8.
Not written to the Bet Tracker (write blocked). Bet only at take-at or longer, $0.20, never shorter than -300.
WR/TE TDs only at +250 or longer (Tim's rule from 11/8, pending his confirm). The 1:00 games had already kicked off, so only the 4:05 and later games are listed as plays.

## Anytime TD shortlist, games not yet started (v2)

| # | Player | Game | Team implied | GL share (inside 5) | New chance | Fair | Take-at (x1.2) | Verdict | Note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey SF RB | LV @ SF Sun 4:25 PM ET | 30.0 | 45% | 71.7% | -253 | -211 | Play | old rule: Play |
| 2 | Josh Jacobs GB RB | GB @ NE Sun 4:25 PM ET | 20.8 | 52% | 58.1% | -139 | -116 | Play | old rule: Small stake |
| 3 | D'Andre Swift CHI RB | TB @ CHI Sun 8:20 PM ET | 26.8 | 40% | 53.3% | -114 | +105 | Play | old rule: Skip |
| 4 | James Cook III BUF RB | BUF @ MIN Mon 8:15 PM ET | 23.2 | 30% | 52.3% | -110 | +109 | Play | old rule: Small stake |
| 5 | Zach Charbonnet SEA RB | ARI @ SEA Sun 4:25 PM ET | 24.0 | 46% | 51.9% | -108 | +111 | Play | backup QB cut: Drew Lock expected to start; old rule: Play |
| 6 | Ashton Jeanty LV RB | LV @ SF Sun 4:25 PM ET | 21.5 | 38% | 48.1% | +108 | +130 | Play | old rule: Skip |
| 7 | Omarion Hampton LAC RB | HOU @ LAC Sun 4:05 PM ET | 17.5 | 39% | 43.3% | +131 | +157 | Small stake | old rule: Small stake |
| 8 | George Kittle SF TE | LV @ SF Sun 4:25 PM ET | 30.0 | 7% | 42.0% | +138 | +166 | Small stake | WR/TE: needs +250 or longer; RZ tgt share 22%; old rule: Play |
| 9 | Bucky Irving TB RB | TB @ CHI Sun 8:20 PM ET | 20.8 | 16% | 40.5% | +147 | +176 | Small stake | old rule: Skip |
| 10 | Brock Bowers LV TE | LV @ SF Sun 4:25 PM ET | 21.5 | 8% | 38.2% | +162 | +194 | Small stake | WR/TE: needs +250 or longer; RZ tgt share 32%; old rule: Skip |
| 11 | Rhamondre Stevenson NE RB | GB @ NE Sun 4:25 PM ET | 23.8 | 22% | 36.1% | +177 | +212 | Small stake | old rule: Skip |
| 12 | Jaxon Smith-Njigba SEA WR | ARI @ SEA Sun 4:25 PM ET | 24.0 | 7% | 35.6% | +181 | +218 | Small stake | backup QB cut: Drew Lock expected to start; WR/TE: needs +250 or longer; RZ tgt share 28%; old rule: Play |
| 13 | Woody Marks HOU RB | HOU @ LAC Sun 4:05 PM ET | 23.0 | 22% | 35.5% | +182 | +218 | Small stake | old rule: Skip |
| 14 | Josh Allen BUF QB | BUF @ MIN Mon 8:15 PM ET | 23.2 | 26% | 35.2% | +184 | +221 | Small stake | old rule: Small stake |
| 15 | Nico Collins HOU WR | HOU @ LAC Sun 4:05 PM ET | 23.0 | 11% | 34.6% | +189 | +227 | Small stake | WR/TE: needs +250 or longer; RZ tgt share 25%; old rule: Skip |
| 16 | Sean Tucker TB RB | TB @ CHI Sun 8:20 PM ET | 20.8 | 31% | 34.4% | +191 | +229 | Small stake | old rule: Skip |
| 17 | Tucker Kraft GB TE | GB @ NE Sun 4:25 PM ET | 20.8 | 8% | 32.8% | +205 | +246 | Small stake | WR/TE: needs +250 or longer; RZ tgt share 24%; old rule: Skip |
| 18 | Jordan Mason MIN RB | BUF @ MIN Mon 8:15 PM ET | 20.2 | 19% | 31.5% | +217 | +260 | Small stake | old rule: Skip |
| 19 | Emanuel Wilson SEA RB | ARI @ SEA Sun 4:25 PM ET | 24.0 | 28% | 31.5% | +218 | +261 | Small stake | backup QB cut: Drew Lock expected to start; old rule: Skip |
| 20 | Jahdae Walker CHI WR | TB @ CHI Sun 8:20 PM ET | 26.8 | 9% | 31.0% | +223 | +267 | Small stake | WR/TE: needs +250 or longer; RZ tgt share 12%; old rule: Small stake |
| 21 | Trey McBride ARI TE | ARI @ SEA Sun 4:25 PM ET | 15.5 | 13% | 30.9% | +223 | +268 | Small stake | backup QB cut: Gardner Minshew II expected to start; WR/TE: needs +250 or longer; RZ tgt share 29%; old rule: Small stake |
| 22 | Aaron Jones Sr. MIN RB | BUF @ MIN Mon 8:15 PM ET | 20.2 | 11% | 30.1% | +232 | +279 | Small stake | old rule: Skip |

Below the cut (Skip, still 28%+): Kyle Monangai 39.6%, Hunter Henry 33.5%, Colston Loveland 31.0%, Kaelon Black 30.6%, Kimani Vidal 29.0%, Roschon Johnson 28.7%, Rome Odunze 28.2%.

## What moved vs the Saturday list (old hit-rate method)

- Christian McCaffrey: 65% (-186) to 72% (-253). Implied total 30.0 and a 45% goal-line share. Take-at is -211, so take him only at -211 or longer; skip if FanDuel is shorter.
- Josh Jacobs (GB) and D'Andre Swift (CHI): new Plays at 58% and 53%. Both lead their team in inside-5 work (52% and 40%). Old rule had them Small stake and Skip.
- Zach Charbonnet (SEA): stays a Play at 52% even with the backup-QB cut (Darnold out, Drew Lock). Emanuel Wilson is a small stake.
- Ashton Jeanty (LV) 48% (Play) and Omarion Hampton (LAC) 43% (Small stake) are new on goal-line share (38% and 39%).
- James Cook III: unchanged, 52% (-110), take-at +109.
- George Kittle: 45% to 42% (+138). Goal-line share is 7%, so he lives on receiving red-zone looks. WR/TE rule: +250 or longer only.
- Jaxon Smith-Njigba: Saturday Play (old rule) to 36% (+181) with the Lock cut. WR rule: +250 or longer only. Trey McBride 31% with Minshew, same rule.
- WR/TE overall: every WR/TE is now Small stake at best (nobody clears 45%). That matches the 2-12 WR/TE results.

## Started games (1:00 slot, for grading only, not plays)

| Player | Game | New chance | Fair |
|---|---|---|---|
| Jahmyr Gibbs DET RB | DET @ MIA Sun 1:00 PM ET | 63.3% | -172 |
| Javonte Williams DAL RB | DAL @ IND Sun 1:00 PM ET | 62.6% | -168 |
| Kenneth Walker III KC RB | NYJ @ KC Sun 1:00 PM ET | 60.6% | -154 |
| Jonathan Taylor IND RB | DAL @ IND Sun 1:00 PM ET | 59.2% | -145 |
| Kyren Williams LAR RB | LAR @ WSH Sun 1:00 PM ET | 53.9% | -117 |
| Jonah Coleman DEN RB | DEN @ CAR Sun 1:00 PM ET | 49.5% | +102 |
| Amon-Ra St. Brown DET WR | DET @ MIA Sun 1:00 PM ET | 48.2% | +107 |
| Davante Adams LAR WR | LAR @ WSH Sun 1:00 PM ET | 47.6% | +110 |
| Rashee Rice KC WR | NYJ @ KC Sun 1:00 PM ET | 46.5% | +115 |
| De'Von Achane MIA RB | DET @ MIA Sun 1:00 PM ET | 45.1% | +122 |

## Receptions shortlist

| # | Player | Line | Game | Opp rank vs pos catches | 2026 catches | Est | Fair |
|---|---|---|---|---|---|---|---|
| 1 | Trey McBride ARI TE | 7+ | @ SEA 4:25 | SEA #19 vs TE | 9 8 9 7 9 7 10 7 | 75% | -300 |
| 2 | CeeDee Lamb DAL WR | 5+ | @ IND 1:00 | IND #30 (tough) | 5 8 7 17 2 9 5 7 | 72% | -257 |
| 3 | Malik Nabers NYG WR | 5+ | @ PHI 1:00 | PHI #5 | 6 1 5 6 11 12 7 | 70% | -233 |
| 4 | George Kittle SF TE | 4+ | vs LV 4:25 | LV #3 vs TE | 2 4 6 4 5 5 8 | 70% | -233 |
| 5 | Jahmyr Gibbs DET RB | 4+ | @ MIA 1:00 | MIA #6 vs RB | 5 6 7 4 5 5 2 | 70% | -233 |
| 6 | Puka Nacua LAR WR | 6+ | @ WSH 1:00 | WSH #6 vs WR | 5 9 17 6 8 11 | 68% | -213 |
| 7 | Brock Bowers LV TE | 5+ | @ SF 4:25 | SF #10 vs TE | 10 6 8 4 6 7 | 68% | -213 |
| 8 | Jaxon Smith-Njigba SEA WR | 6+ | vs ARI 4:25 | ARI #27 (tough) | 8 9 10 5 5 12 9 6 | 58% | -138 |

Amon-Ra St. Brown 5+ (65%, fair -186) only if he is active (Q, ribs); MIA is #31 vs WR catches.

## Drop or downgrade (injury / QB)

- Jaxon Smith-Njigba TD: rule says Play, but Darnold is out and Drew Lock starts; LT Cross and G Nelson out; total 45.5 to 39.5. Downgrade to small stake at +150 or longer. Cooper Kupp: skip.
- Trey McBride / Michael Wilson: new QB Gardner Minshew (Brissett traded to BAL). McBride catches stay (target floor), TD stays small stake only.
- Saquon Barkley, all PHI: 3rd-string QB Joe Milton starts, McKee Q; line flipped PHI -5.5 to NYG -3, total 38.5. Skip PHI props.
- Amon-Ra St. Brown: Q (ribs). Skip TD; catches only if active at the 11:30 AM inactives.
- Out: Mike Evans, Deebo Samuel, Christian Kirk, Brandon Aiyuk (SF); Garrett Wilson (NYJ); DeVonta Smith, Dontayvion Wicks (PHI); Brian Robinson Jr. (ATL); TreVeyon Henderson (NE); David Montgomery (HOU); Rashid Shaheed (SEA); Treylon Burks (WSH); KaVontae Turpin (DAL).
- Doubtful: Cam Skattebo NYG (Singletary leads). IR: Jeremiyah Love ARI (Allgeier RB1), Tyrone Tracy NYG, Terry McLaurin WSH.
- Q: George Pickens, Jake Ferguson (DAL; boosts Lamb), Emeka Egbuka (TB), Hunter Henry (NE), Kyle Monangai (CHI), MarShawn Lloyd (GB), DJ Moore, Keon Coleman, Joshua Palmer (BUF, Monday).
- QB, Monday: Kyler Murray out, Carson Wentz starts for MIN. Skip Jefferson and Hockenson props; Cook and Allen stay small.
- CLE: Shedeur Sanders starts (Watson Q).

## Line moves (ESPN open to now)

- ARI @ SEA: SEA -13.5 to -8.5, total 45.5 to 39.5 (Darnold out).
- NYG @ PHI: PHI -5.5 to NYG -3, total 44.5 to 38.5 (Milton).
- HOU @ LAC: LAC -1.5 to HOU -6, total 43.5 to 40.5 (LAC winless).
- BUF @ MIN: total 48.5 to 43.5 (Wentz).
- DAL @ IND: IND -1.5 to DAL -4.5. LV @ SF: SF -8.5 to -10, total 46.5 to 51.5.
- CIN vs ATL total 48.5 to 52.5. NYJ @ KC total 41.5 to 47.5. TB @ CHI: CHI -3.5 to -6.
