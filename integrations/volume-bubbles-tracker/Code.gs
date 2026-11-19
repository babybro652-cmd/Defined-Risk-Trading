/**
 * Volume Bubbles Tracker: receives the Volume Bubbles ES indicator's alert()
 * JSON (pine/volume-bubbles-es.pine, section "5. Alerts (JSON)") and logs one
 * row per event in the "Volume Bubbles Tracker" Google Sheet.
 *
 * Paste this into that sheet's Extensions > Apps Script, Save, run
 * addTestBubble once (approve permissions), then Deploy > New deployment >
 * Web app, Execute as Me, Who has access Anyone. Put the /exec URL in ONE
 * TradingView alert: "Volume Bubbles ES" > "Any alert() function call" >
 * Once per bar close. Full steps in README.md next to this file.
 *
 * Payload (one per event, on bar close):
 *   {"source":"volume-bubbles-es","symbol":"ES1!","tf":"1","type":"vol_hold",
 *    "time":"2026-11-18T10:42","confirmTime":"2026-11-18T10:45","tz":"ET",
 *    "price":7372.25,"volume":13617,"zScore":4.6,"rvol":3.3,"nearHVN":true,
 *    "held":true,"side":"bull","fvg":false,"ifvg":true}
 *   type = bubble | vol_hold | pivot_vol. held / fvg / ifvg are null on bubbles.
 *
 * Tabs it makes (never touches any other tab):
 *   Bubbles Log  one row per event. The outcome columns (MFE / MAE within
 *                30 min, Held Level 30m) stay blank here; the analysis
 *                scripts in analysis/indicators fill them from 1m bars.
 *   Log          every post: OK, DUPLICATE, NOT JSON, OTHER SOURCE, ERROR.
 *
 * Duplicates (same type + time + price in the last 50 rows) are skipped and
 * only noted in Log, so a second alert on the same chart can't double rows.
 */

// Optional shared secret. The indicator has no Webhook Key input, so leave
// this "". If you ever set it, posts must carry the same value as "key".
var SECRET = "";

var SOURCE = "volume-bubbles-es";
var EVENTS = "Bubbles Log";
var LOG = "Log";
var DEDUP_ROWS = 50;

var HEADERS = ["Date ET", "Time ET", "Type", "Side", "Price", "Volume", "zScore", "RVOL",
  "Near HVN", "Held", "FVG", "IFVG", "Symbol", "TF", "Confirm Time ET", "Received",
  "MFE 30m (pts)", "MAE 30m (pts)", "Held Level 30m", "Outcome Notes", "Raw JSON"];
var C = { DATE: 1, TIME: 2, TYPE: 3, SIDE: 4, PRICE: 5, CONFIRM: 15, MFE: 17, RAW: 21 };
var LOG_HEADERS = ["Received", "Status", "Detail", "Raw"];

function doGet() {
  return ContentService.createTextOutput("ok");
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
      logRow(ss, "NOT JSON", "alert must use 'Any alert() function call'", raw);
      return reply({ ok: false, error: "not json" });
    }
    if (!body || typeof body !== "object") {
      logRow(ss, "NOT JSON", "body is not a JSON object", raw);
      return reply({ ok: false, error: "not json" });
    }
    if (SECRET && body.key !== SECRET) {
      logRow(ss, "BAD KEY", "", raw);
      return reply({ ok: false, error: "unauthorized" });
    }
    if (body.source !== SOURCE) {
      logRow(ss, "OTHER SOURCE", String(body.source || "(none)") + " is not " + SOURCE, raw);
      return reply({ ok: false, error: "wrong source" });
    }
    return reply(addEvent(ss, body, raw));
  } catch (err) {
    try {
      logRow(SpreadsheetApp.getActiveSpreadsheet(), "ERROR", String(err), (e && e.postData && e.postData.contents) || "");
    } catch (ignore) {}
    return reply({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function addEvent(ss, b, raw) {
  var sh = ss.getSheetByName(EVENTS);
  var parts = splitTime(b.time);
  var conf = splitTime(b.confirmTime);
  var type = String(b.type || "");
  var price = num(b.price);

  if (isDuplicate(sh, parts.date, parts.time, type, price)) {
    logRow(ss, "DUPLICATE", type + " " + parts.date + " " + parts.time + " @ " + price, raw);
    return { ok: true, duplicate: true };
  }

  var row = [parts.date, parts.time, type, String(b.side || ""), price, num(b.volume),
    num(b.zScore), num(b.rvol), flag(b.nearHVN), flag(b.held), flag(b.fvg), flag(b.ifvg),
    String(b.symbol || ""), String(b.tf || ""), conf.time ? conf.date + " " + conf.time : "",
    new Date(), "", "", "", "", raw];
  sh.appendRow(row);
  logRow(ss, "OK", type + " " + parts.date + " " + parts.time + " @ " + price, "");
  return { ok: true };
}

// Same type + event time + price within the last DEDUP_ROWS rows.
function isDuplicate(sh, date, time, type, price) {
  var last = sh.getLastRow();
  if (last < 2) return false;
  var n = Math.min(DEDUP_ROWS, last - 1);
  var vals = sh.getRange(last - n + 1, 1, n, C.PRICE).getDisplayValues();
  var p = price === "" ? "" : Number(price);
  for (var i = 0; i < vals.length; i++) {
    var r = vals[i];
    var rp = r[C.PRICE - 1] === "" ? "" : Number(String(r[C.PRICE - 1]).replace(/,/g, ""));
    if (r[C.DATE - 1] === date && r[C.TIME - 1] === time && r[C.TYPE - 1] === type && rp === p) return true;
  }
  return false;
}

// "2026-11-18T10:42" -> {date: "2026-11-18", time: "10:42"} (kept as text, already ET)
function splitTime(t) {
  var s = String(t || "");
  var m = s.match(/^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2})/);
  return m ? { date: m[1], time: m[2] } : { date: s, time: "" };
}

function num(v) {
  if (v === null || v === undefined || v === "") return "";
  var n = Number(v);
  return isNaN(n) ? String(v) : n;
}

// true / false stay booleans; null (bubbles have no held/fvg/ifvg) = blank
function flag(v) {
  if (v === true || v === "true") return true;
  if (v === false || v === "false") return false;
  return "";
}

function ensureTabs(ss) {
  var sh = ss.getSheetByName(EVENTS);
  if (!sh) {
    // Reuse the new sheet's empty default tab if it's there
    var first = ss.getSheets()[0];
    if (ss.getSheets().length === 1 && first.getLastRow() === 0 && /^(Sheet1|Hoja 1|Sheet 1)$/.test(first.getName())) {
      sh = first.setName(EVENTS);
    } else {
      sh = ss.insertSheet(EVENTS);
    }
  }
  if (sh.getLastRow() === 0) {
    sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight("bold");
    sh.setFrozenRows(1);
    // Dates and times stay as typed text (ET), so Sheets doesn't shift them
    sh.getRange("A:B").setNumberFormat("@");
    sh.getRange(1, C.CONFIRM, sh.getMaxRows(), 1).setNumberFormat("@");
    sh.getRange(1, C.MFE, 1, 4).setBackground("#fff2cc")
      .setNote("Filled later by the analysis scripts from 1m bars. Leave blank.");
    sh.setColumnWidth(C.RAW, 300);
  }
  var lg = ss.getSheetByName(LOG);
  if (!lg) lg = ss.insertSheet(LOG);
  if (lg.getLastRow() === 0) {
    lg.getRange(1, 1, 1, LOG_HEADERS.length).setValues([LOG_HEADERS]).setFontWeight("bold");
    lg.setFrozenRows(1);
  }
}

function logRow(ss, status, detail, raw) {
  var lg = ss.getSheetByName(LOG) || ss.insertSheet(LOG);
  lg.appendRow([new Date(), status, detail, String(raw).slice(0, 5000)]);
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// Run once from the editor: makes the tabs and adds a sample row marked TEST.
// Delete the TEST row afterwards.
function addTestBubble() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  ensureTabs(ss);
  var now = Utilities.formatDate(new Date(), "America/New_York", "yyyy-MM-dd'T'HH:mm");
  var sample = {
    source: SOURCE, symbol: "TEST", tf: "1", type: "vol_hold", time: now, confirmTime: now,
    tz: "ET", price: 6000.25, volume: 12345, zScore: 4.6, rvol: 3.3, nearHVN: true,
    held: true, side: "bull", fvg: false, ifvg: true
  };
  var res = addEvent(ss, sample, JSON.stringify(sample));
  Logger.log(JSON.stringify(res));
}
