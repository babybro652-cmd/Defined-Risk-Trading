#!/usr/bin/env python3
"""Print the Sheets batchUpdate requests that format the NHL, NBA or UCL tab (all share one style).

Usage:
  python3 analysis/tab_format.py nhl > /tmp/nhl_fmt.json
  python3 analysis/tab_format.py nba > /tmp/nba_fmt.json
  python3 analysis/tab_format.py ucl > /tmp/ucl_fmt.json

Reads analysis/<sport>/out/sheet_values.json (its `meta` row positions). Pass the printed list as
`requests` to the Sheets connector's update_spreadsheet after the values are written. It first
resets formats and merges. Conditional-format gradients are added each time, so on a rerun delete the
tab's old rules first (deleteConditionalFormatRule, sheetId, index 0, repeated) or skip the grad rules.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET_ID = {'nhl': 9100, 'nba': 9200, 'ucl': 9300}
NAVY = {'red': 0.12156863, 'green': 0.21960784, 'blue': 0.39215687}
SECTION = {'red': 0.8509804, 'green': 0.88235295, 'blue': 0.9490196}
HEADER = {'red': 0.26666668, 'green': 0.32941177, 'blue': 0.41568628}
WHITE = {'red': 1, 'green': 1, 'blue': 1}
GOOD = {'red': 0.7176471, 'green': 0.8784314, 'blue': 0.7294118}
BAD = {'red': 0.9764706, 'green': 0.81960785, 'blue': 0.8}

# section key -> {'pct': [col idx], 'num2': [...], 'num1': [...], 'num3': [...] (.000), 'bold': [...],
#                  'center': [...], 'grad': [col idx, high = green]}
LAYOUT = {
    'nhl': {'a': {'pct': [7, 11, 12], 'num1': [15], 'bold': [12], 'grad': [12]},
            'b': {'pct': [5, 8, 9, 10, 11], 'bold': [9], 'grad': [9]},
            'c': {'pct': [4, 5, 6, 7], 'num1': [2, 3], 'center': [8], 'grad': [4, 5]},
            'd': {'pct': [4, 7, 11], 'num2': [2, 5], 'num1': [3, 6], 'num3': [9, 10], 'grad': [2]}},
    'nba': {'tips': {'pct': [3, 4]},
            'mg': {'pct': [1, 2, 3, 4, 5, 6, 7, 8], 'grad': [2, 4, 6, 8]},
            'mp': {'pct': [3, 5, 6, 7, 8, 10, 12], 'num1': [14, 15], 'bold': [9, 11, 13], 'grad': [8, 10, 12]},
            'a': {'pct': [11, 12, 13, 17, 18], 'grad': [11, 12, 13, 18]},
            'b': {'pct': [6, 9, 10, 11], 'grad': [6, 9]},
            'c': {'pct': [4, 5, 6, 7, 9, 10, 11, 12], 'num1': [2, 3, 8], 'grad': [5, 6, 10, 11]},
            'd': {'pct': [5]}},
    'ucl': {'games': {'pct': [6, 7, 9], 'num2': [2, 3, 4, 5], 'num1': [8]},
            'a': {'pct': [9, 13, 14], 'num2': [10, 11, 12], 'grad': [9, 13]},
            'b': {'pct': [4, 5, 6, 13, 14], 'num2': [2, 3, 8, 9, 11, 12], 'grad': [4, 5]},
            'c': {'pct': [5, 6, 7, 8, 9, 11], 'num2': [2, 3, 4, 10, 13, 14], 'grad': [4, 6, 8]},
            'd': {}},
}


def runs(cols):
    out = []
    for c in sorted(cols):
        if out and out[-1][1] == c:
            out[-1][1] = c + 1
        else:
            out.append([c, c + 1])
    return out


def rng(sid, r0, r1, c0, c1):
    return {'sheetId': sid, 'startRowIndex': r0, 'endRowIndex': r1, 'startColumnIndex': c0, 'endColumnIndex': c1}


def fmt(sid, r0, r1, c0, c1, f, fields):
    return {'repeatCell': {'range': rng(sid, r0, r1, c0, c1), 'cell': {'userEnteredFormat': f}, 'fields': fields}}


def main():
    sport = sys.argv[1].lower()
    sid = SHEET_ID[sport]
    d = json.load(open(os.path.join(HERE, sport, 'out', 'sheet_values.json')))
    meta = d['meta']; rows = d[sport.upper()]; n, w = meta['rows'], meta['width']
    R, C = max(400, n + 20), max(17, w)
    req = [{'unmergeCells': {'range': rng(sid, 0, R, 0, C)}},
           fmt(sid, 0, R, 0, C, {}, 'userEnteredFormat'),
           {'updateSheetProperties': {'properties': {'sheetId': sid, 'gridProperties': {'rowCount': R,
            'columnCount': C, 'frozenRowCount': 1, 'frozenColumnCount': 1}}, 'fields': 'gridProperties'}}]
    req.append(fmt(sid, 0, n, 0, w, {'textFormat': {'fontSize': 10}, 'verticalAlignment': 'TOP'},
                   'userEnteredFormat.textFormat,userEnteredFormat.verticalAlignment'))
    req.append(fmt(sid, 0, 1, 0, w, {'backgroundColor': NAVY, 'textFormat': {'bold': True, 'fontSize': 12,
                   'foregroundColor': WHITE}, 'verticalAlignment': 'TOP'}, 'userEnteredFormat'))
    req.append({'mergeCells': {'range': rng(sid, 1, 2, 1, 10), 'mergeType': 'MERGE_ALL'}})
    req.append(fmt(sid, 1, 2, 0, 10, {'textFormat': {'fontSize': 10, 'italic': True}, 'wrapStrategy': 'WRAP',
                   'verticalAlignment': 'TOP'}, 'userEnteredFormat'))
    req.append({'updateDimensionProperties': {'range': {'sheetId': sid, 'dimension': 'ROWS', 'startIndex': 1, 'endIndex': 2},
                'properties': {'pixelSize': 90}, 'fields': 'pixelSize'}})
    req.append(fmt(sid, 2, 3, 1, 2, {'backgroundColor': {'red': 1, 'green': 1, 'blue': 0}, 'textFormat': {'bold': True,
                   'fontSize': 10, 'foregroundColor': {'red': 0, 'green': 0, 'blue': 1}}}, 'userEnteredFormat'))

    def section(title_row1):          # 1-based row of a section title, header is the next row
        r = title_row1 - 1
        req.append(fmt(sid, r, r + 1, 0, w, {'backgroundColor': SECTION, 'textFormat': {'bold': True, 'fontSize': 10}},
                       'userEnteredFormat.backgroundColor,userEnteredFormat.textFormat'))
        req.append(fmt(sid, r + 1, r + 2, 0, w, {'backgroundColor': HEADER, 'textFormat': {'bold': True, 'fontSize': 10,
                       'foregroundColor': WHITE}, 'wrapStrategy': 'WRAP', 'horizontalAlignment': 'CENTER'},
                       'userEnteredFormat.backgroundColor,userEnteredFormat.textFormat,userEnteredFormat.wrapStrategy,userEnteredFormat.horizontalAlignment'))

    # shortlist block
    s = meta['short']
    section(s)
    p0, p1 = s + 1, s + 1 + meta['n_picks']      # 0-based data rows p0..p1-1
    req.append(fmt(sid, p0, p1, 0, 1, {'textFormat': {'bold': True, 'fontSize': 10}}, 'userEnteredFormat.textFormat'))
    req.append(fmt(sid, p0, p1 + 1, 3, 4, {'wrapStrategy': 'WRAP'}, 'userEnteredFormat.wrapStrategy'))
    req.append(fmt(sid, p1, p1 + 1, 0, 1, {'textFormat': {'bold': True, 'italic': True, 'fontSize': 10}}, 'userEnteredFormat.textFormat'))
    # probable goalies / injuries block (NHL): title row = goalie_hdr - 1, data rows until the blank before 'a'
    if 'goalie_hdr' in meta:
        g = meta['goalie_hdr']
        section(g - 1)
        req.append(fmt(sid, g, meta['a'][0] - 4, 0, 4, {'wrapStrategy': 'WRAP'}, 'userEnteredFormat.wrapStrategy'))
    # all other sections from meta: title row = start - 2
    for key, spec in LAYOUT[sport].items():
        if key not in meta:
            continue
        a, b = meta[key]
        section(a - 2)
        for kind, pattern in (('pct', ('PERCENT', '0%')), ('num2', ('NUMBER', '0.00')), ('num1', ('NUMBER', '0.0')),
                              ('num3', ('NUMBER', '.000'))):
            for c0, c1 in runs(spec.get(kind, [])):
                req.append(fmt(sid, a - 1, b, c0, c1, {'numberFormat': {'type': pattern[0], 'pattern': pattern[1]}},
                               'userEnteredFormat.numberFormat'))
        for c0, c1 in runs(spec.get('bold', [])):
            req.append(fmt(sid, a - 1, b, c0, c1, {'textFormat': {'bold': True, 'fontSize': 10}}, 'userEnteredFormat.textFormat'))
        for c0, c1 in runs(spec.get('center', [])):
            req.append(fmt(sid, a - 1, b, c0, c1, {'horizontalAlignment': 'CENTER'}, 'userEnteredFormat.horizontalAlignment'))
        for c in spec.get('grad', []):
            req.append({'addConditionalFormatRule': {'index': 0, 'rule': {'ranges': [rng(sid, a - 1, b, c, c + 1)],
                        'gradientRule': {'minpoint': {'colorStyle': {'rgbColor': BAD}, 'type': 'MIN'},
                                         'midpoint': {'colorStyle': {'rgbColor': WHITE}, 'type': 'PERCENTILE', 'value': '50'},
                                         'maxpoint': {'colorStyle': {'rgbColor': GOOD}, 'type': 'MAX'}}}}})
    for c0, c1, px in ((0, 1, 170), (1, 2, 150), (2, 3, 110), (3, 4, 260), (4, w, 72)):
        req.append({'updateDimensionProperties': {'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': c0,
                    'endIndex': c1}, 'properties': {'pixelSize': px}, 'fields': 'pixelSize'}})
    print(json.dumps(req))


if __name__ == '__main__':
    main()
