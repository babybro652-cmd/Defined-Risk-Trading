import json,subprocess,re,csv,collections,os
R='/home/user/Defined-Risk-Trading'
def show(c,p): return subprocess.run(['git','-C',R,'show',f'{c}:{p}'],capture_output=True,text=True).stdout
dates={'2026-10-30':'485077d','2026-11-02':'abc9b15','2026-11-04':'ea0de84','2026-11-05':'a3b7043','2026-11-06':'9799f9f','2026-11-07':'08379c3'}
log=[r for r in csv.DictReader(open(R+'/analysis/first_events/log.csv')) if r['sport']=='NBA']
games=json.load(open(R+'/analysis/nba/data/games_2026-27.json')); games=list(games.values()) if isinstance(games,dict) else games
ros={k:v['name'] for k,v in json.load(open(R+'/analysis/nba/data/rosters.json')).items()}
def last(n): return n.split(' (')[0].strip()
rows=[]
for d,c in dates.items():
    try: fb=json.loads(show(c,'analysis/nba/out/fb_candidates.json'))
    except Exception: continue
    sl=show(c,'analysis/nba/out/shortlist.md')
    tips={}
    for m in re.finditer(r'- (\S+) @ (\S+) [\d:]+ ET: .*?away wins tip (\d+)%',sl):
        a,h,p=m.group(1),m.group(2),int(m.group(3)); tips[a]=p; tips[h]=100-p
    lu={}
    lf=f'{R}/analysis/nba/data/lineups_{d}.json'
    if os.path.exists(lf):
        try: lu=json.loads(show(c,f'analysis/nba/data/lineups_{d}.json')) or json.load(open(lf))
        except Exception: lu=json.load(open(lf))
    t=collections.defaultdict(list)
    for r in fb: t[r['tm']].append(r)
    for tm,v in t.items():
        v.sort(key=lambda r:-r['p_v2']); top=[x['player'] for x in v[:2]]; opp=v[0]['opp']
        g=next((x for x in log if x['date']==d and tm in [s.strip() for s in x['game'].split('@')]),None)
        if not g: continue
        side='away' if g['game'].split('@')[0].strip()==tm else 'home'
        tfs=g[f'{side}_first_shot']; fp=g['first_points_any']; fs=g['first_score']
        # team first basket: from games json
        gj=next((x for x in games if isinstance(x,dict) and x.get('date')==d and tm in (x.get('away'),x.get('home'))),None)
        team_first=ros.get(gj['tf'].get(tm),'') if gj and gj.get('tf') else ''
        startersact=set(ros.get(p[0],p[0]) for p in (gj or {}).get('pl',[]) if p[1]==tm and p[2])
        proj=set((lu.get(tm) or {}).get('five',[])) if isinstance(lu,dict) else set()
        miss=sorted(proj-startersact) if proj and startersact else []
        hit_team=team_first in top
        hit_game=any(last(fp)==p for p in top) if fp else False
        rows.append(dict(date=d,team=tm,opp=opp,tip=tips.get(tm,''),tipwin=g.get('tip_winner',''),top=' / '.join(top),
                         team_first=team_first,hit_team=hit_team,hit_game=hit_game,first_points=fp,proj_known=bool(proj),missing=', '.join(miss)))
with open(R+'/analysis/reports/2026-11-08-model-consistency-by-team.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
agg=collections.defaultdict(list)
for r in rows: agg[r['team']].append(r)
out=[]
for tm,v in agg.items():
    n=len(v); ht=sum(r['hit_team'] for r in v); hg=sum(r['hit_game'] for r in v)
    tp=[r['tip'] for r in v if r['tip']!='']; full=sum(1 for r in v if r['proj_known'] and not r['missing'])
    out.append((ht/n,n,tm,ht,hg,round(sum(tp)/len(tp)) if tp else '-',full,sum(r['proj_known'] for r in v),'; '.join(f"{r['date'][5:]} vs {r['opp']} tip {r['tip']}% {'HIT' if r['hit_team'] else 'miss'} ({r['team_first']}){' MISSING: '+r['missing'] if r['missing'] else ''}" for r in v)))
out.sort(key=lambda x:(-x[0],-x[1]))
print(len(rows),'team-games')
for o in out:
    if o[1]>=2: print(f"{o[2]}: team-first {o[3]}/{o[1]}, game-first {o[4]}/{o[1]}, avg tip {o[5]}%, full lineup {o[6]}/{o[7]} | {o[8]}")
