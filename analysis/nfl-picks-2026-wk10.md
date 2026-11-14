# NFL Week 10 first look (built Wed 11/11, TD model v2)

Built with `python3 analysis/nfl/build_tracker.py --week 9` (2026 through MNF BUF @ MIN). Full list: `analysis/nfl/out/week_shortlist.csv`
and the NFL Scorer Tracker "Week Shortlist" tab (top 41 rows pushed). Lines are ESPN as of Wed; recheck Saturday.
Rules: bet only at take-at or longer, $0.20; RB/QB Play 45%+; WR/TE only at +250 or longer; no TD parlays over 2 legs.

## TNF Thu 11/12: WSH @ NYG 8:15 PM ET (NYG implied 22.0, WSH 19.5)

TD (none reach Play):
- Isaiah Likely NYG TE 33% (fair +204, take +250 or longer per WR/TE rule). Small stake only.
- Jacory Croskey-Merritt WSH RB 32% (fair +215, take +258). Small stake.
- Cam Skattebo NYG OUT. Singletary 26% (+280), Nabers 30% (+234, take +281): skip unless the board is long.

Receptions (parlay-eligible category):
- Malik Nabers 5+ receptions: 7 of 8 games in 2026 (6 1 5 6 11 12 7 5); WSH allows 13.2 WR catches/g (#4 softest). Est 70%, fair -233.
- Stefon Diggs 4+ receptions: 5 of 7 in 2026, 9 of 17 in 2025. Est 60%, fair -150.
- Isaiah Likely 4+ receptions: 6 of 8 in 2026. Est 57%, fair -133.

## Sunday/Monday first look (v2 Plays, 45%+ RB/QB)

| Player | Game | Chance | Fair | Take-at |
|---|---|---|---|---|
| Christian McCaffrey SF | SF @ DAL 4:25 | 71% | -246 | -205 |
| Jahmyr Gibbs DET | NE vs DET 9:30 AM (intl) | 62% | -167 | -139 |
| Javonte Williams DAL | SF @ DAL 4:25 | 60% | -153 | -128 |
| James Cook III BUF | BUF @ NYJ 1:00 | 59% | -144 | -120 |
| Kenneth Walker III KC | KC @ ATL 1:00 | 57% | -133 | -111 (Mahomes Q) |
| Derrick Henry BAL | LAC @ BAL Mon | 57% | -131 | -109 |
| Jonathan Taylor IND | MIA @ IND 1:00 | 55% | -124 | -103 |
| Kyren Williams LAR | LAR @ ARI 4:05 | 51% | -105 | +114 |
| Zach Charbonnet SEA | SEA @ LV 4:05 | 50% | +102 | +122 (Lock at QB) |
| Bijan Robinson ATL | KC @ ATL 1:00 | 49% | +105 | +126 |

Injuries to watch: Josh Jacobs OUT (finger; Kaleb Johnson leads GB), Puka Nacua DOUBTFUL (MCL), Rhamondre Stevenson DOUBTFUL,
Mahomes Q (elbow), Herbert Q, McCarthy Q, Lamar Jackson IR (thumb), Malik Willis IR (MIA backup QB), Jake Ferguson OUT, Deebo/Evans/Pickens Q,
Garrett Wilson Q (concussion), Watson to start for CLE.

## Saturday 11/14 recheck (final designations, TNF in)

Rebuilt Sat 11/14 with `python3 analysis/nfl/build_tracker.py --week 10 --slate 10` (TNF WSH @ NYG in the stats; injuries feed 15:48 UTC).
Sheet: Injuries (all 270 rows), Week Shortlist (top 55 rows) and Notes pushed. No Week 10 NFL rows on the Bet Tracker yet (nothing dated 11/15).
Defense rank #1 = softest vs that position.

### Anytime TD, Sunday/Monday (v2)

| Player | Game | Opp rank vs pos | Chance | Fair | Take-at | Verdict |
|---|---|---|---|---|---|---|
| Christian McCaffrey SF RB | @ DAL 4:25 | DAL #4 vs RB | 72% | -251 | -209 | Play |
| Jahmyr Gibbs DET RB | vs NE 9:30 AM (Munich) | NE #23 | 62% | -161 | -134 | Play |
| Javonte Williams DAL RB | vs SF 4:25 | SF #28 | 60% | -151 | -126 | Play |
| James Cook III BUF RB | @ NYJ 1:00 | NYJ #6 | 59% | -144 | -120 | Play |
| Derrick Henry BAL RB | vs LAC Mon | LAC #8 | 57% | -132 | -110 | Play (Huntley at QB) |
| Jonathan Taylor IND RB | vs MIA 1:00 | MIA #8 | 56% | -125 | -104 | Play |
| Kyren Williams LAR RB | @ ARI 4:05 | ARI #16 | 51% | -105 | +114 | Play |
| Bijan Robinson ATL RB | vs KC 1:00 | KC #25 | 50% | -101 | +118 | Play (new, ATL total up) |
| Zach Charbonnet SEA RB | @ LV 4:05 | LV #10 | 50% | +102 | +122 | Play (Lock at QB) |
| Kenneth Walker III KC RB | @ ATL 1:00 | ATL #6 | 58% | -138 | -115 | Small stake, Q groin: only if active at 11:30 AM |
| Bhayshul Tuten JAX RB | @ TEN 1:00 | TEN #21 | 42% | +138 | +166 | Small stake |
| Omarion Hampton LAC RB | @ BAL Mon | BAL #12 | 40% | +148 | +178 | Small stake |
| Josh Allen BUF QB | @ NYJ 1:00 | NYJ #14 | 39% | +156 | +187 | Small stake |

WR/TE (+250 or longer only): Rashee Rice 41%, Kittle 41%, Ja'Marr Chase 41%, Tee Higgins 38%, CeeDee Lamb 36%.

### Receptions (blended 2026 x2 + 2025 hit rate, x0.95)

| Player | Line | Game | Opp rank vs pos catches | 2026 log | Est | Fair |
|---|---|---|---|---|---|---|
| Trey McBride ARI TE | 7+ | vs LAR 4:05 | LAR #17 vs TE | 9 8 9 7 9 7 10 7 7 (9/9) | 76% | -317 (pass if shorter than -300) |
| Tyler Warren IND TE | 4+ | vs MIA 1:00 | MIA #7 vs TE | 3 6 9 5 7 4 4 (6/7) | 74% | -278 |
| Brock Bowers LV TE | 5+ | vs SEA 4:05 | SEA #12 vs TE | 10 6 8 4 6 7 7 (6/7) | 73% | -271 (Mendoza QB) |
| Drake London ATL WR | 4+ | vs KC 1:00 | KC #27 (tough) | 2 4 9 5 7 4 7 1 5 (7/9) | 73% | -268 |
| Keenan Allen IND WR | 4+ | vs MIA 1:00 | MIA #29 (tough) | 6 1 6 5 8 3 7 4 (6/8) | 72% | -257 |
| Christian McCaffrey SF RB | 4+ | @ DAL 4:25 | DAL #16 vs RB | 5 4 4 3 3 9 6 2 (5/8) | 72% | -257 |
| Tetairoa McMillan CAR WR | 4+ | @ NO 1:00 | NO #18 | 5 5 2 14 6 4 6 4 (7/8) | 69% | -224 |
| CeeDee Lamb DAL WR | 6+ | vs SF 4:25 | SF #23 | 5 8 7 17 2 9 5 7 10 (6/9) | 61% | -158 (5+ is 83%, too short) |

Kittle 4+ is 84% (fair -543, too short) and 5+ is under 55%: skip. Evans OUT may add targets for Kittle and Deebo.

### Drop / downgrade

- Josh Jacobs GB: OUT (finger surgery). Kaleb Johnson leads GB.
- Puka Nacua LAR: IR (was Doubtful Wed). Davante Adams IR. Michael Wilson ARI IR (neck).
- Kenneth Walker III KC: Q (groin). Wait for inactives; drop if out.
- Amon-Ra St. Brown DET: Q (ribs, limited Fri). Skip TD and 7+ catches until active.
- Garrett Wilson NYJ: Q (concussion, one step left). Skip 4+ catches until cleared.
- Rhamondre Stevenson NE: Q (knee); TreVeyon Henderson OUT.
- Mike Evans SF: OUT. Marvin Harrison Jr. HOU: OUT. T.J. Hockenson MIN: OUT. Jake Ferguson DAL: OUT. Carnell Tate TEN: OUT.
- David Montgomery HOU: Q (groin). Ladd McConkey LAC: Q (back, no practice Fri). Jordan Addison MIN: Q (thumb).
- Cleared: Mahomes (full week, no tag), Deebo, Pickens, Tuten, Woody Marks, Goff.
- QB: Drew Lock SEA (Darnold out), Fernando Mendoza LV listed starter over Cousins, ARI depth chart starter not Brissett, MIA backup (Willis IR), Tyler Huntley BAL (Lamar IR), Watson CLE.

### Line moves since Wed (team implied totals)

KC 24.5 to 25.2 and ATL 21.0 to 22.2 (total up about 2); DET 27.0 to 26.0 and NE 24.5 to 23.5 (total down 2); MIN 19 to 20; CLE 17 to 18;
SF 29.5 to 30.0, DAL 26.0 to 25.5. Chances moved under 2 points; Bijan Robinson rose to Play at 50%.
