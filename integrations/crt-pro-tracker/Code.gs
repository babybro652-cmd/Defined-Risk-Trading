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
 *   ENTRY {id, side, time, entry, sl, risk_pts, tp1, tp2, tp3, ref_high, ref_low, tf}
 *   TP    {id, side, time, level (TP1 | TP2 | TP3), price}
 *   EXIT  {id, side, time, exit, reason (SL | TP3 | REVERSE | EMA), tp_hits, pnl_pts}
 *
 * Duplicates are ignored: an ENTRY whose id is already in the sheet, or an
 * EXIT for a trade that already has one, only goes to the Log tab.
 *
 * It creates its own tabs (CRT Pro Trades / CRT Pro Summary / CRT Pro Log)
 * and never touches the sheet's older tabs.
 *
 * TEST indicator (pine/crt-pro-vmap-es.pine): payloads with
 * "source":"crt-pro-vmap" go to their own tabs, "CRT Pro VMap" and
 * "CRT Pro VMap Summary", created the first time one arrives (or run
 * setupVmap()). Those ENTRY payloads also carry setup (A | B), poc,
 * dist_to_poc_pts, entry_zone and sweep_zone (poc | shelf | thin | none).
 * Live CRT Pro rows keep going to CRT Pro Trades exactly as before. Both
 * indicators share the CRT Pro Log tab (VMap events are marked "VMAP").
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
  "Entry", "SL", "TP1", "TP2", "TP3", "Risk (pts)", "TP Reached", "Exit Time (ET)", "Exit",
  "Exit Reason", "P&L (pts)", "R", "P&L $ (2 ES)", "Result"];
var C = { ID: 1, DATE: 2, ENTRY_TIME: 3, SESSION: 4, SIDE: 5, TF: 6, ENTRY: 7, STOP: 8,
  TP1: 9, TP2: 10, TP3: 11, RISK: 12, TP_HIT: 13, EXIT_TIME: 14, EXIT: 15, REASON: 16,
  PNL_PTS: 17, R: 18, PNL_USD: 19, RESULT: 20 };

// TEST indicator (CRT Pro + Volume Map). Same columns as above, plus U:Y.
var VMAP_SOURCE = "crt-pro-vmap";
var VMAP_TRADES = "CRT Pro VMap";
var VMAP_SUMMARY = "CRT Pro VMap Summary";
var VMAP_HEADERS = HEADERS.concat(["POC", "Dist to POC", "Entry Zone", "Sweep Zone", "Setup"]);

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

    if (isVmap(body)) ensureVmapTabs(ss);

    var status;
    if (body.event === "ENTRY") status = recordEntry(ss, body);
    else if (body.event === "TP") status = recordTp(ss, body);
    else if (body.event === "EXIT") status = recordExit(ss, body);
    else status = "UNKNOWN EVENT";

    logRow(ss, (isVmap(body) ? "VMAP " : "") + (body.event || "?") + (status === "ok" ? "" : " (" + status + ")"), body.id || "", raw);
    return json({ ok: true, status: status });
  } finally {
    lock.releaseLock();
  }
}

// VMap payloads go to their own tab; everything else to CRT Pro Trades.
function isVmap(b) {
  return b && b.source === VMAP_SOURCE;
}

function tradesTab(b) {
  return isVmap(b) ? VMAP_TRADES : TRADES;
}

function recordEntry(ss, b) {
  var sh = ss.getSheetByName(tradesTab(b));
  if (findTradeRow(sh, b.id)) return "duplicate";
  var parts = String(b.time || "").split(" ");
  var sl = b.sl !== undefined ? b.sl : b.sweep_stop; // sweep_stop = alerts from before the TP update
  var row = [
    b.id, parts[0] || "", parts[1] || "", sessionFor(parts[1]), b.side, b.tf || "",
    num(b.entry), num(sl), num(b.tp1), num(b.tp2), num(b.tp3), num(b.risk_pts), 0,
    "", "", "", "", "", "", "OPEN"
  ];
  if (isVmap(b)) {
    row.push(num(b.poc), num(b.dist_to_poc_pts), b.entry_zone || "", b.sweep_zone || "", b.setup || "");
  }
  sh.appendRow(row);
  return "ok";
}

// Marks the highest TP the open trade has reached (1-3).
function recordTp(ss, b) {
  var sh = ss.getSheetByName(tradesTab(b));
  var r = findTradeRow(sh, b.id);
  if (!r) return "no matching entry";
  if (sh.getRange(r, C.EXIT).getValue() !== "") return "trade already closed";
  var level = Number(String(b.level || "").replace(/\D/g, ""));
  if (!(level > Number(sh.getRange(r, C.TP_HIT).getValue() || 0))) return "duplicate";
  sh.getRange(r, C.TP_HIT).setValue(level);
  return "ok";
}

function recordExit(ss, b) {
  var sh = ss.getSheetByName(tradesTab(b));
  var r = findTradeRow(sh, b.id);
  if (!r) return "no matching entry";
  if (sh.getRange(r, C.EXIT).getValue() !== "") return "duplicate";

  var pnl = num(b.pnl_pts);
  var risk = Number(sh.getRange(r, C.RISK).getValue());
  var parts = String(b.time || "").split(" ");
  var rMult = risk > 0 ? Math.round((pnl / risk) * 100) / 100 : "";
  var result = pnl > 0 ? "Win" : pnl < 0 ? "Loss" : "Breakeven";
  var hits = b.tp_hits !== undefined ? Number(b.tp_hits) : "";
  if (hits !== "" && hits > Number(sh.getRange(r, C.TP_HIT).getValue() || 0)) sh.getRange(r, C.TP_HIT).setValue(hits);
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
  buildSummaryFor(s, TRADES, "CRT Pro — forward test");
}

// Writes the summary block for one trades tab. Returns the first free row.
function buildSummaryFor(s, tradesName, title) {
  var T = "'" + tradesName + "'!";
  var res = T + "$T$2:$T", ses = T + "$D$2:$D", rr = T + "$R$2:$R", usd = T + "$S$2:$S", pts = T + "$Q$2:$Q";
  var tp = T + "$M$2:$M", why = T + "$P$2:$P";
  var closed = "COUNTIF(" + res + ",\"Win\")+COUNTIF(" + res + ",\"Loss\")+COUNTIF(" + res + ",\"Breakeven\")";
  var reached = function (n) { return "=IFERROR(COUNTIFS(" + tp + ",\">=" + n + "\"," + why + ",\"<>\")/B3,0)"; };
  var rows = [
    [title, ""],
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
    ["Reached TP1", reached(1)],
    ["Reached TP2", reached(2)],
    ["Reached TP3", reached(3)],
    ["Exit: SL", "=COUNTIF(" + why + ",\"SL\")"],
    ["Exit: TP3", "=COUNTIF(" + why + ",\"TP3\")"],
    ["Exit: EMA", "=COUNTIF(" + why + ",\"EMA\")"],
    ["Exit: opposite signal", "=COUNTIF(" + why + ",\"REVERSE\")"],
    ["", ""],
    ["By session (ET)", "Trades", "Total R", "Total $ (2 ES)"]
  ];
  s.clear();
  for (var i = 0; i < rows.length; i++) {
    s.getRange(i + 1, 1, 1, rows[i].length).setValues([rows[i]]);
  }
  var first = rows.length + 1;
  var sessions = ["Asia", "London", "NY open (9:30-10)", "NY 10-12", "NY afternoon", "After hours"];
  for (var j = 0; j < sessions.length; j++) {
    var r = first + j, name = sessions[j];
    s.getRange(r, 1, 1, 4).setValues([[
      name,
      "=COUNTIFS(" + ses + ",A" + r + "," + res + ",\"<>OPEN\"," + res + ",\"<>\")",
      "=SUMIFS(" + rr + "," + ses + ",A" + r + ")",
      "=SUMIFS(" + usd + "," + ses + ",A" + r + ")"
    ]]);
  }
  s.getRange("A1").setFontWeight("bold").setFontSize(12);
  s.getRange(rows.length, 1, 1, 4).setFontWeight("bold");
  s.getRange("B8").setNumberFormat("0%");
  s.getRange("B11").setNumberFormat("0.00");
  s.getRange("B12").setNumberFormat("$#,##0");
  s.getRange("B13:B15").setNumberFormat("0%");
  s.getRange(first, 4, sessions.length, 1).setNumberFormat("$#,##0");
  return first + sessions.length + 1;
}

/** Run once from the editor to create the VMap tabs now (they are also created on the first VMap alert). */
function setupVmap() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  ensureVmapTabs(ss);
  buildVmapSummary(ss.getSheetByName(VMAP_SUMMARY));
}

function ensureVmapTabs(ss) {
  var t = ss.getSheetByName(VMAP_TRADES);
  if (!t) {
    t = ss.insertSheet(VMAP_TRADES);
    t.getRange(1, 1, 1, VMAP_HEADERS.length).setValues([VMAP_HEADERS]).setFontWeight("bold");
    t.setFrozenRows(1);
  }
  if (!ss.getSheetByName(VMAP_SUMMARY)) {
    buildVmapSummary(ss.insertSheet(VMAP_SUMMARY));
  }
}

// Same summary as CRT Pro, plus the test result: win rate and R by setup,
// entry zone and sweep zone.
function buildVmapSummary(s) {
  var row = buildSummaryFor(s, VMAP_TRADES, "CRT Pro + Volume Map (TEST) — forward test");
  var T = "'" + VMAP_TRADES + "'!";
  var why = T + "$P$2:$P", setup = T + "$Y$2:$Y";
  s.getRange(row, 1, 1, 2).setValues([["Exit: end of day", "=COUNTIF(" + why + ",\"EOD\")"]]);
  s.getRange(row + 1, 1).setValue("(Exit: TP3 = the final target: untaken session high/low, or the fallback R.)").setFontStyle("italic");
  row += 3;
  row = breakdown(s, row, "By setup", T + "$Y$2:$Y", ["A", "B"], "");
  row = breakdown(s, row, "By entry zone", T + "$W$2:$W", ["poc", "shelf", "thin", "none"], "");
  row = breakdown(s, row, "By sweep zone (setup A)", T + "$X$2:$X", ["poc", "thin", "shelf", "none"], "," + setup + ",\"A\"");
  breakdown(s, row, "Setup A by entry zone", T + "$W$2:$W", ["poc", "shelf", "thin", "none"], "," + setup + ",\"A\"");
}

// One results table: Trades / Wins / Win rate / Avg R / Total R / Total $ per
// value in col. extra = more COUNTIFS/SUMIFS criteria (e.g. setup A only).
function breakdown(s, row, title, col, names, extra) {
  var T = "'" + VMAP_TRADES + "'!";
  var res = T + "$T$2:$T", rr = T + "$R$2:$R", usd = T + "$S$2:$S";
  s.getRange(row, 1, 1, 7).setValues([[title, "Trades", "Wins", "Win rate", "Avg R", "Total R", "Total $ (2 ES)"]]).setFontWeight("bold");
  for (var i = 0; i < names.length; i++) {
    var r = row + 1 + i, key = col + ",A" + r + extra;
    s.getRange(r, 1, 1, 7).setValues([[
      names[i],
      "=COUNTIFS(" + key + "," + res + ",\"<>OPEN\"," + res + ",\"<>\")",
      "=COUNTIFS(" + key + "," + res + ",\"Win\")",
      "=IFERROR(C" + r + "/B" + r + ",0)",
      "=IFERROR(F" + r + "/B" + r + ",0)",
      "=SUMIFS(" + rr + "," + key + ")",
      "=SUMIFS(" + usd + "," + key + ")"
    ]]);
  }
  s.getRange(row + 1, 4, names.length, 1).setNumberFormat("0%");
  s.getRange(row + 1, 5, names.length, 1).setNumberFormat("0.00");
  s.getRange(row + 1, 7, names.length, 1).setNumberFormat("$#,##0");
  return row + names.length + 2;
}

/** Adds one sample trade so you can see the layout; delete its rows after. */
function addTestTrade() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  ensureTabs(ss);
  recordEntry(ss, { id: "TEST-1", side: "LONG", time: "2026-09-30 10:15", entry: 7800, sl: 7796, risk_pts: 4, tp1: 7804, tp2: 7808, tp3: 7812, tf: "1" });
  recordTp(ss, { id: "TEST-1", side: "LONG", time: "2026-09-30 10:22", level: "TP1", price: 7804 });
  recordTp(ss, { id: "TEST-1", side: "LONG", time: "2026-09-30 10:31", level: "TP2", price: 7808 });
  recordExit(ss, { id: "TEST-1", side: "LONG", time: "2026-09-30 10:40", exit: 7809.5, reason: "EMA", tp_hits: 2, pnl_pts: 9.5 });
}

/** Adds one sample VMap trade to the CRT Pro VMap tab; delete its row after. */
function addTestVmapTrade() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  ensureVmapTabs(ss);
  var src = VMAP_SOURCE;
  recordEntry(ss, { source: src, id: "VM-TEST-1", side: "LONG", time: "2026-09-30 10:15", entry: 7738, sl: 7734, risk_pts: 4, tp1: 7741.5, tp2: 7751.75, tp3: 7762, tf: "5", setup: "A", poc: 7742.5, dist_to_poc_pts: -4.5, entry_zone: "shelf", sweep_zone: "thin" });
  recordTp(ss, { source: src, id: "VM-TEST-1", side: "LONG", time: "2026-09-30 10:22", level: "TP1", price: 7741.5 });
  recordExit(ss, { source: src, id: "VM-TEST-1", side: "LONG", time: "2026-09-30 10:40", exit: 7734, reason: "SL", tp_hits: 1, pnl_pts: -4 });
}
