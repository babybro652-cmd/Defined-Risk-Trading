# College basketball (CBB): big games only

Tim, 11/14/26: college picks are CFB every Saturday and CBB big games only. Routine: "CBB big games only", daily 8:43 AM ET (skips days with none). No model yet; research picks from ESPN data, same idea as `analysis/ncaaf/`.

## What counts as a big game
- A Top 25 team (AP) against another Top 25 team or a power-conference team (ACC, Big Ten, Big 12, SEC, Big East), or
- A national TV game (ESPN, ESPN2, ABC, CBS, FOX, FS1, TNT, TBS, truTV, Peacock, NBC). ESPN+ and conference streams do not count.
- Skip Top 25 vs small-school buy games even on TV.

## Method
1. Slate: ESPN scoreboard `.../basketball/mens-college-basketball/scoreboard?dates=YYYYMMDD&groups=50&limit=400` (groups=50 is all D1; the default returns only Top 25). Rankings from `.../rankings`.
2. For each big game, pull `summary?event=<id>`: `predictor` (ESPN BPI matchup win %) and `pickcenter` (DraftKings spread, total, moneyline).
3. Fair spread from BPI win %: fair home spread = -11 x z(home win %), normal with sd 11 points (CBB margins). Examples: 60% = -2.8, 70% = -5.8, 76% = -7.8, 86% = -11.9.
4. Gap = line minus fair. Lean only at a gap of 3+ points; best 4 games at most per day.
5. Skip games where a key injury is unresolved (starter questionable, or out in the last box score with no update). ESPN's injury feed is often empty, so check the last box score for who started and played minutes.
6. Early season caution until mid-December: BPI leans on preseason priors, and teams have only played 2 to 4 games, many against buy-game opponents. Smaller stakes, and treat a 3 to 5 point gap as a lean, not an edge. From mid-December the gaps get more trustworthy.

## Player props
None. Tim, 11/15/26: CBB is sides and totals only, no player props.

## Logging and grading
- Log picks as Bets rows, Sport "NCAAB", Placed "Pick", with line, fair and a short reason. Never write J:K.
- Save `analysis/ncaab/picks-YYYY-MM-DD.md` per slate.
- Grade from the ESPN summary (final score and box score) in column I only (W, L, Void).

## Log
- 11/14/26: first slate. Thin Saturday (football day, no Big Ten games). Two big games: LSU @ #14 Gonzaga, Colorado @ Providence (Peacock).
- 11/15/26: 11/14 went 2-3 (sides 0-2, props 2-1). Six big games checked; only Louisville @ Memphis reached a 3-point gap (Memphis +8.5). Three props. Tim dropped the props the same morning: CBB is sides and totals only from 11/15.
- 11/17/26: 11/15 went 1-0 (Memphis +8.5 W); no big games 11/16. Seven big games checked; three reached a 3-point gap: Rutgers +18.5, Indiana +2.5, UNLV +18.5. Two are big-dog leans against BPI early-season priors; watch whether BPI underrates the top teams this early.
- 11/18/26: 11/17 went 2-1 (Rutgers +16.5 W placed, Indiana +2.5 W, UNLV +18.5 L). Five big games checked; two reached a 3-point gap: Rutgers +4.5, West Virginia +9.5 (both teams in each game on a back-to-back).
- 11/19/26: 11/18 went 1-1 (Rutgers +4.5 L, WVU +9.5 W; Tim passed after the lines moved). First pre-game run (1 hr before first tip, with chart in `out/`). Eight big games checked; picks NC State -2.5 (gap 6.4), VCU +2.5 (gap 5.0), $1.50 each from the $3 CBB budget. Kansas +3.5 (gap 4.8) skipped: Stokes DNP last night, Council out 3 games.
- 11/20/26: 11/19 went 3-0, all placed (NC State -3.5 W 93-83, VCU +1.5 W 83-77, VCU ML +104 W; $4.50 staked, +$4.40). Thirteen games checked (eight real matchups, five buy games skipped); one reached a 3-point gap: Oklahoma St +1.5 (gap 6.0). Northwestern +11.5 just missed (2.9). Tim then asked for the ranked buy games too: added Loyola MD +41.5 ($1), MVSU +38.5 ($0.50), Manhattan@Miami under 150.5 ($0.50); passed Coastal and EIU (4-game cap). BPI fair spread is compressed above about 97% win, so buy-game gaps also checked against season scoring averages.
