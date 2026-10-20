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
