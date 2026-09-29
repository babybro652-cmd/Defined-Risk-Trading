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

// How far back (in rows) to look for an identical signal before appending.
// Duplicate alerts arrive seconds apart, so the last few dozen rows is plenty.
var DEDUPE_LOOKBACK_ROWS = 50;

// Two TradingView alerts pointed at the same /exec URL (or an alert that
// re-fires) post the same SIGNAL more than once. A signal is identified by
// date + time + signal type + its price (entry for BUY/SELL, ref price for
// everything else); if that key is already in the recent rows, skip it.
function signalKey(date, time, signal, price) {
  return [normDate(date), normTime(time), String(signal).trim(), price === "" ? "" : Number(price)].join("|");
}

// The sheet can re-display what the webhook wrote ("00:45" shows as "0:45"),
// so compare dates and times by their numbers, not their text.
function normDate(d) {
  return String(d).replace(/\D/g, "");
}

function normTime(t) {
  var m = String(t).match(/(\d{1,2}):(\d{2})/);
  return m ? Number(m[1]) * 60 + Number(m[2]) : String(t).trim();
}

function isDuplicateSignal(sheet, body) {
  var lastRow = sheet.getLastRow();
  if (lastRow < FIRST_DATA_ROW) return false;
  var start = Math.max(FIRST_DATA_ROW, lastRow - DEDUPE_LOOKBACK_ROWS + 1);
  var rows = sheet.getRange(start, 1, lastRow - start + 1, COL.DIV_VALID_UNTIL).getDisplayValues();
  var isTrade = body.signal === "BUY" || body.signal === "SELL";
  var incoming = signalKey(body.date || "", body.time || "", body.signal || "",
                           numOrBlank(isTrade ? body.entry : body.ref_price));
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i];
    var rowIsTrade = r[COL.SIGNAL_TYPE - 1] === "BUY" || r[COL.SIGNAL_TYPE - 1] === "SELL";
    var price = numOrBlank(rowIsTrade ? r[COL.ENTRY - 1] : r[COL.REF_PRICE - 1]);
    if (signalKey(r[COL.DATE - 1], r[COL.TIME - 1], r[COL.SIGNAL_TYPE - 1], price) === incoming) {
      return true;
    }
  }
  return false;
}

function appendSignalRow(sheet, body) {
  if (isDuplicateSignal(sheet, body)) return;

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

/**
 * One-time cleanup for rows logged before the duplicate check existed.
 * Run it by hand from the Apps Script editor (select removeDuplicateRows,
 * then Run). For each group of identical signals it keeps the first row,
 * moves the latest copy's Result into it (plus any Furthest Adverse Price or
 * Notes only a copy has), deletes the copies, and renumbers column A. Safe to run again:
 * a second run finds nothing to remove.
 */
function removeDuplicateRows() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  var lastRow = sheet.getLastRow();
  if (lastRow < FIRST_DATA_ROW) return;

  var count = lastRow - FIRST_DATA_ROW + 1;
  var rows = sheet.getRange(FIRST_DATA_ROW, 1, count, COL.DIV_VALID_UNTIL).getDisplayValues();
  var firstRowForKey = {};
  var toDelete = [];

  for (var i = 0; i < rows.length; i++) {
    var r = rows[i];
    var signal = r[COL.SIGNAL_TYPE - 1];
    if (!signal) continue;
    var isTrade = signal === "BUY" || signal === "SELL";
    var key = signalKey(r[COL.DATE - 1], r[COL.TIME - 1], signal,
                        numOrBlank(isTrade ? r[COL.ENTRY - 1] : r[COL.REF_PRICE - 1]));

    if (!(key in firstRowForKey)) {
      firstRowForKey[key] = i;
      continue;
    }

    var keep = firstRowForKey[key];
    var keepRow = FIRST_DATA_ROW + keep;
    // The UPDATE handler always wrote to the newest copy, so a later copy's
    // Result is the most current one: it wins.
    if (r[COL.RESULT - 1] && r[COL.RESULT - 1] !== rows[keep][COL.RESULT - 1]) {
      sheet.getRange(keepRow, COL.RESULT).setValue(r[COL.RESULT - 1]);
      rows[keep][COL.RESULT - 1] = r[COL.RESULT - 1];
    }
    if (r[COL.ADVERSE_PRICE - 1] && !rows[keep][COL.ADVERSE_PRICE - 1]) {
      sheet.getRange(keepRow, COL.ADVERSE_PRICE).setValue(Number(r[COL.ADVERSE_PRICE - 1]));
      rows[keep][COL.ADVERSE_PRICE - 1] = r[COL.ADVERSE_PRICE - 1];
    }
    if (r[COL.NOTES - 1] && !rows[keep][COL.NOTES - 1]) {
      sheet.getRange(keepRow, COL.NOTES).setValue(r[COL.NOTES - 1]);
      rows[keep][COL.NOTES - 1] = r[COL.NOTES - 1];
    }
    toDelete.push(FIRST_DATA_ROW + i);
  }

  // Delete from the bottom up so earlier row numbers stay valid.
  for (var d = toDelete.length - 1; d >= 0; d--) {
    sheet.deleteRow(toDelete[d]);
  }

  // Renumber column A on every row that holds a signal.
  var newLast = sheet.getLastRow();
  if (newLast >= FIRST_DATA_ROW) {
    var types = sheet.getRange(FIRST_DATA_ROW, COL.SIGNAL_TYPE, newLast - FIRST_DATA_ROW + 1, 1).getValues();
    var nums = sheet.getRange(FIRST_DATA_ROW, COL.NUM, newLast - FIRST_DATA_ROW + 1, 1).getValues();
    var n = 0;
    for (var j = 0; j < types.length; j++) {
      if (types[j][0]) nums[j][0] = ++n;
    }
    sheet.getRange(FIRST_DATA_ROW, COL.NUM, nums.length, 1).setValues(nums);
  }

  Logger.log("Removed " + toDelete.length + " duplicate rows.");
}

function numOrBlank(v) {
  return (v === undefined || v === null || v === "") ? "" : Number(v);
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
