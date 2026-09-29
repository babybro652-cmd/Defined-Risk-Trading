/**
 * CRT Setups -> Google Sheet trade tracker (Google Apps Script)
 *
 * Receives the JSON webhook alerts from the "CRT Setups" TradingView indicator
 * (pine/crt-setups.pine) and records them:
 *   Trades  - one row per trade: setup, level, session, entry, stop, exit, P&L
 *   Setups  - every setup and every missed setup (no 1m trigger)
 *   Log     - every alert received, raw
 *   Summary - win rate, net P&L, profit factor, and results by week, setup
 *             type, level, session and exit reason
 *
 * Setup: see apps-script/README.md
 */

// Must match "Webhook Key" in the indicator settings. Leave both empty to skip the check.
const SECRET = 'change-me';

const TRADES = 'Trades';
const SETUPS = 'Setups';
const LOG = 'Log';
const SUMMARY = 'Summary';

const TRADE_HEADERS = [
  'Trade ID', 'Week Of', 'Date', 'Entry Time (NY)', 'Session', 'Side', 'Setup', 'Level', 'Counter-Trend',
  'Trigger', 'Entry', 'Stop', 'TP1', 'Last Stop', 'Exit Time (NY)', 'Exit Price', 'Exit Reason',
  'P&L $', 'Best Open $', 'Result', 'Contracts',
];
// 1-based column numbers in the Trades sheet (A = 1)
const COL = {
  id: 1, week: 2, date: 3, entryTime: 4, session: 5, side: 6, setup: 7, level: 8, ct: 9,
  trigger: 10, entry: 11, sl: 12, tp1: 13, lastSl: 14, exitTime: 15, exitPrice: 16, reason: 17,
  pnl: 18, best: 19, result: 20, contracts: 21,
};
const SETUP_HEADERS = ['Received', 'Bar Time (NY)', 'Week Of', 'Event', 'Side', 'Setup', 'Level', 'Stage', 'Zone / Level Price', 'Counter-Trend'];
const LOG_HEADERS = ['Received', 'Event', 'Trade ID', 'Symbol', 'Bar Time (NY)', 'Payload'];

/** TradingView sends each alert here as an HTTP POST. */
function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const body = e && e.postData ? e.postData.contents : '';
    if (!body) {
      // Run from the editor (no alert data): build the tabs instead
      setup();
      sheet_(LOG, LOG_HEADERS).appendRow([new Date(), 'SETUP RUN', '', '', '', 'doPost was run from the editor with no alert data, so the tabs were set up instead.']);
      return reply_('setup done');
    }
    let d;
    try {
      d = JSON.parse(body);
    } catch (err) {
      // A plain-text alert (Alert Format "Text") is pointed at this sheet. Delete that alert in TradingView.
      sheet_(LOG, LOG_HEADERS).appendRow([new Date(), 'TEXT ALERT (ignored)', '', '', '', body]);
      return reply_('ignored: not json');
    }
    if (SECRET && d.key !== SECRET) return reply_('forbidden');
    delete d.key;

    let status = 'ok';
    if (d.event === 'ENTRY') status = onEntry_(d);
    else if (d.event === 'STOP') status = onStop_(d);
    else if (d.event === 'EXIT') status = onExit_(d);
    else if (d.event === 'SETUP' || d.event === 'MISSED') status = onSetup_(d);

    const label = status === 'ok' ? d.event : d.event + ' (' + status + ')';
    sheet_(LOG, LOG_HEADERS).appendRow([new Date(), label, d.id || '', d.symbol || '', d.time || '', JSON.stringify(d)]);

    return reply_('ok');
  } finally {
    lock.releaseLock();
  }
}

/** Adds a "CRT Tracker" menu to the sheet so setup and the test trade can be run without the editor. */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('CRT Tracker')
    .addItem('Set up / repair tabs', 'setup')
    .addItem('Add a test trade', 'testTrade')
    .addItem('Remove duplicate setups', 'removeDuplicateSetups')
    .addToUi();
}

/** Open the web app URL in a browser to check the deployment is live. */
function doGet() {
  return reply_('CRT Setups tracker is live');
}

function onEntry_(d) {
  const sh = sheet_(TRADES, TRADE_HEADERS);
  if (findRow_(sh, d.id)) return 'duplicate';
  const row = new Array(TRADE_HEADERS.length).fill('');
  row[COL.id - 1] = d.id;
  row[COL.week - 1] = weekOf_(d.time);
  row[COL.date - 1] = String(d.time || '').slice(0, 10);
  row[COL.entryTime - 1] = d.time;
  row[COL.session - 1] = d.session;
  row[COL.side - 1] = d.side;
  row[COL.setup - 1] = d.setup;
  row[COL.level - 1] = d.level;
  row[COL.ct - 1] = d.ct;
  row[COL.trigger - 1] = d.trigger;
  row[COL.entry - 1] = d.entry;
  row[COL.sl - 1] = d.sl;
  row[COL.tp1 - 1] = d.tp1;
  row[COL.lastSl - 1] = d.sl;
  row[COL.contracts - 1] = d.contracts;
  sh.appendRow(row);
  return 'ok';
}

function onStop_(d) {
  const sh = sheet_(TRADES, TRADE_HEADERS);
  const r = findRow_(sh, d.id);
  if (!r) return 'no matching entry';
  sh.getRange(r, COL.lastSl).setValue(d.sl);
  return 'ok';
}

function onExit_(d) {
  const sh = sheet_(TRADES, TRADE_HEADERS);
  const r = findRow_(sh, d.id);
  if (!r) return 'no matching entry';
  if (sh.getRange(r, COL.exitTime).getValue() !== '') return 'duplicate';
  const pnl = Math.round(Number(d.pnl_usd) * 100) / 100;
  const best = d.best_usd === null || d.best_usd === undefined ? '' : Math.round(Number(d.best_usd) * 100) / 100;
  const result = pnl > 0 ? 'Win' : pnl < 0 ? 'Loss' : 'Breakeven';
  sh.getRange(r, COL.exitTime, 1, 6).setValues([[d.time, d.price, d.reason, pnl, best, result]]);
  sh.getRange(r, COL.pnl).setFontColor(pnl > 0 ? '#188038' : pnl < 0 ? '#d93025' : '#5f6368');
  return 'ok';
}

function onSetup_(d) {
  const sh = sheet_(SETUPS, SETUP_HEADERS);
  const price = d.zone !== undefined && d.zone !== null ? d.zone : (d.level_price !== undefined ? d.level_price : '');
  const row = [
    new Date(), d.time, weekOf_(d.time), d.event, d.side, d.setup || '', d.level || '',
    d.event === 'MISSED' ? 'no 1m trigger' : (d.stage || ''), price, d.ct || '',
  ];
  // Setups carry no trade id, so a repeat is the same bar time, event, side, setup, level, stage and price
  const last = sh.getLastRow();
  if (last > 1) {
    const n = Math.min(50, last - 1);
    const key = setupKey_(row.slice(1));
    if (sh.getRange(last - n + 1, 2, n, 8).getValues().some(r => setupKey_(r) === key)) return 'duplicate';
  }
  sh.appendRow(row);
  return 'ok';
}

// Columns B:I of a Setups row (bar time .. price) as one comparable string
function setupKey_(r) {
  const t = r[0] instanceof Date ? Utilities.formatDate(r[0], SpreadsheetApp.getActiveSpreadsheet().getSpreadsheetTimeZone(), 'yyyy-MM-dd H:mm') : String(r[0]).replace(/ 0(\d):/, ' $1:');
  return [t, r[2], r[3], r[4], r[5], r[6], Number(r[7])].join('|');
}

/** Run once from the menu or editor: keeps the first copy of each setup and deletes the repeats. */
function removeDuplicateSetups() {
  const sh = sheet_(SETUPS, SETUP_HEADERS);
  const last = sh.getLastRow();
  if (last < 3) return;
  const rows = sh.getRange(2, 2, last - 1, 8).getValues();
  const seen = {};
  const drop = [];
  rows.forEach((r, i) => {
    const k = setupKey_(r);
    if (seen[k]) drop.push(i + 2);
    seen[k] = true;
  });
  for (let i = drop.length - 1; i >= 0; i--) sh.deleteRow(drop[i]);
  sheet_(LOG, LOG_HEADERS).appendRow([new Date(), 'CLEANUP', '', '', '', 'Removed ' + drop.length + ' duplicate setup rows.']);
}

/** Run once from the editor (select setup > Run) to create the sheets and the summary. */
function setup() {
  sheet_(TRADES, TRADE_HEADERS);
  sheet_(SETUPS, SETUP_HEADERS);
  sheet_(LOG, LOG_HEADERS);
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(SUMMARY) || ss.insertSheet(SUMMARY, 0);
  sh.clear();
  // Trades columns: E Session, F Side, G Setup, H Level, O Exit Time, Q Exit Reason, R P&L $
  const rows = [
    ['Metric', 'Value'],
    ['Closed trades', '=COUNTA(Trades!O2:O)'],
    ['Wins', '=COUNTIF(Trades!R2:R,">0")'],
    ['Losses', '=COUNTIF(Trades!R2:R,"<0")'],
    ['Breakeven', '=COUNTIF(Trades!T2:T,"Breakeven")'],
    ['Win rate', '=IFERROR(B3/B2,0)'],
    ['Net P&L $', '=SUM(Trades!R2:R)'],
    ['Average win $', '=IFERROR(AVERAGEIF(Trades!R2:R,">0"),0)'],
    ['Average loss $', '=IFERROR(AVERAGEIF(Trades!R2:R,"<0"),0)'],
    ['Profit factor', '=IFERROR(SUMIF(Trades!R2:R,">0")/ABS(SUMIF(Trades!R2:R,"<0")),0)'],
    ['Largest win $', '=IFERROR(MAX(Trades!R2:R),0)'],
    ['Largest loss $', '=IFERROR(MIN(Trades!R2:R),0)'],
    ['Average best open $', '=IFERROR(AVERAGE(Trades!S2:S),0)'],
    ['Setups alerted', '=COUNTIF(Setups!D2:D,"SETUP")'],
    ['Setups missed (no 1m trigger)', '=COUNTIF(Setups!D2:D,"MISSED")'],
  ];
  sh.getRange(1, 1, rows.length, 2).setValues(rows);
  sh.getRange('A1:B1').setFontWeight('bold');
  sh.getRange('B6').setNumberFormat('0%');
  ['B7', 'B8', 'B9', 'B11', 'B12', 'B13'].forEach(a => sh.getRange(a).setNumberFormat('$#,##0.00'));
  sh.getRange('B10').setNumberFormat('0.00');

  // Breakdown tables side by side: by week, setup type, level, session, exit reason
  const tables = [
    ['D', 'By week', 'B', 'Week Of', 'order by B desc'],
    ['I', 'By setup type', 'G', 'Setup', 'order by sum(R) desc'],
    ['N', 'By level', 'H', 'Level', 'order by sum(R) desc'],
    ['S', 'By session', 'E', 'Session', 'order by sum(R) desc'],
    ['X', 'By exit reason', 'Q', 'Exit Reason', 'order by count(R) desc'],
  ];
  tables.forEach(([col, title, key, name, order]) => {
    sh.getRange(col + '1').setValue(title).setFontWeight('bold');
    const q = `select ${key}, count(R), sum(R), avg(R) where O is not null group by ${key} ${order} ` +
      `label ${key} '${name}', count(R) 'Trades', sum(R) 'Net $', avg(R) 'Avg $'`;
    sh.getRange(col + '2').setFormula(`=IFERROR(QUERY(Trades!A2:U,"${q}",0),"No closed trades yet")`);
  });
  sh.autoResizeColumns(1, 27);
  const blank = ss.getSheetByName('Sheet1');
  if (blank && blank.getLastRow() === 0 && ss.getSheets().length > 1) ss.deleteSheet(blank);
}

/** Run from the editor to push a fake trade through the sheet without TradingView. */
function testTrade() {
  const id = 'TEST-' + Date.now();
  const post = obj => doPost({ postData: { contents: JSON.stringify(Object.assign({ key: SECRET, symbol: 'ES1!' }, obj)) } });
  post({ event: 'SETUP', id: '', time: '2026-09-25 10:30', side: 'BUY', setup: 'CRT', level: 'NY low', stage: 'armed', zone: 7766.25, ct: 'No' });
  post({ event: 'ENTRY', id: id, time: '2026-09-25 10:34', side: 'BUY', setup: 'CRT', level: 'NY low', session: 'NY AM', ct: 'No', trigger: 'retest', entry: 7767.25, sl: 7762.25, tp1: 7775.25, contracts: 1 });
  post({ event: 'STOP', id: id, time: '2026-09-25 10:40', sl: 7767.25, locked_usd: 0 });
  post({ event: 'EXIT', id: id, time: '2026-09-25 11:50', price: 7788.5, reason: 'TRAIL', pnl_usd: 1062.5, best_usd: 1437.5 });
  post({ event: 'MISSED', id: '', time: '2026-09-25 11:30', side: 'SELL', setup: 'SWEEP', level: 'London', zone: 7781.75 });
}

// Monday of the trade's week (yyyy-MM-dd). Sunday evening futures count as the next week.
function weekOf_(t) {
  const m = String(t || '').match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return '';
  const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
  const day = d.getDay(); // 0 = Sunday
  d.setDate(d.getDate() + (day === 0 ? 1 : 1 - day));
  return Utilities.formatDate(d, Session.getScriptTimeZone(), 'yyyy-MM-dd');
}

function sheet_(name, headers) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

function findRow_(sh, id) {
  if (!id) return 0;
  const cell = sh.getRange('A:A').createTextFinder(String(id)).matchEntireCell(true).findNext();
  return cell ? cell.getRow() : 0;
}

function reply_(text) {
  return ContentService.createTextOutput(text).setMimeType(ContentService.MimeType.TEXT);
}
