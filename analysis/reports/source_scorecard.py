"""Source scorecard (11/12/26): ours vs StarTool vs @NBAFirstBasket vs Tip-off Projections.

Graded NBA dates 11/4 to 11/12 with external sources logged. Results come from
analysis/nba/data/games_2026-27.json (tip winner, game first points) and opening_2026-27.json
(each team's first points, FT included). Our picks come from the last fb_candidates.json /
shortlist.md committed for each date (after lineup reruns). External picks are transcribed from
the logged cards (out/startool/*.md, star_bomb.txt, out/cheatsheet/*.md and the fb-card images,
tipproj_log.csv). A pick who did not play is dropped and the next name moves up.
Run: python3 analysis/reports/source_scorecard.py
"""
import csv, json, re, subprocess, collections, unicodedata

R = '/home/user/Defined-Risk-Trading'
COMMITS = {'2026-11-04': 'ea0de84', '2026-11-05': 'a3b7043', '2026-11-06': '9799f9f', '2026-11-07': '08379c3',
           '2026-11-08': 'eceed10', '2026-11-09': '3a8cef7', '2026-11-11': '5810317', '2026-11-12': 'f2dbf81'}


def norm(n):
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower()
    n = re.sub(r'\b(jr|sr|iii|ii)\b\.?', '', n)
    return re.sub(r'[^a-z ]', '', n).split()[-1] + ':' + n.strip()[0]


def show(c, p):
    return subprocess.run(['git', '-C', R, 'show', f'{c}:{p}'], capture_output=True, text=True).stdout


games = json.load(open(R + '/analysis/nba/data/games_2026-27.json'))
games = list(games.values()) if isinstance(games, dict) else games
opening = json.load(open(R + '/analysis/nba/data/opening_2026-27.json'))
G = {}
for g in games:
    if isinstance(g, dict) and g.get('date') in COMMITS:
        played = {norm(g['nm'][p[0]]) for p in g['pl'] if p[0] in g['nm']}
        tp = {t: norm(g['nm'].get(p, '?')) for t, p in opening.get(g['id'], {}).get('tp', {}).items()}
        G[(g['date'], g['away'], g['home'])] = dict(tipw=g['tip'].get('w'), fp=norm(g['nm'][g['fp'][0]]),
                                                    fpteam=g['fp'][1], tp=tp, played=played)


def gkey(d, a, h):
    k = (d, a, h)
    if k not in G:
        raise KeyError(k)
    return k


# ---------- ours ----------
OURS_TIP, OURS = {}, {}   # (d,a,h) -> team ; (d,team) -> [(name, p)]
for d, c in COMMITS.items():
    for m in re.finditer(r'- (\S+) @ (\S+) [\d:]+ ET: .*?away wins tip (\d+)%', show(c, 'analysis/nba/out/shortlist.md')):
        a, h, p = m.group(1), m.group(2), int(m.group(3))
        if p != 50:
            OURS_TIP[(d, a, h)] = a if p > 50 else h
    for r in json.loads(show(c, 'analysis/nba/out/fb_candidates.json')):
        if r.get('inj') == 'Out':
            continue
        OURS.setdefault((d, r['tm']), []).append((r['player'], r['p_v2'], r['p_v2']))

# ---------- StarTool ----------
# tip: (away %, home %) team last-8 rates (11/11 matchup-based); equal = no call
ST_TIP = {
 '2026-11-04': {('PHI','DET'):(63,38),('ATL','WSH'):(38,75),('MIL','BOS'):(25,63),('CHA','BKN'):(13,50),('CHI','NY'):(38,63),
                ('IND','MEM'):(38,50),('UTAH','NO'):(13,13),('CLE','OKC'):(63,63),('MIN','HOU'):(38,63),('TOR','DEN'):(63,50),
                ('POR','PHX'):(88,63),('DAL','SA'):(25,100),('LAL','SAC'):(63,50),('MIA','LAC'):(100,13)},
 '2026-11-05': {('ORL','PHX'):(75,50),('MIA','GS'):(100,25)},
 '2026-11-06': {('WSH','ATL'):(63,50),('BOS','CHA'):(63,25),('PHI','CLE'):(63,75),('UTAH','DAL'):(25,38),('OKC','MEM'):(50,50),
                ('TOR','MIL'):(63,38),('MIN','NO'):(50,13),('POR','LAL'):(88,63),('SA','SAC'):(88,50)},
 '2026-11-07': {('DEN','IND'):(38,25),('BKN','ATL'):(50,38),('NY','CLE'):(63,75),('WSH','OKC'):(75,50),('ORL','GS'):(75,25),
                ('HOU','PHX'):(50,50),('SA','POR'):(88,75)},
 '2026-11-08': {('PHI','CHI'):(63,25),('LAL','DET'):(63,25),('UTAH','MIN'):(25,50),('BKN','DAL'):(38,50),('BOS','MIL'):(50,25),
                ('NO','LAC'):(25,13),('MIA','SAC'):(100,38)},
 '2026-11-09': {('LAL','ATL'):(50,50),('CLE','CHA'):(88,38),('WSH','DET'):(63,38),('MEM','TOR'):(50,63),('IND','DAL'):(25,50),
                ('DEN','HOU'):(38,63),('SA','PHX'):(88,50),('NO','GS'):(25,25)},
 '2026-11-11': {('WSH','IND'):(46,54),('CLE','NY'):(77,23),('BOS','TOR'):(39,61),('SA','CHI'):(76,24),('DEN','MEM'):(46,54),
                ('LAL','MIL'):(58,42),('BKN','NO'):(59,41),('ORL','UTAH'):(79,21),('GS','HOU'):(36,64),('OKC','POR'):(34,66)},
 '2026-11-12': {('TOR','PHI'):(67,33),('DAL','MIN'):(36,64),('CHA','PHX'):(59,41)},   # DET @ WSH card did not load
}
# team top 2 = star, bomb (star_bomb.txt), no % -> p None; 11/9 and 11/11 with printed model %
ST = {}
for line in open(R + '/analysis/nba/out/startool/star_bomb.txt'):
    d, game, stars, bombs = line.rstrip('\n').split('|')[:4]
    if d not in COMMITS or d in ('2026-11-11', '2026-11-12'):
        continue
    a, h = [x.strip() for x in game.split('@')]
    s, b = stars.split(','), (bombs.split(',') if bombs else ['', ''])
    for tm, i in ((a, 0), (h, 1)):
        ST[(d, tm)] = [(n, None, None) for n in (s[i], b[i]) if n]
ST_PCT_0911 = {'LAL': [('Austin Reaves',18),('Walker Kessler',11)], 'ATL': [('Nickeil Alexander-Walker',14),('Jalen Johnson',14)],
    'CLE': [('Donovan Mitchell',13),('James Harden',12)], 'CHA': [('Brandon Miller',14),('Grayson Allen',11)],
    'WSH': [('Anthony Davis',13),('Trae Young',10)], 'DET': [('Cade Cunningham',17),('Duncan Robinson',10)],
    'MEM': [('Ty Jerome',16),('Cameron Boozer',10)], 'TOR': [('RJ Barrett',13),('Immanuel Quickley',12)],
    'IND': [('Pascal Siakam',16),('Andrew Nembhard',12)], 'DAL': [('Kyrie Irving',14),('Cooper Flagg',14)],
    'DEN': [('Nikola Jokic',15),('Jamal Murray',14)], 'HOU': [('Kevin Durant',13),('Alperen Sengun',11)],
    'SA': [('Victor Wembanyama',15),("De'Aaron Fox",10)], 'PHX': [('Devin Booker',14),('Dillon Brooks',11)],
    'NO': [('Trey Murphy III',14),('Zion Williamson',13)], 'GS': [('Stephen Curry',17),('Yaxel Lendeborg',13)]}
ST_PCT_1111 = {'WSH': [('Anthony Davis',8),('AJ Dybantsa',6),('Trae Young',6),('Alex Sarr',5),('Kyshawn George',5)],
    'IND': [('Pascal Siakam',23),('Andrew Nembhard',16),('Aaron Nesmith',13),('Ivica Zubac',13),('Ben Smith',4)],
    'CLE': [('Donovan Mitchell',15),('James Harden',13),('Evan Mobley',10),('Jarrett Allen',9),('Peyton Watson',9)],
    'NY': [('Jalen Brunson',13),('Karl-Anthony Towns',10),('OG Anunoby',9),('Mikal Bridges',7),('Landry Shamet',5)],
    'BOS': [('Jayson Tatum',19),('Paul George',14),('Derrick White',12),('Neemias Queta',8),('Mike Conley',3)],
    'TOR': [('RJ Barrett',17),('Jakob Poeltl',9),("Ja'Kobe Walter",8),('Jamal Shead',6),('Kyle Anderson',5)],
    'SA': [('Victor Wembanyama',19),("De'Aaron Fox",12),('Stephon Castle',12),('Devin Vassell',10),('Dylan Harper',10)],
    'CHI': [('Caleb Wilson',9),('Norman Powell',9),('Josh Giddey',7),('Matas Buzelis',7),('Nic Claxton',5)],
    'DEN': [('Nikola Jokic',16),('Jamal Murray',15),('Aaron Gordon',8),('Cameron Johnson',7),('Christian Braun',7)],
    'MEM': [('Ty Jerome',15),('Cameron Boozer',10),('Cedric Coward',8),('Jaylen Wells',8),('Zach Edey',5)],
    'LAL': [('Luka Doncic',18),('Austin Reaves',12),('Walker Kessler',8),('Quentin Grimes',6),('Matisse Thybulle',3)],
    'MIL': [('Ryan Rollins',13),('Jaime Jaquez Jr.',12),('Kyle Kuzma',10),('Myles Turner',9),('Brayden Burries',8)],
    'BKN': [('Michael Porter Jr.',15),('Julius Randle',13),('Nolan Traore',7),('Ziaire Wolf',6),("Day'Ron Sharpe",6)],
    'NO': [('Saddiq Bey',16),('Jeremiah Fears',13),('Dejounte Murray',12),('Herbert Jones',7),('Karlo Matkovic',6)],
    'ORL': [('Desmond Bane',14),('Franz Wagner',14),('Anthony Black',11),('Wendell Carter Jr.',8),('Jase Richardson',3)],
    'UTAH': [('Darryn Peterson',17),('Ace Bailey',16),('Jaxson Hayes',9),('Jalen Green',4),('Kevin Okogie',4)],
    'GS': [('Stephen Curry',15),('Yaxel Lendeborg',12),('Brandin Podziemski',8),('Gui Santos',5),('Draymond Green',4)],
    'HOU': [('Kevin Durant',15),('Alperen Sengun',12),('Amen Thompson',11),('Jabari Smith Jr.',10)],
    'OKC': [('Shai Gilgeous-Alexander',23),('Ajay Mitchell',10),('Jared McCain',7),('Isaiah Hartenstein',6),('Kenrich Williams',5)],
    'POR': [('Deni Avdija',14),('Damian Lillard',12),('Donovan Clingan',8),('Scoot Henderson',8),('Toumani Camara',8)]}
ST_PCT_1112 = {  # DET @ WSH card did not load
    'TOR': [('RJ Barrett',13),('Immanuel Quickley',12),('Jakob Poeltl',7),('Collin Murray-Boyles',6),("Ja'Kobe Walter",6)],
    'PHI': [('Jaylen Brown',13),('Joel Embiid',13),('Tyrese Maxey',13),('LeBron James',10),('VJ Edgecombe',8)],
    'DAL': [('Cooper Flagg',14),('Kyrie Irving',14),('P.J. Washington',8),('Daniel Gafford',6),('Caleb Martin',2)],
    'MIN': [('LaMelo Ball',15),('Ayo Dosunmu',12),('Jaden McDaniels',11),('Jonathan Kuminga',9),('Rudy Gobert',8)],
    'CHA': [('Coby White',16),('Grayson Allen',16),('Naz Reid',15),('Ryan Kalkbrenner',7),('Sion James',5)],
    'PHX': [('Devin Booker',12),('Dillon Brooks',9),('Jalen Green',8),('Miles Bridges',8),('Oso Ighodaro',3)]}
for d, tab in (('2026-11-09', ST_PCT_0911), ('2026-11-11', ST_PCT_1111), ('2026-11-12', ST_PCT_1112)):
    for tm, v in tab.items():
        ST[(d, tm)] = [(n, p, p) for n, p in v]   # StarTool prints game first basket %; same number ranks team and game

# ---------- @NBAFirstBasket ----------
SH_TIP = {  # normalized favorite; None = even
 '2026-11-05': {('ORL','PHX'):None,('MIA','GS'):'MIA'},
 '2026-11-06': {('WSH','ATL'):'WSH',('BOS','CHA'):'BOS',('PHI','CLE'):'CLE',('UTAH','DAL'):'UTAH',('OKC','MEM'):'MEM',
                ('TOR','MIL'):'TOR',('MIN','NO'):'MIN',('POR','LAL'):'LAL',('SA','SAC'):'SA'},
 '2026-11-07': {('DEN','IND'):'DEN',('BKN','ATL'):'ATL',('NY','CLE'):'CLE',('WSH','OKC'):None,('ORL','GS'):'ORL',
                ('HOU','PHX'):'PHX',('SA','POR'):'SA'},
 '2026-11-08': {('PHI','CHI'):'PHI',('LAL','DET'):'LAL',('UTAH','MIN'):'MIN',('BKN','DAL'):'DAL',('BOS','MIL'):'BOS',
                ('NO','LAC'):'LAC',('MIA','SAC'):'MIA'},
 '2026-11-09': {('IND','DAL'):'IND',('DEN','HOU'):'DEN',('SA','PHX'):'SA',('NO','GS'):None},
 '2026-11-11': {('WSH','IND'):'WSH',('CLE','NY'):'CLE',('BOS','TOR'):'TOR',('SA','CHI'):'SA',('DEN','MEM'):'MEM',
                ('LAL','MIL'):'LAL',('BKN','NO'):'BKN',('ORL','UTAH'):'ORL',('GS','HOU'):'HOU',('OKC','POR'):'POR'},
 '2026-11-12': {('TOR','PHI'):'TOR',('DET','WSH'):'WSH',('DAL','MIN'):'MIN',('CHA','PHX'):'PHX'},
}
# fb cards: team -> "Name bsk/gm; ..." (1st Bsk = share of team's first baskets, 1st Gm = game first basket)
SH_RAW = {
 '2026-11-05': {'ORL': "Wendell Carter Jr. 24/-; Desmond Bane 23/-; Franz Wagner 22/-; Anthony Black 14/-",
                'PHX': "Jalen Green 28/-; Devin Booker 27/-; Dillon Brooks 22/-; Khaman Maluach 14/-",
                'MIA': "Giannis Antetokounmpo 34/-; Bam Adebayo 32/-; Andrew Wiggins 14/-; Klay Thompson 13/-",
                'GS': "Stephen Curry 22/-; Brandin Podziemski 22/-; Draymond Green 20/-; Yaxel Lendeborg 13/-"},
 '2026-11-06': {
  'WSH': "Trae Young 9/5; Kyshawn George 16/7; AJ Dybantsa 67/33; Anthony Davis 22/11; Alex Sarr 20/11",
  'ATL': "Nickeil Alexander-Walker 22/11; Dyson Daniels 13/7; Luguentz Dort 25/12; Onyeka Okongwu 22/10",
  'BOS': "Derrick White 19/8; Paul George 27/18; Jayson Tatum 21/10",
  'CHA': "Coby White 19/11; Sion James 4/0; Brandon Miller 33/16; Naz Reid 18/9",
  'PHI': "Tyrese Maxey 21/13; VJ Edgecombe 13/4; Jaylen Brown 28/15; LeBron James 22/14; Joel Embiid 37/22",
  'CLE': "James Harden 14/8; Donovan Mitchell 20/9; Peyton Watson 13/2; Evan Mobley 31/19; Jarrett Allen 35/27",
  'MIN': "LaMelo Ball 25/13; Ayo Dosunmu 4/0; Jonathan Kuminga 5/0; Jaden McDaniels 16/12; Rudy Gobert 22/9",
  'NO': "Dejounte Murray 22/11; Jeremiah Fears 20/12; Trey Murphy III 19/10; Zion Williamson 21/13; Karlo Matkovic 0/0",
  'UTAH': "Keyonte George 26/13; Darryn Peterson 14/0; Ace Bailey 21/12; Lauri Markkanen 27/19; Jaxson Hayes 15/8",
  'DAL': "Kyrie Irving 0/0; Max Christie 23/9; Cooper Flagg 24/8; P.J. Washington 20/10; Daniel Gafford 22/16",
  'TOR': "Immanuel Quickley 19/6; RJ Barrett 20/13; Ja'Kobe Walter 10/7; Scottie Barnes 17/10; Jakob Poeltl 16/5",
  'MIL': "Tyler Herro 19/14; Jaime Jaquez Jr. 50/25; Kyle Kuzma 14/8; Myles Turner 15/4",
  'OKC': "Shai Gilgeous-Alexander 14/7; Ajay Mitchell 22/7; Kenrich Williams 0/0; Isaiah Hartenstein 22/7",
  'MEM': "Ty Jerome 29/10; Cedric Coward 21/9; Jaylen Wells 20/7; Cameron Boozer 29/0; Zach Edey 18/18",
  'POR': "Damian Lillard 17/17; Scoot Henderson 22/11; Toumani Camara 13/5; Deni Avdija 31/12; Donovan Clingan 18/9",
  'LAL': "Luka Doncic 35/15; Austin Reaves 21/16; Ziaire Williams 12/0; Matisse Thybulle 25/12; Walker Kessler 15/15",
  'SA': "De'Aaron Fox 19/14; Stephon Castle 20/11; Dylan Harper 8/0; Devin Vassell 23/14; Victor Wembanyama 42/29",
  'SAC': "Darius Acuff Jr. 14/0; Zach LaVine 25/11; De'Andre Hunter 28/25; Precious Achiuwa 15/8; Domantas Sabonis 32/14"},
 '2026-11-07': {
  'DEN': "Jamal Murray 31/23; Christian Braun 0/0; Cameron Johnson 17/11; Aaron Gordon 21/12; Nikola Jokic 31/14",
  'IND': "Andrew Nembhard 22/9; Kelly Oubre Jr. 19/16; Aaron Nesmith 19/6; Pascal Siakam 27/14; Ivica Zubac 35/10",
  'BKN': "Nolan Traore 19/8; Michael Porter Jr. 38/20; Chaney Johnson 0/0; Julius Randle 19/11; Day'Ron Sharpe 33/13",
  'ATL': "Kingston Flemings 50/50; Nickeil Alexander-Walker 23/11; Dyson Daniels 13/7; Jalen Johnson 18/7; Onyeka Okongwu 22/10",
  'NY': "Jalen Brunson 28/21; Mikal Bridges 19/8; Landry Shamet 23/15; OG Anunoby 17/8; Karl-Anthony Towns 20/13",
  'CLE': "James Harden 13/8; Donovan Mitchell 21/9; Peyton Watson 13/2; Evan Mobley 30/19; Jarrett Allen 34/27",
  'WSH': "Trae Young 8/4; Kyshawn George 16/7; AJ Dybantsa 40/20; Anthony Davis 25/11; Alex Sarr 21/11",
  'OKC': "Shai Gilgeous-Alexander 14/7; Ajay Mitchell 21/7; Kenrich Williams 13/13; Isaiah Hartenstein 21/7",
  'ORL': "Jase Richardson 0/0; Anthony Black 14/5; Desmond Bane 23/10; Franz Wagner 24/13; Wendell Carter Jr. 24/16",
  'GS': "Stephen Curry 22/10; Brandin Podziemski 21/12; Yaxel Lendeborg 11/0; Gui Santos 6/6; Draymond Green 19/10",
  'HOU': "Fred VanVleet 29/14; Amen Thompson 20/7; Kevin Durant 19/10; Jabari Smith Jr. 13/7; Alperen Sengun 26/14",
  'PHX': "Devin Booker 28/14; Jalen Green 28/13; Dillon Brooks 22/9; Miles Bridges 9/6; Khaman Maluach 14/14",
  'SA': "De'Aaron Fox 19/15; Stephon Castle 20/11; Dylan Harper 7/0; Devin Vassell 22/13; Victor Wembanyama 42/29",
  'POR': "Damian Lillard 25/25; Scoot Henderson 20/10; Toumani Camara 13/5; Deni Avdija 31/11; Donovan Clingan 18/9"},
 '2026-11-08': {
  'PHI': "Tyrese Maxey 21/13; VJ Edgecombe 14/5; Jaylen Brown 29/15; LeBron James 22/14; Joel Embiid 36/21",
  'CHI': "Josh Giddey 17/3; Norman Powell 22/10; Matas Buzelis 25/7; Caleb Wilson 38/0; Jalen Smith 34/7",
  'LAL': "Luka Doncic 36/16; Austin Reaves 20/15; Ziaire Williams 12/0; Matisse Thybulle 20/10; Walker Kessler 13/13",
  'DET': "Cade Cunningham 16/8; Duncan Robinson 14/7; Ausar Thompson 14/5; John Collins 28/14; Paul Reed 35/18",
  'UTAH': "Keyonte George 25/13; Darryn Peterson 11/0; Ace Bailey 20/12; Lauri Markkanen 30/22; Jaxson Hayes 13/7",
  'MIN': "LaMelo Ball 26/14; Ayo Dosunmu 7/0; Jonathan Kuminga 4/0; Jaden McDaniels 16/12; Rudy Gobert 22/9",
  'BKN': "Nolan Traore 22/11; Michael Porter Jr. 38/20; Chaney Johnson 0/0; Julius Randle 19/11; Day'Ron Sharpe 31/13",
  'DAL': "Kyrie Irving 14/0; Max Christie 23/9; Cooper Flagg 23/8; P.J. Washington 21/10; Daniel Gafford 21/15",
  'BOS': "Derrick White 18/8; Hugo Gonzalez 17/0; Jayson Tatum 23/13; Paul George 26/18; Neemias Queta 29/18",
  'MIL': "Brayden Burries 0/0; Tyler Herro 18/13; Jaime Jaquez Jr. 60/30; Kyle Kuzma 13/8; Myles Turner 15/4",
  'MIA': "Davion Mitchell 15/4; Klay Thompson 12/6; Andrew Wiggins 15/12; Giannis Antetokounmpo 33/16; Bam Adebayo 31/24",
  'SAC': "Darius Acuff Jr. 11/0; Zach LaVine 24/11; De'Andre Hunter 27/24; Keegan Murray 17/4; Domantas Sabonis 38/13",
  'NO': "Dejounte Murray 20/10; Jeremiah Fears 21/12; Trey Murphy III 19/9; Zion Williamson 20/13; Karlo Matkovic 14/14",
  'LAC': "Darius Garland 12/12; Kris Dunn 9/5; Derrick Jones Jr. 23/17; Rui Hachimura 25/12; Brook Lopez 26/7"},
 '2026-11-09': {
  'LAL': "Luka Doncic 36/16; Austin Reaves 21/16; Matisse Thybulle 18/9; Jake LaRavia 10/8; Walker Kessler 13/13",
  'ATL': "Kingston Flemings 33/33; Nickeil Alexander-Walker 23/11; Dyson Daniels 13/6; Jalen Johnson 19/7; Onyeka Okongwu 21/10",
  'WSH': "Trae Young 8/4; Kyshawn George 17/7; AJ Dybantsa 33/17; Anthony Davis 25/11; Alex Sarr 21/11",
  'DET': "Cade Cunningham 16/8; Duncan Robinson 13/7; Ausar Thompson 15/5; John Collins 28/14; Paul Reed 33/17",
  'CLE': "James Harden 13/8; Donovan Mitchell 20/9; Peyton Watson 13/2; Evan Mobley 31/20; Jarrett Allen 34/27",
  'CHA': "Coby White 21/10; Grayson Allen 32/18; Sion James 4/0; Naz Reid 15/8; Ryan Kalkbrenner 22/6",
  'MEM': "Ty Jerome 26/9; Cedric Coward 20/9; Jaylen Wells 19/6; Cameron Boozer 33/0; Zach Edey 21/16",
  'TOR': "Immanuel Quickley 19/6; RJ Barrett 19/12; Ja'Kobe Walter 13/6; Scottie Barnes 17/9; Jakob Poeltl 16/5",
  'IND': "Andrew Nembhard 22/9; Kelly Oubre Jr. 19/16; Aaron Nesmith 18/6; Pascal Siakam 28/15; Ivica Zubac 35/10",
  'DAL': "Kyrie Irving 13/0; Caleb Martin 20/7; Cooper Flagg 23/8; P.J. Washington 20/9; Daniel Gafford 20/15",
  'DEN': "Jamal Murray 30/22; Christian Braun 0/0; Cameron Johnson 17/11; Aaron Gordon 23/11; Nikola Jokic 30/14",
  'HOU': "Fred VanVleet 25/13; Amen Thompson 20/7; Kevin Durant 19/10; Jabari Smith Jr. 13/6; Alperen Sengun 27/15",
  'SA': "De'Aaron Fox 19/14; Stephon Castle 20/11; Dylan Harper 6/0; Devin Vassell 22/13; Victor Wembanyama 43/30",
  'PHX': "Devin Booker 28/14; Jalen Green 29/12; Dillon Brooks 22/9; Miles Bridges 9/6; Oso Ighodaro 3/3",
  'NO': "Dejounte Murray 19/10; Jeremiah Fears 20/12; Trey Murphy III 20/11; Zion Williamson 20/12; Karlo Matkovic 13/13",
  'GS': "Stephen Curry 24/12; Brandin Podziemski 21/11; Yaxel Lendeborg 10/0; Gui Santos 5/5; Draymond Green 19/10"},
}
# 11/12 on: the fbsheet (First Basket Cheat Sheet) logged per starter in fbsheet_log.csv
HAND = set(SH_RAW)
for r in csv.DictReader(open(R + '/analysis/nba/out/cheatsheet/fbsheet_log.csv')):
    if r['date'] in COMMITS and r['date'] not in HAND:
        t = SH_RAW.setdefault(r['date'], {})
        t[r['team']] = (t[r['team']] + '; ' if r['team'] in t else '') + f"{r['player']} {r['first_bsk_pct']}/{r['first_gm_pct']}"
SH = {}
for d, tab in SH_RAW.items():
    for tm, s in tab.items():
        v = []
        for part in s.split('; '):
            name, nums = part.rsplit(' ', 1)
            b, g = nums.split('/')
            v.append((name, int(b), None if g == '-' else int(g)))
        SH[(d, tm)] = v

TP_TIP = {}
for r in csv.DictReader(open(R + '/analysis/nba/out/cheatsheet/tipproj_log.csv')):
    if r['actual_tip_winner']:
        a, h = [x.strip() for x in r['game'].split('@')]
        TP_TIP[(r['date'], a, h)] = r['tipproj_pick']

# ---------- scoring ----------
def alive(lst, k):
    return [x for x in lst if norm(x[0]) in G[k]['played']]


def records():
    """One row per (source, metric, item): item = game for tip / game #1, (game, team) for team top 2."""
    rows = []
    for k, g in sorted(G.items()):
        d, a, h = k
        tips = {'Ours': OURS_TIP.get(k), 'TipProj': TP_TIP.get(k)}
        st = ST_TIP.get(d, {}).get((a, h))
        tips['StarTool'] = None if not st or st[0] == st[1] else (a if st[0] > st[1] else h)
        tips['@NBAFirstBasket'] = SH_TIP.get(d, {}).get((a, h))
        for s, t in tips.items():
            if t and g['tipw']:
                rows.append((s, 'tip', k, t == g['tipw']))
        for s, P in (('Ours', OURS), ('StarTool', ST), ('@NBAFirstBasket', SH)):
            if (d, a) not in P or (d, h) not in P:
                continue
            both = alive(P[(d, a)], k) + alive(P[(d, h)], k)
            # game #1 needs a printed game chance; a tie at the top = no call
            ranked = sorted([x for x in both if x[2] is not None], key=lambda x: (-x[2], -(x[1] or 0)))
            if ranked and (len(ranked) < 2 or ranked[0][2] != ranked[1][2] or ranked[0][1] != ranked[1][1]):
                rows.append((s, 'g1', k, norm(ranked[0][0]) == g['fp']))
            for tm in (a, h):
                lst = alive(P[(d, tm)], k)
                if not (s == 'StarTool' and P[(d, tm)][0][1] is None):   # star/bomb order kept as printed
                    lst = sorted(lst, key=lambda x: (-x[1], -(x[2] or 0)))
                top2 = [norm(x[0]) for x in lst[:2]]
                if not top2 or tm not in g['tp']:
                    continue
                hit = g['tp'][tm] in top2
                rows.append((s, 't2', (k, tm), hit))
                if tm == g['fpteam']:
                    rows.append((s, 'win2', k, hit))
    return rows


SRC = ('Ours', 'StarTool', '@NBAFirstBasket', 'TipProj')


def tally(rows, metric, items=None):
    out = {}
    for s in SRC:
        v = [h for (x, m, it, h) in rows if x == s and m == metric and (items is None or it in items)]
        out[s] = (sum(v), len(v))
    return out


if __name__ == '__main__':
    rows = records()
    pct = lambda w, n: f"{w}/{n} ({100 * w / n:.0f}%)" if n else 'no data'
    print('ALL LOGGED')
    for m in ('tip', 'g1', 'win2', 't2'):
        print(m, {s: pct(*v) for s, v in tally(rows, m).items()})
    print('HEAD TO HEAD (items every listed source called)')
    for m, srcs in (('tip', ('Ours', 'StarTool', '@NBAFirstBasket')), ('tip', SRC), ('g1', ('Ours', 'StarTool', '@NBAFirstBasket')),
                    ('g1', ('Ours', '@NBAFirstBasket')), ('t2', ('Ours', 'StarTool', '@NBAFirstBasket')),
                    ('win2', ('Ours', 'StarTool', '@NBAFirstBasket'))):
        sets = [{it for (x, mm, it, h) in rows if x == s and mm == m} for s in srcs]
        common = set.intersection(*sets)
        t = tally(rows, m, common)
        print(m, len(common), {s: pct(*t[s]) for s in srcs})
    print('BY DATE (tip / game #1 / team top 2)')
    for d in COMMITS:
        line = []
        for s in SRC:
            r = [(m, h) for (x, m, it, h) in rows if x == s and (it[0][0] if m == 't2' else it[0]) == d]
            f = lambda mm: (sum(h for m, h in r if m == mm), sum(1 for m, h in r if m == mm))
            line.append(f"{s} {'%d-%d' % (f('tip')[0], f('tip')[1] - f('tip')[0])} / {f('g1')[0]}of{f('g1')[1]} / {f('t2')[0]}of{f('t2')[1]}")
        print(d[5:], ' | '.join(line))
