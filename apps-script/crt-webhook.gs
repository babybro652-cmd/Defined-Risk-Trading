/**
 * CRT Basic → Google Sheet trade tracker (Google Apps Script)
 *
 * Receives the indicator's JSON webhook alerts and records them:
 *   Trades  — one row per trade (entry, stop, TP1-3, targets hit, exit, P&L, R)
 *   Log     — every alert received, raw
 *   Summary — win rate, net P&L, average R, swept-level vs. not
 *
 * Setup: see apps-script/README.md
 */

// Must match "Webhook Key" in the indicator settings. Leave both empty to skip the check.
const SECRET = 'change-me';

const TRADES = 'Trades';
const LOG = 'Log';
const SUMMARY = 'Summary';

const TRADE_HEADERS = [
  'Trade ID', 'Symbol', 'CRT TF', 'Side', 'Entry Time (NY)', 'Entry', 'Stop', 'TP1', 'TP2', 'TP3',
  'Risk $', 'Swept Level', 'Level Before TP2', 'TP1 Hit', 'TP1 Time (NY)', 'TP2 Hit', 'TP2 Time (NY)',
  'Exit Time (NY)', 'Exit Price', 'Exit Reason', 'P&L $', 'R Multiple', 'Contracts',
];
// 1-based column numbers in the Trades sheet
const COL = {
  id: 1, symbol: 2, ctf: 3, side: 4, entryTime: 5, entry: 6, sl: 7, tp1: 8, tp2: 9, tp3: 10,
  risk: 11, swept: 12, obstacle: 13, tp1Hit: 14, tp1Time: 15, tp2Hit: 16, tp2Time: 17,
  exitTime: 18, exitPrice: 19, reason: 20, pnl: 21, r: 22, contracts: 23,
};
const LOG_HEADERS = ['Received', 'Event', 'Trade ID', 'Symbol', 'Bar Time (NY)', 'Payload'];

/** TradingView sends each alert here as an HTTP POST. */
function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const body = e && e.postData ? e.postData.contents : '';
    let d;
    try {
      d = JSON.parse(body);
    } catch (err) {
      sheet_(LOG, LOG_HEADERS).appendRow([new Date(), 'BAD JSON', '', '', '', body]);
      return reply_('bad json');
    }
    if (SECRET && d.key !== SECRET) return reply_('forbidden');
    delete d.key;

    sheet_(LOG, LOG_HEADERS).appendRow([new Date(), d.event, d.id || '', d.symbol || '', d.time || '', JSON.stringify(d)]);

    if (d.event === 'ENTRY') onEntry_(d);
    else if (d.event === 'TP1' || d.event === 'TP2') onTarget_(d, d.event);
    else if (d.event === 'EXIT') onExit_(d);
    // SKIP events are only logged

    return reply_('ok');
  } finally {
    lock.releaseLock();
  }
}

/** Open the web app URL in a browser to check the deployment is live. */
function doGet() {
  return reply_('CRT webhook is live');
}

function onEntry_(d) {
  const sh = sheet_(TRADES, TRADE_HEADERS);
  if (findRow_(sh, d.id)) return; // duplicate alert
  const row = new Array(TRADE_HEADERS.length).fill('');
  row[COL.id - 1] = d.id;
  row[COL.symbol - 1] = d.symbol;
  row[COL.ctf - 1] = d.ctf;
  row[COL.side - 1] = d.side;
  row[COL.entryTime - 1] = d.time;
  row[COL.entry - 1] = d.entry;
  row[COL.sl - 1] = d.sl;
  row[COL.tp1 - 1] = d.tp1 === null ? '' : d.tp1;
  row[COL.tp2 - 1] = d.tp2;
  row[COL.tp3 - 1] = d.tp3 === null || d.tp3 === undefined ? '' : d.tp3;
  row[COL.risk - 1] = d.risk_usd;
  row[COL.swept - 1] = d.swept;
  row[COL.obstacle - 1] = d.obstacle;
  row[COL.tp1Hit - 1] = d.tp1 === null ? 'n/a' : 'No';
  row[COL.tp2Hit - 1] = 'No';
  row[COL.contracts - 1] = d.contracts;
  sh.appendRow(row);
}

function onTarget_(d, which) {
  const sh = sheet_(TRADES, TRADE_HEADERS);
  const r = findRow_(sh, d.id);
  if (!r) return;
  const hitCol = which === 'TP1' ? COL.tp1Hit : COL.tp2Hit;
  sh.getRange(r, hitCol, 1, 2).setValues([['Yes', d.time]]);
}

function onExit_(d) {
  const sh = sheet_(TRADES, TRADE_HEADERS);
  const r = findRow_(sh, d.id);
  if (!r) return;
  sh.getRange(r, COL.exitTime, 1, 5).setValues([[d.time, d.price, d.reason, d.pnl_usd, d.r_multiple === null ? '' : d.r_multiple]]);
  sh.getRange(r, COL.pnl).setFontColor(d.pnl_usd > 0 ? '#188038' : '#d93025');
  // The final target closes the trade without a separate TP alert
  if ((d.reason === 'TP2' || d.reason === 'TP3') && sh.getRange(r, COL.tp2Hit).getValue() !== 'Yes') {
    sh.getRange(r, COL.tp2Hit, 1, 2).setValues([['Yes', d.time]]);
  }
}

/** Run once from the editor (select setup ▸ Run) to create the sheets and the summary. */
function setup() {
  sheet_(TRADES, TRADE_HEADERS);
  sheet_(LOG, LOG_HEADERS);
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SUMMARY)
    || SpreadsheetApp.getActiveSpreadsheet().insertSheet(SUMMARY);
  sh.clear();
  const rows = [
    ['Metric', 'Value'],
    ['Closed trades', '=COUNTA(Trades!S2:S)'],
    ['Wins', '=COUNTIF(Trades!U2:U,">0")'],
    ['Win rate', '=IFERROR(B3/B2,0)'],
    ['Net P&L $', '=SUM(Trades!U2:U)'],
    ['Average win $', '=IFERROR(AVERAGEIF(Trades!U2:U,">0"),0)'],
    ['Average loss $', '=IFERROR(AVERAGEIF(Trades!U2:U,"<=0"),0)'],
    ['Average R', '=IFERROR(AVERAGE(Trades!V2:V),0)'],
    ['TP1 hit rate', '=IFERROR(COUNTIF(Trades!N2:N,"Yes")/B2,0)'],
    ['TP2 hit rate', '=IFERROR(COUNTIF(Trades!P2:P,"Yes")/B2,0)'],
    ['Stopped out (SL)', '=COUNTIF(Trades!T2:T,"SL")'],
    ['Breakeven (BE)', '=COUNTIF(Trades!T2:T,"BE")'],
    ['Closed at TP2', '=COUNTIF(Trades!T2:T,"TP2")'],
    ['Closed at TP3', '=COUNTIF(Trades!T2:T,"TP3")'],
    ['Win rate — swept a key level', '=IFERROR(COUNTIFS(Trades!L2:L,"?*",Trades!U2:U,">0")/COUNTIFS(Trades!L2:L,"?*",Trades!S2:S,"<>"),0)'],
    ['Win rate — no key level', '=IFERROR(COUNTIFS(Trades!L2:L,"",Trades!U2:U,">0")/COUNTIFS(Trades!L2:L,"",Trades!S2:S,"<>"),0)'],
    ['Net P&L $ — swept a key level', '=SUMIFS(Trades!U2:U,Trades!L2:L,"?*")'],
    ['Net P&L $ — no key level', '=SUMIFS(Trades!U2:U,Trades!L2:L,"",Trades!S2:S,"<>")'],
  ];
  sh.getRange(1, 1, rows.length, 2).setValues(rows);
  sh.getRange('A1:B1').setFontWeight('bold');
  ['B4', 'B9', 'B10', 'B15', 'B16'].forEach(a => sh.getRange(a).setNumberFormat('0%'));
  ['B5', 'B6', 'B7', 'B17', 'B18'].forEach(a => sh.getRange(a).setNumberFormat('$#,##0.00'));
  sh.getRange('B8').setNumberFormat('0.00');
  sh.autoResizeColumns(1, 2);
}

/** Run from the editor to push a fake trade through the sheet without TradingView. */
function testTrade() {
  const id = 'TEST-' + Date.now();
  const post = obj => doPost({ postData: { contents: JSON.stringify(Object.assign({ key: SECRET, symbol: 'ES1!', id: id }, obj)) } });
  post({ event: 'ENTRY', time: '2026-09-23 09:45', ctf: '15', side: 'LONG', entry: 5800.25, sl: 5796.5, tp1: 5804, tp2: 5808.75, tp3: 5813, risk_usd: 187.5, swept: '1H', obstacle: '', contracts: 1 });
  post({ event: 'TP1', time: '2026-09-23 10:00', price: 5804, closed_pct: 50, banked_usd: 93.75, new_sl: 5800.25 });
  post({ event: 'TP2', time: '2026-09-23 10:15', price: 5808.75, closed_pct: 25, banked_usd: 200, new_sl: 5800.25 });
  post({ event: 'EXIT', time: '2026-09-23 10:45', price: 5813, reason: 'TP3', pnl_usd: 359.38, r_multiple: 1.92 });
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
