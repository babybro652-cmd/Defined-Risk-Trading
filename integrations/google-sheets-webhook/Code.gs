/**
 * Receives TradingView webhook POSTs from the CRT-Divergence-SR indicator's
 * alert() calls and writes them into the "CRT Forward Test Log" sheet.
 *
 * Deploy this bound to that spreadsheet (Extensions > Apps Script from
 * inside the sheet itself), then Deploy > New deployment > Web app,
 * execute as "Me", access "Anyone". Paste the resulting /exec URL into a
 * single TradingView alert set to condition "Any alert() function call",
 * webhook URL enabled, on the CRT-Divergence-SR indicator.
 *
 * Two message shapes are handled, matching the two alert() payload types
 * the indicator sends:
 *
 *   SIGNAL - a brand new row (BUY, SELL, CRT Bull/Bear (unfiltered),
 *   Bull/Bear Div). Column layout matches the sheet exactly:
 *     A # | B Date | C Time | D Instrument | E Signal Type | F Direction |
 *     G Signal Ref Price | H Furthest Adverse Price | I Ticks of Drawdown
 *     (formula, untouched) | J Entry | K SL | L TP1 | M TP2 | N TP3 |
 *     O Result | P R Achieved (formula) | Q Cumulative R (formula) | R Notes |
 *     S Div Valid Until (Bull/Bear Div rows only - the last bar the pivot
 *     still counts as "recent" for confluence; any drawdown checked after
 *     this belongs to a different move, not this signal)
 *
 *   UPDATE - a TP/SL hit on the currently open trade. Finds the most
 *   recent row whose Signal Type is BUY or SELL and overwrites its
 *   Result cell. Safe because a new SIGNAL row for BUY/SELL only ever
 *   appears when a fresh confluence signal fires, so every UPDATE
 *   between two such rows necessarily belongs to the same open trade.
 */

var COL = {
  NUM: 1, DATE: 2, TIME: 3, INSTRUMENT: 4, SIGNAL_TYPE: 5, DIRECTION: 6,
  REF_PRICE: 7, ADVERSE_PRICE: 8, TICKS: 9, ENTRY: 10, SL: 11,
  TP1: 12, TP2: 13, TP3: 14, RESULT: 15, R_ACHIEVED: 16,
  CUMULATIVE_R: 17, NOTES: 18, DIV_VALID_UNTIL: 19
};

var HEADER_ROW = 1;
var FIRST_DATA_ROW = 2;

function doGet(e) {
  return ContentService.createTextOutput("CRT forward-test webhook is running.")
    .setMimeType(ContentService.MimeType.TEXT);
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    var body = JSON.parse(e.postData.contents);

    var expectedSecret = PropertiesService.getScriptProperties().getProperty("WEBHOOK_SECRET");
    if (expectedSecret && body.secret !== expectedSecret) {
      return jsonResponse({ ok: false, error: "unauthorized" });
    }

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];

    if (body.type === "SIGNAL") {
      appendSignalRow(sheet, body);
    } else if (body.type === "UPDATE") {
      updateLastOpenTrade(sheet, body);
    } else {
      return jsonResponse({ ok: false, error: "unknown type: " + body.type });
    }

    return jsonResponse({ ok: true });
  } catch (err) {
    return jsonResponse({ ok: false, error: err.message });
  } finally {
    lock.releaseLock();
  }
}

function appendSignalRow(sheet, body) {
  var lastRow = sheet.getLastRow();
  var row = lastRow < HEADER_ROW ? FIRST_DATA_ROW : lastRow + 1;
  var nextNum = row - FIRST_DATA_ROW + 1;

  var values = new Array(COL.DIV_VALID_UNTIL).fill("");
  values[COL.NUM - 1] = nextNum;
  values[COL.DATE - 1] = body.date || "";
  values[COL.TIME - 1] = body.time || "";
  values[COL.INSTRUMENT - 1] = body.ticker || "";
  values[COL.SIGNAL_TYPE - 1] = body.signal || "";

  if (body.signal === "BUY" || body.signal === "SELL") {
    values[COL.DIRECTION - 1] = body.direction || "";
    values[COL.ENTRY - 1] = numOrBlank(body.entry);
    values[COL.SL - 1] = numOrBlank(body.sl);
    values[COL.TP1 - 1] = numOrBlank(body.tp1);
    values[COL.TP2 - 1] = numOrBlank(body.tp2);
    values[COL.TP3 - 1] = numOrBlank(body.tp3);
  } else {
    // CRT Bull/Bear (unfiltered), Bull Div, Bear Div - only the reference
    // price is known at signal time. Furthest Adverse Price is filled in
    // later once you can see what price actually did.
    values[COL.REF_PRICE - 1] = numOrBlank(body.ref_price);
    if (body.valid_until_date || body.valid_until_time) {
      values[COL.DIV_VALID_UNTIL - 1] = (body.valid_until_date || "") + " " + (body.valid_until_time || "");
    }
  }

  sheet.getRange(row, 1, 1, COL.DIV_VALID_UNTIL).setValues([values]);
}

function updateLastOpenTrade(sheet, body) {
  var lastRow = sheet.getLastRow();
  if (lastRow < FIRST_DATA_ROW) return;

  var signalTypes = sheet.getRange(FIRST_DATA_ROW, COL.SIGNAL_TYPE, lastRow - FIRST_DATA_ROW + 1, 1).getValues();
  for (var i = signalTypes.length - 1; i >= 0; i--) {
    var value = signalTypes[i][0];
    if (value === "BUY" || value === "SELL") {
      var targetRow = FIRST_DATA_ROW + i;
      sheet.getRange(targetRow, COL.RESULT).setValue(body.result || "");
      return;
    }
  }
}

function numOrBlank(v) {
  return (v === undefined || v === null || v === "") ? "" : Number(v);
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
