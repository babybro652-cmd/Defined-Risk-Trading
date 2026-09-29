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
  var lastRow = lastSignalRow(sheet);
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

// Per-row formulas for the calculated columns, in R1C1 form so the same text
// works on any row. V4 = tick size, V5:V7 = TP1-3 R multiples (Dashboard).
var FORMULA_TICKS = '=IF(OR(RC7="",RC8=""),"",ROUND(ABS(RC8-RC7)/R4C22,0))';
var FORMULA_R = '=IF(RC15="","",IF(RC15="TP1 HIT",R5C22,IF(RC15="TP2 HIT",R6C22,' +
  'IF(RC15="TP3 HIT",R7C22,IF(RC15="STOPPED",-1,IF(RC15="STOPPED (BE)",0,' +
  'IF(RC15="STOPPED (TRAIL)",R5C22,"")))))))';
var FORMULA_CUM_R = '=SUM(R2C16:RC16)';

// Last row that holds a signal. getLastRow() can't be used: the formula
// columns and the dashboard (columns U:AA) extend past the real data.
function lastSignalRow(sheet) {
  var last = sheet.getLastRow();
  if (last < FIRST_DATA_ROW) return HEADER_ROW;
  var types = sheet.getRange(FIRST_DATA_ROW, COL.SIGNAL_TYPE, last - FIRST_DATA_ROW + 1, 1).getValues();
  for (var i = types.length - 1; i >= 0; i--) {
    if (types[i][0] !== "") return FIRST_DATA_ROW + i;
  }
  return HEADER_ROW;
}

function setRowFormulas(sheet, row) {
  sheet.getRange(row, COL.TICKS).setFormulaR1C1(FORMULA_TICKS);
  sheet.getRange(row, COL.R_ACHIEVED, 1, 2).setFormulasR1C1([[FORMULA_R, FORMULA_CUM_R]]);
}

function appendSignalRow(sheet, body) {
  if (isDuplicateSignal(sheet, body)) return;

  var row = lastSignalRow(sheet) + 1;
  var nextNum = Number(sheet.getRange(row - 1, COL.NUM).getValue()) + 1 || 1;

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

  // Write only the input columns (A:H, J:O, R:S). I, P and Q hold formulas.
  sheet.getRange(row, COL.NUM, 1, COL.ADVERSE_PRICE).setValues([values.slice(0, COL.ADVERSE_PRICE)]);
  sheet.getRange(row, COL.ENTRY, 1, COL.RESULT - COL.ENTRY + 1)
    .setValues([values.slice(COL.ENTRY - 1, COL.RESULT)]);
  sheet.getRange(row, COL.NOTES, 1, 2).setValues([values.slice(COL.NOTES - 1, COL.DIV_VALID_UNTIL)]);
  setRowFormulas(sheet, row);
}

function updateLastOpenTrade(sheet, body) {
  var lastRow = lastSignalRow(sheet);
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
 * One-time repair, run by hand from the Apps Script editor (select
 * fixFormulasAndDashboard, then Run). The template only had formulas and
 * dashboard ranges for rows 2-50, so trades logged below row 50 never got
 * an R value and the dashboard ignored them. This:
 *  1. writes the Ticks of Drawdown, R Achieved and Cumulative R formulas on
 *     every row from 2 down to the last signal, and
 *  2. widens every dashboard range (columns U:AA) from row 50 to row 5000.
 * Only formula cells change; nothing you typed is touched. Safe to re-run.
 */
function fixFormulasAndDashboard() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  var last = lastSignalRow(sheet);
  var fixedRows = 0;
  if (last >= FIRST_DATA_ROW) {
    var n = last - FIRST_DATA_ROW + 1;
    var ticks = [], rCols = [];
    for (var i = 0; i < n; i++) {
      ticks.push([FORMULA_TICKS]);
      rCols.push([FORMULA_R, FORMULA_CUM_R]);
    }
    sheet.getRange(FIRST_DATA_ROW, COL.TICKS, n, 1).setFormulasR1C1(ticks);
    sheet.getRange(FIRST_DATA_ROW, COL.R_ACHIEVED, n, 2).setFormulasR1C1(rCols);
    fixedRows = n;
  }

  var dash = sheet.getRange("U1:AA20");
  var formulas = dash.getFormulas();
  var widened = 0;
  for (var r = 0; r < formulas.length; r++) {
    for (var c = 0; c < formulas[r].length; c++) {
      var f = formulas[r][c];
      if (!f) continue;
      var nf = f.replace(/(\$?[A-Z]{1,2}\$?)50(?!\d)/g, function (m, ref) { return ref + "5000"; });
      if (nf !== f) {
        dash.getCell(r + 1, c + 1).setFormula(nf);
        widened++;
      }
    }
  }
  Logger.log("Formulas written on " + fixedRows + " rows; " + widened + " dashboard formulas widened to row 5000.");
}

/**
 * Rebuilds the Forward Test Dashboard block (U1:AA19) with the template's
 * labels, settings and formulas, covering rows 2-5000. Run by hand if the
 * block gets wiped (deleting whole rows 2-50 deletes it, since it shares
 * those rows with the log). It only writes to U1:AA19, then refreshes the
 * row formulas. Settings go back to the defaults (tick 0.25, TP1-3 = 1/2/3R);
 * change V4:V7 afterwards if you use other values.
 */
function rebuildDashboard() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  var E = "$E$2:$E$5000", I = "$I$2:$I$5000", O = "$O$2:$O$5000", P = "$P$2:$P$5000";
  var trades = "((" + E + "=\"BUY\")+(" + E + "=\"SELL\"))";
  var cnt = function (t) { return "=COUNTIF(" + E + ",\"" + t + "\")"; };
  var avg = function (t) { return "=IFERROR(AVERAGEIFS(" + I + "," + E + ",\"" + t + "\"),\"\")"; };
  var mx = function (cell, t) { return "=IF(" + cell + "=\"\",\"\",MAXIFS(" + I + "," + E + ",\"" + t + "\"))"; };
  var mn = function (cell, t) { return "=IF(" + cell + "=\"\",\"\",MINIFS(" + I + "," + E + ",\"" + t + "\"))"; };

  // Columns U, V, W, X, Y, Z, AA for rows 1-19.
  var block = [
    ["Forward Test Dashboard", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
    ["Settings (edit these)", "", "", "Signal Counts", "", "", ""],
    ["Tick Size", 0.25, "", "Total Signals Logged", "=COUNTA(" + E + ")", "", ""],
    ["TP1 R multiple", 1, "", "BUY", cnt("BUY"), "", ""],
    ["TP2 R multiple", 2, "", "SELL", cnt("SELL"), "", ""],
    ["TP3 R multiple", 3, "", "CRT Bull (unfiltered)", cnt("CRT Bull (unfiltered)"), "", ""],
    ["", "", "", "CRT Bear (unfiltered)", cnt("CRT Bear (unfiltered)"), "", ""],
    ["", "", "", "Bull Div", cnt("Bull Div"), "", ""],
    ["", "", "", "Bear Div", cnt("Bear Div"), "", ""],
    ["", "", "", "", "", "", ""],
    ["BUY/SELL Trade Performance", "", "", "Signal Drawdown Before Follow-Through", "", "", ""],
    ["Closed Trades", "=SUMPRODUCT(" + trades + "*(" + O + "<>\"\")*(" + O + "<>\"WAITING\")*(" + O + "<>\"LIVE\"))", "",
      "Avg Ticks - Bull Div", avg("Bull Div"), "Avg Ticks - CRT Bull", avg("CRT Bull (unfiltered)")],
    ["Wins (TP hit or trailed)", "=SUMPRODUCT(" + trades + "*(ISNUMBER(SEARCH(\"TP\"," + O + "))+(" + O + "=\"STOPPED (TRAIL)\")))", "",
      "Avg Ticks - Bear Div", avg("Bear Div"), "Avg Ticks - CRT Bear", avg("CRT Bear (unfiltered)")],
    ["Breakeven Stops", "=SUMPRODUCT(" + trades + "*(" + O + "=\"STOPPED (BE)\"))", "",
      "Max Ticks - Bull Div", mx("Y13", "Bull Div"), "Max Ticks - CRT Bull", mx("AA13", "CRT Bull (unfiltered)")],
    ["Full Losses", "=SUMPRODUCT(" + trades + "*(" + O + "=\"STOPPED\"))", "",
      "Max Ticks - Bear Div", mx("Y14", "Bear Div"), "Max Ticks - CRT Bear", mx("AA14", "CRT Bear (unfiltered)")],
    ["Win Rate", "=IFERROR(V14/V13,0)", "",
      "Min Ticks - Bull Div", mn("Y13", "Bull Div"), "Min Ticks - CRT Bull", mn("AA13", "CRT Bull (unfiltered)")],
    ["Total R", "=SUM(" + P + ")", "",
      "Min Ticks - Bear Div", mn("Y14", "Bear Div"), "Min Ticks - CRT Bear", mn("AA14", "CRT Bear (unfiltered)")],
    ["Average R per Trade", "=IFERROR(V18/V13,0)", "", "", "", "", ""]
  ];
  sheet.getRange(1, 21, block.length, 7).setValues(block);
  sheet.getRange("V17").setNumberFormat("0%");
  fixFormulasAndDashboard();
  Logger.log("Dashboard rebuilt in U1:AA19.");
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
