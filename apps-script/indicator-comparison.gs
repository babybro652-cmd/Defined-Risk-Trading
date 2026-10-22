/**
 * Indicator Comparison tab (analysis of 10/22/2026).
 * Paste into the CRT Trade Tracker's Apps Script editor as a new file, then run
 * addIndicatorComparison. It creates (or clears and refills) the "Indicator Comparison"
 * tab and touches nothing else. Numbers come from
 * analysis/indicators/indicator-comparison-2026-10-22.md.
 */
function addIndicatorComparison() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName('Indicator Comparison') || ss.insertSheet('Indicator Comparison');
  sh.clear();
  var rows = [
    ['Indicator comparison, 10/22/2026 (1m bar replay; $ = 2 ES net of $10/trade; 4/4 = 4 pt stop, 4 pt target)', '', '', '', '', '', '', '', ''],
    ['Indicator', 'Signals', 'Win %', 'Avg R', 'Total R', '$ 2 ES net', 'Exp $/trade', 'Max DD (R)', 'Best/worst streak'],
    ['CRT Pro ES, actual exits', 702, '23.2%', -0.085, -59.5, -22045, -31, 84.0, '5 / 17'],
    ['CRT Pro ES, 4/4', 702, '48.1%', -0.026, -18.6, -14445, -21, 36.8, '7 / 9'],
    ['CRT Pro VMap, actual', 116, '23.3%', -0.069, -8.0, -4360, -38, 17.0, '3 / 13'],
    ['CRT Pro VMap, 4/4', 116, '43.1%', -0.109, -12.6, -6210, -54, 17.5, '4 / 4'],
    ['CRT + Div BUY/SELL, logged', 48, '31.3%', -0.146, -7.0, '', '', 10.0, '3 / 4'],
    ['CRT + Div BUY/SELL, 4/4', 54, '59.3%', 0.153, 8.3, 2760, 51, 4.0, '4 / 3'],
    ['CRT + Div, Div from label, 4/4', 343, '51.0%', 0.034, 11.8, 1295, 4, 18.9, '5 / 7'],
    ['CRT + Div, CRT tag, 4/4', 106, '42.5%', -0.134, -14.3, -6760, -64, 25.6, '5 / 8'],
    ['CRT Setups', 0, '', '', '', '', '', '', 'no trades logged'],
    ['', '', '', '', '', '', '', '', ''],
    ['10-12 window, 4/4', 'n', 'Win %', '', 'Total R', '$ 2 ES net', '', '', ''],
    ['CRT Pro ES', 88, '44.3%', '', -10.0, -4880, '', '', ''],
    ['CRT Pro VMap', 27, '40.7%', '', -5.0, -2270, '', '', ''],
    ['CRT + Div BUY/SELL', 6, '100%', '', 6.0, 2340, '', '', ''],
    ['Div from label', 24, '58.3%', '', 4.0, 1360, '', '', ''],
    ['CRT tag', 11, '45.5%', '', -1.0, -510, '', '', ''],
    ['', '', '', '', '', '', '', '', ''],
    ['Takeaway: CRT + Div BUY/SELL with a 4/4 bracket is the only result that held in both halves of the data (59% / 59%). Small samples in 10-12.', '', '', '', '', '', '', '', '']
  ];
  sh.getRange(1, 1, rows.length, rows[0].length).setValues(rows);
  sh.getRange('A1').setFontWeight('bold');
  sh.getRange('A2:I2').setFontWeight('bold').setBackground('#e8eaed');
  sh.getRange('A13:I13').setFontWeight('bold').setBackground('#e8eaed');
  sh.getRange('F3:F11').setNumberFormat('$#,##0;-$#,##0');
  sh.getRange('F14:F18').setNumberFormat('$#,##0;-$#,##0');
  sh.setFrozenRows(2);
  sh.autoResizeColumns(1, 9);
}
