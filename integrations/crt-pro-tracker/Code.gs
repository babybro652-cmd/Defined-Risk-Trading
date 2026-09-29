/**
 * CRT Pro Tracker — receives the CRT Pro ES indicator's trade-log alerts
 * (pine/crt-pro-es.pine, "Trade Log (webhook)" section) and records each
 * trade in the "CRT Trade Tracker" Google Sheet.
 *
 * Bind this to that spreadsheet (Extensions > Apps Script inside the sheet),
 * run setup() once, then Deploy > New deployment > Web app, execute as Me,
 * access Anyone. Paste the /exec URL into ONE TradingView alert on the
 * indicator with condition "Any alert() function call". Full steps in
 * README.md next to this file.
 *
 * Payloads (JSON, one per bar close):
 *   ENTRY {id, side, time, entry, sweep_stop, risk_pts, ref_high, ref_low, tf}
 *   EXIT  {id, side, time, exit, reason (EMA | REVERSE), pnl_pts}
 *
 * Duplicates are ignored: an ENTRY whose id is already in the sheet, or an
 * EXIT for a trade that already has one, only goes to the Log tab.
 *
 * It creates its own tabs (CRT Pro Trades / CRT Pro Summary / CRT Pro Log)
 * and never touches the sheet's older tabs.
 */

// Optional shared secret. Leave "" to accept any post, or set it to the same
// value as the indicator's "Webhook Key" input.
var SECRET = "";

var POINT_VALUE = 50;   // ES: $50 per point
var CONTRACTS = 2;      // dollars are shown at 2 ES contracts

var TRADES = "CRT Pro Trades";
var SUMMARY = "CRT Pro Summary";
var LOG = "CRT Pro Log";

var HEADERS = ["Trade ID", "Date", "Entry Time (ET)", "Session", "Side", "Chart TF",
  "Entry", "Sweep Stop", "Risk (pts)", "Exit Time (ET)", "Exit", "Exit Reason",
  "P&L (pts)", "R", "P&L $ (2 ES)", "Result"];
var C = { ID: 1, DATE: 2, ENTRY_TIME: 3, SESSION: 4, SIDE: 5, TF: 6, ENTRY: 7, STOP: 8,
  RISK: 9, EXIT_TIME: 10, EXIT: 11, REASON: 12, PNL_PTS: 13, R: 14, PNL_USD: 15, RESULT: 16 };

function doGet() {
  return ContentService.createTextOutput("CRT Pro tracker is live.");
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    ensureTabs(ss);
    var raw = (e && e.postData && e.postData.contents) || "";
    var body;
    try {
      body = JSON.parse(raw);
    } catch (err) {
      logRow(ss, "NOT JSON", "", raw);
      return json({ ok: false, error: "not json" });
    }
    if (SECRET && body.key !== SECRET) {
      logRow(ss, "BAD KEY", body.id || "", raw);
      return json({ ok: false, error: "unauthorized" });
    }

    var status;
    if (body.event === "ENTRY") status = recordEntry(ss, body);
    else if (body.event === "EXIT") status = recordExit(ss, body);
    else status = "UNKNOWN EVENT";

    logRow(ss, (body.event || "?") + (status === "ok" ? "" : " (" + status + ")"), body.id || "", raw);
    return json({ ok: true, status: status });
  } finally {
    lock.releaseLock();
  }
}

function recordEntry(ss, b) {
  var sh = ss.getSheetByName(TRADES);
  if (findTradeRow(sh, b.id)) return "duplicate";
  var parts = String(b.time || "").split(" ");
  var row = [
    b.id, parts[0] || "", parts[1] || "", sessionFor(parts[1]), b.side, b.tf || "",
    num(b.entry), num(b.sweep_stop), num(b.risk_pts), "", "", "", "", "", "", "OPEN"
  ];
  sh.appendRow(row);
  return "ok";
}

function recordExit(ss, b) {
  var sh = ss.getSheetByName(TRADES);
  var r = findTradeRow(sh, b.id);
  if (!r) return "no matching entry";
  if (sh.getRange(r, C.EXIT).getValue() !== "") return "duplicate";

  var pnl = num(b.pnl_pts);
  var risk = Number(sh.getRange(r, C.RISK).getValue());
  var parts = String(b.time || "").split(" ");
  var rMult = risk > 0 ? Math.round((pnl / risk) * 100) / 100 : "";
  var result = pnl > 0 ? "Win" : pnl < 0 ? "Loss" : "Breakeven";
  sh.getRange(r, C.EXIT_TIME, 1, 7).setValues([[
    parts[1] || "", num(b.exit), b.reason || "", pnl, rMult, pnl * POINT_VALUE * CONTRACTS, result
  ]]);
  return "ok";
}

// Sessions in Eastern time, matching the rest of the DRT logs.
function sessionFor(hhmm) {
  var m = String(hhmm || "").match(/(\d{1,2}):(\d{2})/);
  if (!m) return "";
  var t = Number(m[1]) * 100 + Number(m[2]);
  if (t >= 1900 || t < 300) return "Asia";
  if (t < 930) return "London";
  if (t < 1000) return "NY open (9:30-10)";
  if (t < 1200) return "NY 10-12";
  if (t < 1600) return "NY afternoon";
  return "After hours";
}

function findTradeRow(sh, id) {
  if (!id) return 0;
  var last = sh.getLastRow();
  if (last < 2) return 0;
  var ids = sh.getRange(2, C.ID, last - 1, 1).getValues();
  for (var i = ids.length - 1; i >= 0; i--) {
    if (ids[i][0] === id) return i + 2;
  }
  return 0;
}

function logRow(ss, event, id, raw) {
  var tz = "America/New_York";
  ss.getSheetByName(LOG).appendRow([
    Utilities.formatDate(new Date(), tz, "yyyy-MM-dd HH:mm:ss"), event, id, raw
  ]);
}

function num(v) {
  return (v === undefined || v === null || v === "") ? "" : Number(v);
}

function json(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/** Run once from the editor. Creates the three tabs; safe to run again. */
function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  ensureTabs(ss);
  buildSummary(ss.getSheetByName(SUMMARY));
}

function ensureTabs(ss) {
  var t = ss.getSheetByName(TRADES);
  if (!t) {
    t = ss.insertSheet(TRADES);
    t.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight("bold");
    t.setFrozenRows(1);
  }
  if (!ss.getSheetByName(LOG)) {
    var l = ss.insertSheet(LOG);
    l.getRange(1, 1, 1, 4).setValues([["Received (ET)", "Event", "Trade ID", "Payload"]]).setFontWeight("bold");
    l.setFrozenRows(1);
  }
  if (!ss.getSheetByName(SUMMARY)) {
    buildSummary(ss.insertSheet(SUMMARY));
  }
}

function buildSummary(s) {
  var T = "'" + TRADES + "'!";
  var res = T + "$P$2:$P", ses = T + "$D$2:$D", rr = T + "$N$2:$N", usd = T + "$O$2:$O", pts = T + "$M$2:$M";
  var closed = "COUNTIF(" + res + ",\"Win\")+COUNTIF(" + res + ",\"Loss\")+COUNTIF(" + res + ",\"Breakeven\")";
  var rows = [
    ["CRT Pro — forward test", ""],
    ["", ""],
    ["Closed trades", "=" + closed],
    ["Open trades", "=COUNTIF(" + res + ",\"OPEN\")"],
    ["Wins", "=COUNTIF(" + res + ",\"Win\")"],
    ["Losses", "=COUNTIF(" + res + ",\"Loss\")"],
    ["Breakeven", "=COUNTIF(" + res + ",\"Breakeven\")"],
    ["Win rate", "=IFERROR(B5/B3,0)"],
    ["Total points", "=SUM(" + pts + ")"],
    ["Total R", "=SUM(" + rr + ")"],
    ["Average R per trade", "=IFERROR(B10/B3,0)"],
    ["Total $ (2 ES)", "=SUM(" + usd + ")"],
    ["", ""],
    ["By session (ET)", "Trades", "Total R", "Total $ (2 ES)"]
  ];
  s.clear();
  for (var i = 0; i < rows.length; i++) {
    s.getRange(i + 1, 1, 1, rows[i].length).setValues([rows[i]]);
  }
  var sessions = ["Asia", "London", "NY open (9:30-10)", "NY 10-12", "NY afternoon", "After hours"];
  for (var j = 0; j < sessions.length; j++) {
    var r = 15 + j, name = sessions[j];
    s.getRange(r, 1, 1, 4).setValues([[
      name,
      "=COUNTIFS(" + ses + ",A" + r + "," + res + ",\"<>OPEN\"," + res + ",\"<>\")",
      "=SUMIFS(" + rr + "," + ses + ",A" + r + ")",
      "=SUMIFS(" + usd + "," + ses + ",A" + r + ")"
    ]]);
  }
  s.getRange("A1").setFontWeight("bold").setFontSize(12);
  s.getRange("A14:D14").setFontWeight("bold");
  s.getRange("B8").setNumberFormat("0%");
  s.getRange("B11").setNumberFormat("0.00");
  s.getRange("B12").setNumberFormat("$#,##0");
  s.getRange("D15:D20").setNumberFormat("$#,##0");
}

/** Adds one sample trade so you can see the layout; delete its rows after. */
function addTestTrade() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  ensureTabs(ss);
  recordEntry(ss, { id: "TEST-1", side: "LONG", time: "2026-09-30 10:15", entry: 7800, sweep_stop: 7796, risk_pts: 4, tf: "1" });
  recordExit(ss, { id: "TEST-1", side: "LONG", time: "2026-09-30 10:40", exit: 7808, reason: "EMA", pnl_pts: 8 });
}
