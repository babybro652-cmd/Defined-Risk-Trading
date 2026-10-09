/**
 * Tim Money workbook: adds Vanessa's debt list (10/9) and Together Loans to the plan.
 * Run once from Extensions > Apps Script in the Tim Money workbook.
 *
 * Setup: 4 new bill rows before "Car payment", so the Weeks tab picks them up.
 * Weeks: 4 matching columns, formulas copied from the column to the left.
 */
function addVanessaDebts() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const setup = ss.getSheetByName('Setup');
  const weeks = ss.getSheetByName('Weeks');

  // Safety checks: stop if the layout has changed since 10/9.
  if (setup.getRange('A31').getValue() !== 'Car payment (payroll split)') throw new Error('Setup!A31 is not Car payment; layout changed, stopping.');
  if (setup.getRange('A32').getValue() !== 'Prop firm reset (last one)') throw new Error('Setup!A32 is not Prop firm reset; layout changed, stopping.');
  if (weeks.getRange('Z3').getValue() !== 'Car payment (payroll split)') throw new Error('Weeks!Z3 is not Car payment; layout changed, stopping.');

  // 1. Room for 4 more bills (bill list grows from rows 12-31 to 12-35).
  setup.insertRowsBefore(31, 4);
  weeks.insertColumnsBefore(26, 4); // before column Z
  const n = weeks.getLastRow() - 2;
  weeks.getRange(3, 25, n, 1).copyTo(weeks.getRange(3, 26, n, 4));

  // 2. Bills. Row 19 (Canva, dropped) now holds the prop reset, which sat outside the scheduled list.
  const d = (y, m, day) => new Date(y, m - 1, day);
  setup.getRange('A19:H19').setValues([['Prop firm reset (last one)', 105, 'One-time', d(2026, 10, 15), 'Buy after payday Thu 10/15', '', '', "Tim's final reset (10/9): NY session only. Canva dropped 10/8."]]);
  setup.getRange('A26:H26').setValues([['Together Loans', 172.41, 'Monthly', d(2027, 1, 2), 'Due the 2nd', '', '', 'Balance $1,843.84 (10/9). $327.59 credit covers 11/2 and $155.18 of 12/2, so 12/2 is $17.23 out of pocket (typed in Weeks). Full payment from 1/2.']]);
  setup.getRange('A29:H29').setValues([['Discover', 300, 'Monthly', d(2026, 11, 7), 'Due the 7th', '', '', 'Owed $8,199.95 at 22.99% (Vanessa, 10/9). Current.']]);
  setup.getRange('A31:H34').setValues([
    ['State Employees Credit Union', 100, 'Monthly', d(2026, 10, 31), 'Due the 31st', '', '', 'Owed $1,200 at 10.75% (Vanessa, 10/9). Current.'],
    ['Shell card', 92, 'Monthly', d(2026, 10, 16), 'Due the 16th', '', '', 'Owed $1,645.83 at 32.49% (Vanessa, 10/9). Current.'],
    ['Cash App loans', 100, 'Monthly', d(2026, 11, 15), 'Planning figure, 15th', '', '', 'Owed $3,985 (Vanessa, 10/9). No set payment; $100/mo is a placeholder. Cash App may auto-deduct; check the app.'],
    ['', '', '', '', '', '', '', 'Open row'],
  ]);

  // 3. Old prop reset row (now row 36) is replaced by row 19.
  if (setup.getRange('A36').getValue() === 'Prop firm reset (last one)') setup.getRange('A36:H36').clearContent();

  // 4. Together Loans 12/2 partial payment: week of Thu 11/26, column T.
  const dates = weeks.getRange(4, 1, n - 1, 1).getValues();
  for (let i = 0; i < dates.length; i++) {
    const v = dates[i][0];
    if (v instanceof Date && v.getFullYear() === 2026 && v.getMonth() === 10 && v.getDate() === 26) {
      weeks.getRange(4 + i, 20).setValue(17.23);
    }
  }
  SpreadsheetApp.flush();
}
