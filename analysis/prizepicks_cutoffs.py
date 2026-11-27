import json,statistics as S,math
d=json.load(open('nba_box.json'))
close={'MIA','NY','PHI','IND','DAL','PHX','NO','LAC','LAL','SA','ATL','BOS','MEM','MIN'}
gs=sorted(d['games'].values(),key=lambda g:g['date'])
P={}
for g in gs:
    for r in g['rows']:
        if r['team'] not in close: continue
        try: m=int(r['minutes'])
        except: continue
        P.setdefault((r['team'],r['name']),[]).append(dict(min=m,pts=int(r['points']),reb=int(r['rebounds']),ast=int(r['assists'])))
def ncdf(z): return 0.5*(1+math.erf(z/2**0.5))
res=[]
for (t,n),L in P.items():
    L=L[-10:]
    if len(L)<8: continue
    mins=[x['min'] for x in L]
    if S.mean(mins)<30 or min(mins)<24: continue
    for stat in ['reb','pts','pr','pra','ra']:
        f={'reb':lambda x:x['reb'],'pts':lambda x:x['pts'],'pr':lambda x:x['pts']+x['reb'],'pra':lambda x:x['pts']+x['reb']+x['ast'],'ra':lambda x:x['reb']+x['ast']}[stat]
        v=[f(x) for x in L]; med=S.median(v); mu=S.mean(v); sd=max(S.pstdev(v),math.sqrt(mu)*0.9)*1.15
        proj=0.5*med+0.5*mu
        # cutoff: largest X.5 with P(>X)>=0.6
        X=math.floor(proj)+0.5
        while 1-ncdf((X-proj)/sd)<0.60: X-=1
        emp=sum(1 for a in v if a>X)/len(v)
        # 'edge width': gap between cutoff and projection relative to typical PP line(~proj-0.5)
        res.append((round((proj-X)/proj,3),t,n,stat,round(proj,1),X,round(emp,2),min(v),round(sd,1)))
res.sort()
for r in res:
    if r[3] in('reb','pr','pra','ra') or r[0]<0.1: print(r)
