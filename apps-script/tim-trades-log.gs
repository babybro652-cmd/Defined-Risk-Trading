/**
 * Tim's own trades -> "Tim Trades" tab in the CRT Trade Tracker sheet.
 *
 * The CRT Pro Trades / Trades tabs are filled by the indicator webhooks, so
 * Tim's real (hand-placed) trades go on their own tab and never mix into the
 * indicator stats.
 *
 * How to use: open the CRT Trade Tracker sheet -> Extensions -> Apps Script ->
 * add a new file, paste this whole file, save, pick the function for the
 * trade (e.g. logTrade_20261020) in the dropdown -> Run. It creates the tab
 * the first time and appends one row. Running it twice adds a duplicate row,
 * so run each trade's function once.
 */

const TIM_TAB = 'Tim Trades';
const TIM_HEADERS = [
  'Date', 'Entry Time (ET)', 'Exit Time (ET)', 'Session', 'Instrument', 'Side', 'Contracts',
  'Account', 'Entry', 'Stop', 'Target', 'Exit', 'Exit Reason', 'Risk (pts)', 'P&L (pts)',
  'R', 'P&L $', 'Source', 'Notes',
];

function timTradesSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(TIM_TAB);
  if (!sh) {
    sh = ss.insertSheet(TIM_TAB);
    sh.getRange(1, 1, 1, TIM_HEADERS.length).setValues([TIM_HEADERS]).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

function appendTimTrade_(row) {
  if (row.length !== TIM_HEADERS.length) throw new Error('Row has ' + row.length + ' values, expected ' + TIM_HEADERS.length);
  timTradesSheet_().appendRow(row);
}

// Tue 10/20/2026 ES long, target hit. Paper account (Tim, 10/20).
function logTrade_20261020() {
  appendTimTrade_([
    '2026-10-20', 'before 9:55', '9:58', 'NY', 'ES', 'LONG', 2,
    'Paper', 7714.50, 7710.50, 7744.50, 7744.50, 'TP', 4.00, 30.00,
    7.5, 3000, 'DRT Phone Screen_Recording_20261020_095850_TradingView.mp4',
    'Target filled 2 @ 7744.50. $ = 30 pts x $50 x 2, before commissions.',
  ]);
}

// Tue 10/20/2026 ES short #1 (afternoon), stopped out. Paper account (Tim, 10/20).
// Recording opens at 1:44 PM with the position already on; entry time not shown.
function logTrade_20261020_2() {
  appendTimTrade_([
    '2026-10-20', 'before 1:44', '1:53', 'NY', 'ES', 'SHORT', 2,
    'Paper', 7763.00, 7767.00, 7741.00, 7767.00, 'SL', 4.00, -4.00,
    -1, -400, 'DRT Phone Screen_Recording_20261020_135352_TradingView.mp4',
    'Stop filled 2 @ 7767.00. $ = -4 pts x $50 x 2, before commissions.',
  ]);
}

// Tue 10/20/2026 ES short #2, re-entry minutes after #1 stopped. Closed by hand
// on the turn after price came 1 tick from target (Tim, 10/20). Paper account.
function logTrade_20261020_3() {
  appendTimTrade_([
    '2026-10-20', '1:53-1:56', '3:47', 'NY', 'ES', 'SHORT', 2,
    'Paper', 7766.00, 7770.00, 7746.00, 7754.75, 'Manual', 4.00, 11.25,
    2.81, 1125, 'DRT Phone Screen_Recording_20261020_154729_TradingView.mp4',
    'Closed 2 @ 7754.75 by hand: came 1 tick from the 7746 target and turned. In almost 2 hrs, open P&L reached $1,800 twice and $1,975 once; Tim closed on the turn. $ = 11.25 pts x $50 x 2, before commissions.',
  ]);
}
