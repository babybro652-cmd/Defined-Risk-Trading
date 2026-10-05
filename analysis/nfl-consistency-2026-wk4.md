# NFL Consistency Report: Anytime TDs and Receptions (through 2026 Week 4)

Prepared Mon 10/5/2026 for Tim. Small stakes, for fun. Consistency first, not one big game.

**Live tracker:** [NFL Scorer Tracker 2026](https://docs.google.com/spreadsheets/d/1VPYeOtn3BGq4JYPiwkI_XfvVXCGyvg7nMhGGOzl2VTM/edit) (Google Sheet: scorers by week, red-zone usage, injuries, defense vs position, weekly shortlist). Refreshed each week with `analysis/nfl/build_tracker.py`.

## How this was built

- **Data:** every 2025 regular-season game (272 games, Weeks 1 to 18) and every 2026 game through Week 4 (63 games; ATL @ NO Monday night not yet played, so ATL and NO players show 3 games). Per-game stats were pulled from ESPN box scores and play-by-play (the same numbers that feed ESPN player game logs). Spot checks: Jaxon Smith-Njigba 2026 log (8, 9, 10, 5 catches) matches his ESPN game log; Trey McBride 2025 (126 catches on 169 targets) matches PlayerProfiler; CeeDee Lamb Week 4 (17 catches, 189 yards, 1 TD) matches news reports.
- **Sample:** 4 games is small. Rankings lean on the pooled 2025 + 2026 rate (about 20 games per player), with 2026 used to confirm the role is still the same.
- **TD hit rate** = games with a rushing or receiving TD / games played. Return TDs and passing TDs are not counted. Games played = games where the player shows up in the box score.
- **Red-zone (RZ) and inside-10 opportunities** = targets plus carries that started inside the opponent 20 (or 10), counted from ESPN play-by-play text. Plays wiped out by penalty are excluded. Treat these as close estimates, not official counts. Bijan Robinson and teammate Brian Robinson Jr. are told apart by the play-by-play initials ("Bi." vs "Br."); ATL had no red-zone snaps at all in Weeks 1 and 2.
- **Team TD share** = player's rushing + receiving TDs / all rushing + receiving TDs scored by his team in the games he played.
- **Target share** = player targets / team targets in games he played.
- **Not available:** routes run % (PlayerProfiler and PFF keep it behind a login or did not render; Pro-Football-Reference blocked requests with HTTP 403). It is left out rather than guessed.
- **Known gap:** ESPN box scores drop a receiver who played but drew zero targets, so a rare 0-catch, 0-target game may be missing. This can only flatter a floor, never hurt it.
- Defense ranks: **#1 = allows the most** to that position (softest), #32 = allows the least.

## Status check before betting (from ESPN injury feed, 10/5)

| Player | Status | Note |
|---|---|---|
| Ja'Marr Chase (CIN) | Questionable | Concussion in Week 4, left in the 2nd quarter. Must clear protocol. |
| Tee Higgins (CIN) | Questionable | Adductor issue in Week 4. His 11-catch game came with Chase out. |
| Lamar Jackson (BAL) | Questionable | Ankle, seen in a walking boot. Tyler Huntley played the 2nd half of Week 4. Affects Flowers and Henry. |
| Puka Nacua (LAR) | Active | Missed Weeks 2 and 3 (hip/groin), back in Week 4 with 9 catches and a rushing TD. |
| Justin Jefferson (MIN) | Inactive Week 4 | No designation detail in the feed. Check before betting. |
| DeVonta Smith (PHI) | Out Week 4 | Hamstring, "at very best questionable" for Week 5 in London. |
| Dallas Goedert (PHI) | Inactive Week 4 | |
| Keenan Allen (IND) | Out Week 4 | Groin. |
| Rashee Rice (KC) | Questionable | Hamstring. KC is on bye Week 5 anyway. |
| De'Von Achane (MIA) | Injured reserve | Knee. Removed from all lists. |
| Travis Etienne Jr. (NO) | Injured reserve | Hamstring. Removed. |
| A.J. Brown (NE) | Injured reserve | High-ankle sprain, not eligible until Week 6. Removed. |

**QB changes that move these numbers (2026 starters by week):** SEA Drew Lock Wk 1 to 2, Sam Darnold Wk 3 to 4. CHI Caleb Williams Wk 1 to 2, Case Keenum Wk 3, Tyson Bagent Wk 4. MIN Carson Wentz Wk 1 to 2, Kyler Murray Wk 3 to 4. NYG Jaxson Dart Wk 1 (now on IR for the season), Jameis Winston since. WSH Jayden Daniels Wk 1 to 2, then Mariota and Kaliakmanis (Daniels aims to return Week 5). TB Baker Mayfield Wk 1 to 3, Jalon Daniels Wk 4. ATL Cooper Rush Wk 1 to 2, Michael Penix Jr. Wk 3. ARI is Jacoby Brissett all four weeks.

**Players on new teams in 2026 (2025 numbers came with the old team):** Wan'Dale Robinson (NYG to TEN), Stefon Diggs (NE to WSH), Keenan Allen (LAC to IND), Jaylen Waddle (MIA to DEN), Mike Evans (TB to SF), Deebo Samuel (WSH to SF), Michael Pittman Jr. (IND to PIT), Kenneth Walker III (SEA to KC), Jauan Jennings (SF to MIN), Chris Rodriguez Jr. (WSH to JAX).

## Anytime TD: Top 15 by consistency

Ranked by combined hit rate (2025 + 2026), then 2026 hit rate. Opportunity columns show the goal-line role behind the rate.

| # | Player | Tm | Pos | 2026 games w/ TD | 2025 games w/ TD | Combined hit % | TDs 2026 / 2025 | Team TD share 26 / 25 | RZ opps/g 26 / 25 | Inside-10 opps/g 26 / 25 | Multi-TD games | Max in 1 game |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Christian McCaffrey | SF | RB | 3/4 | 12/17 | 71% | 4 / 17 | 25% / 35% | 3.8 / 5.7 | 2.2 / 2.8 | 5 | 3 |
| 2 | Jahmyr Gibbs | DET | RB | 4/4 | 10/17 | 67% | 7 / 18 | 50% / 32% | 6.8 / 3.8 | 2.8 / 1.5 | 7 | 3 |
| 3 | Javonte Williams | DAL | RB | 3/4 | 10/16 | 65% | 6 / 13 | 43% / 28% | 5.2 / 3.9 | 3.0 / 1.9 | 5 | 3 |
| 4 | Derrick Henry | BAL | RB | 4/4 | 9/17 | 62% | 7 / 16 | 50% / 35% | 5.2 / 3.6 | 3.8 / 2.2 | 7 | 4 |
| 5 | Kyren Williams | LAR | RB | 3/4 | 10/17 | 62% | 4 / 13 | 40% / 21% | 3.8 / 3.6 | 2.2 / 1.9 | 4 | 2 |
| 6 | Jonathan Taylor | IND | RB | 3/4 | 10/17 | 62% | 6 / 20 | 60% / 38% | 4.2 / 4.1 | 2.0 / 2.1 | 8 | 3 |
| 7 | Omarion Hampton | LAC | RB | 3/4 | 5/9 | 62% | 3 / 5 | 43% / 28% | 3.2 / 3.1 | 1.8 / 1.8 | 0 | 1 |
| 8 | Josh Allen | BUF | QB | 4/4 | 8/16 | 60% | 7 / 14 | 44% / 26% | 2.2 / 1.4 | 1.5 / 1.0 | 8 | 3 |
| 9 | George Kittle | SF | TE | 3/4 | 6/11 | 60% | 4 / 7 | 25% / 21% | 1.2 / 1.2 | 0.8 / 0.5 | 2 | 2 |
| 10 | James Cook III | BUF | RB | 3/4 | 9/17 | 57% | 3 / 14 | 19% / 24% | 3.8 / 3.4 | 2.2 / 1.5 | 4 | 3 |
| 11 | Puka Nacua | LAR | WR | 1/2 | 9/16 | 56% | 1 / 11 | 25% / 19% | 1.0 / 1.1 | 1.0 / 0.7 | 2 | 2 |
| 12 | Bijan Robinson | ATL | RB | 2/3 | 9/17 | 55% | 3 / 11 | 60% / 31% | 3.3 / 2.8 | 2.0 / 1.2 | 3 | 2 |
| 13 | Jaxon Smith-Njigba | SEA | WR | 3/4 | 8/17 | 52% | 6 / 10 | 46% / 23% | 2.5 / 0.9 | 1.2 / 0.4 | 4 | 3 |
| 14 | Trey McBride | ARI | TE | 2/4 | 9/17 | 52% | 2 / 11 | 22% / 29% | 2.2 / 1.8 | 1.8 / 0.5 | 2 | 2 |
| 15 | Davante Adams | LAR | WR | 1/4 | 9/14 | 56% | 2 / 14 | 20% / 26% | 1.0 / 2.2 | 0.0 / 1.6 | 5 | 3 |

**What stands out**

- **The RB goal-line backs own this list.** Every top 7 name is a lead back with about 2 or more inside-10 touches per game (Hampton is lowest at 1.8). That role is what makes a TD repeatable.
- **McCaffrey** is the steadiest: 15 of 21 games with a TD. 2026 inside-10 work is down a bit (2.2 per game vs 2.8) but the role is intact.
- **Gibbs and Henry** have scored in all 4 games of 2026 and own 50% of their team's TDs. Gibbs' 7 TDs include a 3-TD game (Week 3), but the 4/4 hit rate is what matters here.
- **Kyren Williams** scored in 10 of 17 in 2025 and 3 of 4 in 2026, and never more than 2 TDs in a game in this sample. Lowest spike risk of the lead RBs.
- **Omarion Hampton** has never scored more than 1 TD in a game. 8 of 13 games with a TD. Pure steady, small sample (9 games in 2025).
- **Josh Allen** (QB) has a rushing TD in all 4 games of 2026 but 8/16 in 2025. He is the best non-RB TD bet when he gets goal-line sneaks.
- **Kittle** is the only TE scoring at 60%, but his red-zone volume is low (1.2 opps per game). The rate is ahead of the usage, so expect some cooling.
- **Pass catchers:** Puka (9 of 16 in 2025), JSN, McBride and Adams are the WR/TE options. McBride and JSN get the most red-zone looks of the pass catchers here (2.2 and 2.5 per game in 2026).

**One-game spikes that inflate totals (TD count looks bigger than the hit rate):**

| Player | Spike | Effect |
|---|---|---|
| Jonathan Taylor | Five 3-TD games in 2025 (20 TDs total) | 20 TDs came in only 10 of 17 games. Bet the 62% hit rate, not the TD total. |
| Derrick Henry | 4-TD game late in 2025, 3-TD game in 2026 Week 1 | Still 13 of 21 games, so the rate holds. |
| Davante Adams | 3-TD game in 2025, only 1 of 4 games in 2026, 0 inside-10 looks in 2026 | 2025 rate (9/14) is propping him up. Role looks smaller next to a healthy Puka. |
| Jaxon Smith-Njigba | 3-TD game in 2026 (Wk 2) | 6 TDs in 2026 came in 3 games. 2025 was 8 of 17. |
| D'Andre Swift | 3 TDs in Week 1, 0 since | 1 of 4 in 2026. Not on the list for that reason. |
| Brock Bowers | 3-TD game in 2025 | 4 of 12 games in 2025 (33%). |
| James Cook III | 3-TD game in 2025 | 9 of 17. Fine rate, but only 3 TDs in 2026 and 19% team share. |

**Next tier (missed the cut):** Amon-Ra St. Brown (3/4 in 2026, 7/17 in 2025), Garrett Wilson (2/4, 4/7), Christian Watson (3/4, 4/10), Tee Higgins (1/4, 9/15, questionable), Kenneth Walker III (3/4 in 2026 with KC, but 4/17 in 2025 with SEA; KC on bye), Nico Collins (2/2, 6/15).

## Receptions: Top 15 by consistency

Ranked by how often the player cleared 4.5 catches across both seasons, then by the low end of his range (20th percentile game) and standard deviation. Lower std dev = steadier.

| # | Player | Tm | Pos | Games (25+26) | Avg 2026 | Avg 2025 | Avg all | Floor 2026 | Floor 2025 | Std dev | Over 3.5 | Over 4.5 | Over 5.5 | Over 6.5 | Tgt share 26 / 25 | 2026 by game |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Trey McBride | ARI | TE | 21 (17+4) | 8.2 | 7.4 | 7.6 | 7 | 4 | 2.1 | 21/21 | 20/21 | 16/21 | 14/21 | 31% / 27% | 9 8 9 7 |
| 2 | Jaxon Smith-Njigba | SEA | WR | 21 (17+4) | 8.0 | 7.0 | 7.2 | 5 | 2 | 1.9 | 20/21 | 19/21 | 16/21 | 15/21 | 37% / 36% | 8 9 10 5 |
| 3 | Puka Nacua | LAR | WR | 18 (16+2) | 7.0 | 8.1 | 7.9 | 5 | 2 | 2.7 | 17/18 | 17/18 | 14/18 | 13/18 | 27% / 30% | 5 9 |
| 4 | CeeDee Lamb | DAL | WR | 17 (13+4) | 9.2 | 5.8 | 6.6 | 5 | 1 | 3.1 | 16/17 | 15/17 | 11/17 | 8/17 | 32% / 25% | 5 8 7 17 |
| 5 | Chris Olave | NO | WR | 19 (16+3) | 9.0 | 6.2 | 6.7 | 8 | 3 | 2.3 | 16/19 | 15/19 | 13/19 | 10/19 | 29% / 29% | 10 8 9 |
| 6 | Amon-Ra St. Brown | DET | WR | 21 (17+4) | 7.8 | 6.9 | 7.0 | 4 | 0 | 3.0 | 19/21 | 16/21 | 15/21 | 13/21 | 29% / 31% | 10 9 4 8 |
| 7 | Ja'Marr Chase | CIN | WR | 20 (16+4) | 5.2 | 7.8 | 7.3 | 2 | 2 | 3.7 | 16/20 | 16/20 | 13/20 | 11/20 | 18% / 32% | 2 7 9 3 |
| 8 | Christian McCaffrey | SF | RB | 21 (17+4) | 4.0 | 6.0 | 5.6 | 3 | 1 | 2.1 | 18/21 | 14/21 | 11/21 | 7/21 | 20% / 23% | 5 4 4 3 |
| 9 | Zay Flowers | BAL | WR | 20 (17+3) | 6.0 | 5.1 | 5.2 | 5 | 2 | 1.8 | 16/20 | 13/20 | 8/20 | 7/20 | 30% / 29% | 5 5 8 |
| 10 | Brock Bowers | LV | TE | 14 (12+2) | 8.0 | 5.3 | 5.7 | 6 | 1 | 2.6 | 13/14 | 10/14 | 6/14 | 3/14 | 32% / 24% | 10 6 |
| 11 | Wan'Dale Robinson | TEN | WR | 20 (16+4) | 4.0 | 5.8 | 5.4 | 1 | 1 | 2.6 | 14/20 | 13/20 | 10/20 | 6/20 | 21% / 30% | 5 1 7 3 |
| 12 | George Pickens | DAL | WR | 21 (17+4) | 4.5 | 5.5 | 5.3 | 2 | 1 | 2.4 | 15/21 | 13/21 | 10/21 | 7/21 | 19% / 23% | 3 6 7 2 |
| 13 | Drake London | ATL | WR | 15 (12+3) | 5.0 | 5.7 | 5.5 | 2 | 1 | 2.7 | 11/15 | 8/15 | 7/15 | 6/15 | 27% / 30% | 2 4 9 |
| 14 | Tyler Warren | IND | TE | 21 (17+4) | 5.8 | 4.5 | 4.7 | 3 | 2 | 1.7 | 15/21 | 11/21 | 5/21 | 3/21 | 22% / 21% | 3 6 9 5 |
| 15 | Davante Adams | LAR | WR | 18 (14+4) | 5.5 | 4.3 | 4.6 | 3 | 1 | 1.5 | 15/18 | 8/18 | 4/18 | 2/18 | 24% / 25% | 3 8 7 4 |

**What stands out**

- **Trey McBride is the steadiest catch bet in the league right now.** Over 3.5 catches in 21 of 21 games, over 4.5 in 20 of 21, lowest game 4. 2026: 9, 8, 9, 7 on a 31% target share with Brissett at QB.
- **Jaxon Smith-Njigba** has the lowest std dev of the high-volume group (1.9) and a 37% target share, the highest on the list. One clunker in 21 games (2 catches). His 5-catch Week 4 came on only 6 targets in a run-heavy win.
- **Puka Nacua** cleared 4.5 in 17 of 18 games when active. The only risk is health: he missed Weeks 2 and 3 with the hip.
- **CeeDee Lamb's 2026 average (9.2) is inflated by the 17-catch Week 4.** Without it he is 5, 8, 7. His 2025 floor was 1. Still 15 of 17 over 4.5.
- **Chris Olave** has 8 or more in all 3 games of 2026 (Shough at QB), 29% target share both years. 2025 had three 3-catch games, so his true floor is lower than 2026 shows.
- **Ja'Marr Chase** is elite over a full season (7.8 per game in 2025) but 2026 is 2, 7, 9, 3, and the Week 4 number is from a concussion exit. Wait on his status.
- **McCaffrey** catches dropped in 2026 (4.0 per game vs 6.0). Fine for over 3.5 (18 of 21), less safe at 4.5.
- **Zay Flowers** has a 1.8 std dev and 5+ in all 3 games of 2026. Depends on Lamar's ankle.

## Steady floor list (receptions overs)

Players who almost never fall below the line. Best line to target in parentheses.

| Player | Line to target | Hit rate at that line | Lowest game (2025 / 2026) | Std dev |
|---|---|---|---|---|
| Trey McBride (ARI TE) | Over 5.5 | 16/21 (over 4.5: 20/21) | 4 / 7 | 2.1 |
| Jaxon Smith-Njigba (SEA WR) | Over 5.5 | 16/21 (over 4.5: 19/21) | 2 / 5 | 1.9 |
| Puka Nacua (LAR WR) | Over 4.5 | 17/18 | 2 / 5 | 2.7 |
| Amon-Ra St. Brown (DET WR) | Over 3.5 | 19/21 | 0 / 4 | 3.0 |
| Christian McCaffrey (SF RB) | Over 3.5 | 18/21 | 1 / 3 | 2.1 |
| Zay Flowers (BAL WR) | Over 3.5 | 16/20 | 2 / 5 | 1.8 |
| Davante Adams (LAR WR) | Over 3.5 | 15/18 | 1 / 3 | 1.5 |
| Sam LaPorta (DET TE) | Over 3.5 | 9/13 (5, 6, 3, 8 in 2026) | 3 / 3 | 1.5 |
| Stefon Diggs (WSH WR) | Over 3.5 | 13/21 (4, 5, 4, 5 in 2026) | 2 / 4 | 2.2 |

Diggs and LaPorta are low-ceiling, low-variance plays: good for small overs at 3.5, not for big lines.

## Avoid: boom-bust

| Player | Why | Game-by-game |
|---|---|---|
| Michael Wilson (ARI WR) | Std dev 3.7, highest on the board. A 15-catch game and three 1-catch games in 2025. Over 4.5 in only 9 of 21. | 2026: 5, 2, 11, 7. 2025 started 1, 1, 1, 3, 2 |
| Tetairoa McMillan (CAR WR) | 2026 average (6.5) is one 14-catch game. Otherwise 5, 5, 2. Over 4.5 in 10 of 21. CAR on bye anyway. | 2026: 5, 5, 2, 14 |
| Dalton Schultz (HOU TE) | 12 catches in Week 2, then 3 and 2. | 2026: 4, 12, 3, 2 |
| Jake Ferguson (DAL TE) | Range 0 to 13. 3.0 per game in 2026 with Lamb and Pickens eating. | 2026: 2, 4, 3, 3 |
| Kyle Pitts Sr. (ATL TE) | 2 catches in 3 games of 2026 (2 targets per game). | 2026: 0, 1, 1 |
| Tee Higgins (CIN WR) | 11 catches in Week 4 came with Chase out. 2025 average 3.9, over 4.5 in 9 of 19. Also questionable. | 2026: 3, 5, 6, 11 |
| Travis Kelce (KC TE) | One 9-catch game, three games of 2 or 3. | 2026: 3, 9, 2, 2 |
| Courtland Sutton (DEN WR) | 2.2 per game in 2026, with Jaylen Waddle now in Denver. | 2026: 2, 3, 3, 1 |
| Jonathan Taylor (TD) | 20 TDs in 2025 came in 10 games, five of them 3-TD games. Fine hit rate, but don't chase TD totals or 2+ TD props. | 2025 TD games: 0 1 3 0 3 1 3 3 0 3 0 0 1 0 1 1 0 |
| D'Andre Swift (TD) | 3 TDs in Week 1, 0 since. | 2026: 3, 0, 0, 0 |
| Davante Adams (TD) | 9/14 in 2025 included a 3-TD game. 1 of 4 in 2026 with 0 inside-10 looks. | 2026: 0, 2, 0, 0 |

## 2026 only rankings

Same data, but only this season's 4 games (3 for ATL and NO). Use it to spot who is hot right now; the pooled lists above are steadier.

### 2026 only: Anytime TD top 15

Ranked by number of 2026 games with a TD, then red-zone opps per game. No 2025 data in the order.

| # | Player | Tm | Pos | 2026 games w/ TD | TDs | RZ opps/g | Inside-10/g | Team RZ share | 2026 by game |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Jahmyr Gibbs | DET | RB | 4/4 | 7 | 6.8 | 2.8 | 48% | 2 1 3 1 |
| 2 | Derrick Henry | BAL | RB | 4/4 | 7 | 5.2 | 3.8 | 54% | 3 1 2 1 |
| 3 | Josh Allen | BUF | QB | 4/4 | 7 | 2.2 | 1.5 | 23% | 2 2 2 1 |
| 4 | Kenneth Walker III | KC | RB | 3/4 | 6 | 5.5 | 3.0 | 54% | 2 0 2 2 |
| 5 | Javonte Williams | DAL | RB | 3/4 | 6 | 5.2 | 3.0 | 46% | 2 0 1 3 |
| 6 | Jonathan Taylor | IND | RB | 3/4 | 6 | 4.2 | 2.0 | 47% | 2 2 0 2 |
| 7 | Christian McCaffrey | SF | RB | 3/4 | 4 | 3.8 | 2.2 | 36% | 0 2 1 1 |
| 8 | Kyren Williams | LAR | RB | 3/4 | 4 | 3.8 | 2.2 | 44% | 1 1 0 2 |
| 9 | James Cook III | BUF | RB | 3/4 | 3 | 3.8 | 2.2 | 38% | 0 1 1 1 |
| 10 | Omarion Hampton | LAC | RB | 3/4 | 3 | 3.2 | 1.8 | 38% | 1 1 0 1 |
| 11 | Amon-Ra St. Brown | DET | WR | 3/4 | 5 | 3.0 | 1.0 | 21% | 2 2 1 0 |
| 12 | Chuba Hubbard | CAR | RB | 3/4 | 5 | 2.8 | 2.0 | 28% | 2 1 0 2 |
| 13 | Jaxon Smith-Njigba | SEA | WR | 3/4 | 6 | 2.5 | 1.2 | 23% | 1 3 2 0 |
| 14 | Christian Watson | GB | WR | 3/4 | 4 | 1.8 | 1.0 | 16% | 2 1 1 0 |
| 15 | CeeDee Lamb | DAL | WR | 3/4 | 4 | 1.5 | 0.8 | 13% | 1 2 0 1 |

### 2026 only: Receptions top 15

Ranked by 2026 catches per game, then the lowest game (floor). Minimum 3 games played in 2026.

| # | Player | Tm | Pos | Games | Avg | Floor | Over 4.5 | Over 5.5 | Tgt share | 2026 by game |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CeeDee Lamb | DAL | WR | 4 | 9.2 | 5 | 4/4 | 3/4 | 32% | 5 8 7 17 |
| 2 | Chris Olave | NO | WR | 3 | 9.0 | 8 | 3/3 | 3/3 | 29% | 10 8 9 |
| 3 | Trey McBride | ARI | TE | 4 | 8.2 | 7 | 4/4 | 4/4 | 31% | 9 8 9 7 |
| 4 | Jaxon Smith-Njigba | SEA | WR | 4 | 8.0 | 5 | 4/4 | 3/4 | 37% | 8 9 10 5 |
| 5 | Amon-Ra St. Brown | DET | WR | 4 | 7.8 | 4 | 3/4 | 3/4 | 29% | 10 9 4 8 |
| 6 | RJ Harvey | DEN | RB | 3 | 6.7 | 4 | 2/3 | 2/3 | 22% | 4 6 10 |
| 7 | Tetairoa McMillan | CAR | WR | 4 | 6.5 | 2 | 3/4 | 1/4 | 27% | 5 5 2 14 |
| 8 | DeVonta Smith | PHI | WR | 3 | 6.3 | 3 | 2/3 | 2/3 | 33% | 3 10 6 |
| 9 | Tee Higgins | CIN | WR | 4 | 6.2 | 3 | 3/4 | 2/4 | 25% | 3 5 6 11 |
| 10 | Michael Wilson | ARI | WR | 4 | 6.2 | 2 | 3/4 | 2/4 | 30% | 5 2 11 7 |
| 11 | Zay Flowers | BAL | WR | 3 | 6.0 | 5 | 3/3 | 1/3 | 30% | 5 5 8 |
| 12 | Garrett Wilson | NYJ | WR | 4 | 6.0 | 3 | 3/4 | 2/4 | 28% | 6 5 10 3 |
| 13 | Jalen Coker | CAR | WR | 3 | 6.0 | 2 | 2/3 | 2/3 | 20% | 8 8 2 |
| 14 | Tyler Warren | IND | TE | 4 | 5.8 | 3 | 3/4 | 2/4 | 22% | 3 6 9 5 |
| 15 | Jahmyr Gibbs | DET | RB | 4 | 5.5 | 4 | 3/4 | 2/4 | 18% | 5 6 7 4 |

**What stands out (2026 only)**

- **Gibbs, Henry and Josh Allen are the only players with a TD in all 4 games.** Gibbs has the most red-zone work in the league on this count (6.8 per game); Henry has the most inside-10 work (3.8).
- **Kenneth Walker III** (3 of 4, 5.5 RZ opps per game, 54% of KC's red-zone looks) is the biggest riser versus 2025 (4 of 17 with SEA). KC is on bye in Week 5.
- **Chuba Hubbard** (3 of 4, CAR) and **Christian Watson** (3 of 4) make the 2026 list but not the pooled one. CAR is on bye.
- **Receptions:** 4 of the 2026 top 5 are also in the pooled top 5 (Lamb, Olave, McBride, JSN); St. Brown takes the spot of Puka, who has only 2 games. **RJ Harvey** (DEN RB, 4, 6, 10) is the 2026-only name to watch. **McMillan, Higgins and Michael Wilson** sit high on averages built on one big game; their floors are 2 or 3.
- Puka Nacua (2 games) and Brock Bowers (2 games) miss the 3-game minimum for the catch list.

## Week 5 schedule and matchups

**Byes:** Kansas City and Carolina (Kenneth Walker III, Travis Kelce, Rashee Rice, Tetairoa McMillan, Chuba Hubbard). None of the pooled top 15 in either list is on bye (Walker, Hubbard, McMillan and Coker from the 2026-only lists are).

Opponent columns are 2026 Weeks 1 to 4 per game allowed to that position (rank, #1 = most allowed), with the 2025 full-season rank in parentheses as a second look.

### TD list matchups

| Player | Week 5 game | Opp TDs allowed to position per game, 2026 (rank) | 2025 rank | Read |
|---|---|---|---|---|
| Christian McCaffrey | SF @ SEA (Sun) | RB 0.8 (#15) | #32 | Neutral. SEA was the stingiest vs RB TDs in 2025. Role carries it. |
| Jahmyr Gibbs | DET @ ARI (Sun) | RB 0.5 (#26) | #2 | Mixed. Role is the reason to play it. |
| Javonte Williams | TB @ DAL (Thu) | RB 0.2 (#28) | #17 | Tough matchup. Lower the stake. |
| Derrick Henry | BAL @ ATL (Sun night) | RB 0.3 (#27) | #21 | Tough on paper. If Lamar sits, Henry could see even more goal-line work. |
| Kyren Williams | BUF @ LAR (Mon night) | RB 1.5 (#3) | #5 | Best RB matchup on the list. |
| Jonathan Taylor | IND @ PIT (Sun) | RB 1.0 (#11) | #31 | Neutral. |
| Omarion Hampton | DEN @ LAC (Sun) | RB 1.0 (#14) | #19 | Neutral. |
| Josh Allen | BUF @ LAR (Mon night) | QB rushing not split out | n/a | 4 for 4 in 2026. |
| George Kittle | SF @ SEA (Sun) | TE 0.5 (#12) | #21 | Neutral. |
| James Cook III | BUF @ LAR (Mon night) | RB 0.0 (#31) | #30 | LAR has allowed 0 RB TDs. Pass. |
| Puka Nacua | BUF @ LAR (Mon night) | WR 1.5 (#5) | #24 | Good. |
| Bijan Robinson | BAL @ ATL (Sun night) | RB 1.0 (#10) | #16 | Neutral to good. |
| Jaxon Smith-Njigba | SF @ SEA (Sun) | WR 0.8 (#16) | #19 | Neutral. |
| Trey McBride | DET @ ARI (Sun) | TE 1.5 (#1) | #11 | Best TE matchup on the board. |
| Davante Adams | BUF @ LAR (Mon night) | WR 1.5 (#5) | #24 | Good matchup, shrinking role. |

### Receptions list matchups

| Player | Week 5 game | Opp catches allowed to position per game, 2026 (rank) | 2025 rank | Read |
|---|---|---|---|---|
| Trey McBride | DET @ ARI | TE 9.2 (#1) | #19 | Best spot on the board. |
| Jaxon Smith-Njigba | SF @ SEA | WR 10.5 (#20) | #9 | Neutral; volume carries it. |
| Puka Nacua | BUF @ LAR | WR 13.2 (#7) | #28 | Good, if the hip holds. |
| CeeDee Lamb | TB @ DAL (Thu) | WR 8.8 (#31) | #11 | Tough. TB has allowed the 2nd fewest WR catches. |
| Chris Olave | MIN @ NO | WR 10.8 (#19) | #32 | Neutral. MIN was stingiest vs WRs in 2025. |
| Amon-Ra St. Brown | DET @ ARI | WR 9.2 (#26) | #15 | Below average matchup. Stick to 3.5 or 4.5. |
| Ja'Marr Chase | CIN @ MIA | WR 9.8 (#24) | #21 | Concussion; skip until cleared. |
| Christian McCaffrey | SF @ SEA | RB 5.8 (#4) | #1 | Good for catches. SEA is #4 in RB catches allowed in 2026 and was #1 in 2025. |
| Zay Flowers | BAL @ ATL (Sun night) | WR 14.3 (#5) | #17 | Good matchup, QB risk (Lamar). |
| Brock Bowers | LV @ NE | TE 3.2 (#27) | #10 | Tough. |
| Wan'Dale Robinson | HOU @ TEN | WR 15.0 (#2) | #29 | Good matchup, but his 2026 role is shaky (5, 1, 7, 3). |
| George Pickens | TB @ DAL (Thu) | WR 8.8 (#31) | #11 | Tough. |
| Drake London | BAL @ ATL (Sun night) | WR 14.8 (#3) | #2 | Good both years. 9 catches with Penix in Week 3. |
| Tyler Warren | IND @ PIT | TE 3.2 (#28) | #4 | Tough in 2026, soft in 2025. |
| Davante Adams | BUF @ LAR | WR 13.2 (#7) | #28 | Good for over 3.5. |

## Week 5 shortlist

**Anytime TD**

1. **Christian McCaffrey** (SF @ SEA): 15 of 21 games, best hit rate in the sample.
2. **Jahmyr Gibbs** (DET @ ARI): 4 of 4 in 2026, 50% of Detroit's TDs, 6.8 red-zone opps per game.
3. **Kyren Williams** (vs BUF, Mon night): 13 of 21, never a spike, and Buffalo allows the 3rd most RB TDs.
4. **Derrick Henry** (BAL @ ATL, Sun night): 4 of 4 in 2026, 3.8 inside-10 opps per game. Tough matchup, so a smaller stake.
5. **Trey McBride** (DET @ ARI): Detroit allows the most TE TDs (1.5 per game) and McBride gets 2.2 red-zone looks per game. Lower hit rate (11 of 21), so expect a longer price.

**Receptions overs**

1. **Trey McBride over 5.5 or 6.5** (vs DET): 9, 8, 9, 7 this year; DET allows the most TE catches.
2. **Jaxon Smith-Njigba over 5.5** (vs SF): 16 of 21 over 5.5, std dev 1.9.
3. **Puka Nacua over 5.5** (vs BUF): 14 of 18 over 5.5, if he practices fully.
4. **Christian McCaffrey over 3.5** (@ SEA): 18 of 21, SEA is top 4 in RB catches allowed both years.
5. **Drake London over 4.5** (vs BAL): BAL top 3 in WR catches allowed both years. Higher variance, so a small stake.

Skip this week: Lamb and Pickens overs (TB allows few WR catches), Chase (concussion), James Cook TD (LAR allows 0 RB TDs), anyone from KC or CAR (bye).

## Sample size note

Four games is a small sample, and some players have only 2 or 3 (Puka, Bowers, Collins, Olave, ATL and NO players). Rankings lean on the pooled 2025 + 2026 rate (17 to 21 games per player). 2026 was used to confirm the role, the QB and the health, not to set the rate. Defense-vs-position numbers from 4 games are noisy, so the 2025 rank is shown next to each one.

## Sources

- ESPN game summaries and box scores (site.api.espn.com summary endpoint), all 2025 regular-season games and 2026 Weeks 1 to 4. Per-game receptions, targets, rushing and receiving TDs, and play-by-play for red-zone and inside-10 counts.
- ESPN scoreboard (2025 Weeks 1 to 18, 2026 Weeks 1 to 5) for game results, Week 5 schedule and byes.
- ESPN player game log for Jaxon Smith-Njigba 2026 (cross-check): https://www.espn.com/nfl/player/gamelog/_/id/4430878/jaxon-smith-njigba
- ESPN NFL injuries page (status and notes as of 10/5/2026): https://www.espn.com/nfl/injuries
- ESPN statistics by athlete (player positions): https://www.espn.com/nfl/stats
- PlayerProfiler, Trey McBride (cross-check of 2025 targets and catches): https://www.playerprofiler.com/nfl/trey-mcbride/
- ESPN weekly leaders, Week 4 (CeeDee Lamb 17-189-1 cross-check): https://www.espn.com/nfl/weekly/leaders/_/type/receiving
- Pro-Football-Reference (https://www.pro-football-reference.com/years/2026/receiving.htm) and FootballDB returned HTTP 403, so no numbers here come from them. Routes run % was not available from any reachable source.
