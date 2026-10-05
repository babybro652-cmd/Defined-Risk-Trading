import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
G,R,TEAL,OR,BL,GR="#1A9E5F","#D94141","#8FD3CF","#E8912D","#2A6FDB","#6E6E6E"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":20})
def candles(ax,o,h,l,c,x0=0,w=0.6):
    for i,(oo,hh,ll,cc) in enumerate(zip(o,h,l,c)):
        col=G if cc>=oo else R; x=x0+i
        ax.plot([x,x],[ll,hh],color=col,lw=2.2,zorder=3)
        ax.add_patch(Rectangle((x-w/2,min(oo,cc)),w,max(abs(cc-oo),0.15),color=col,zorder=4))
def path(cl,rng,wick=0.6):
    o=[cl[0]]+cl[:-1]; h=[max(a,b)+rng.uniform(0.2,wick) for a,b in zip(o,cl)]; l=[min(a,b)-rng.uniform(0.2,wick) for a,b in zip(o,cl)]
    return o,h,l,list(cl)
def profile(ax,levels,vols,x0,scale,poc=None,va=None):
    for lv,v in zip(levels,vols):
        ax.add_patch(Rectangle((x0,lv-0.2),v*scale,0.4,color=OR if poc is not None and abs(lv-poc)<1e-6 else TEAL,zorder=2))
    if va: ax.add_patch(Rectangle((x0-0.35,va[0]),0.25,va[1]-va[0],color="#B9A7F5",zorder=2))
def clean(ax):
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xticks([]);ax.set_yticks([])
def save(fig,name):
    fig.savefig(name,dpi=150,bbox_inches="tight",facecolor="white");plt.close(fig);print(name)

# A: profile basics
rng=np.random.default_rng(3)
cl=[100,101.5,100.8,102,101.2,100.4,101.6,102.8,102.2,101.4,102.6,103.4,102.8,101.9,102.7,103.8,104.6,103.9,103.1,102.5,103.3,102.6,101.8,102.4,103.0,102.2,101.6,102.3,103.1,102.7]
o,h,l,c=path(cl,rng,0.9)
fig,ax=plt.subplots(figsize=(13,5.2));candles(ax,o,h,l,c)
lv=np.arange(98.8,106.0,0.45); poc=lv[np.argmin(abs(lv-102.55))]
vol=np.exp(-((lv-102.55)/1.25)**2)
profile(ax,lv,vol,31.5,5.5,poc=poc,va=(101.1,104.0))
ax.axhline(poc,color=OR,ls="--",lw=2,xmax=0.83,zorder=1)
ax.text(37.4,poc,"POC",color=OR,fontsize=26,fontweight="bold",va="center")
ax.text(37.4,104.3,"Value Area\n(about 70%)",color="#7B5CE0",fontsize=20,fontweight="bold",va="center")
ax.set_xlim(-1,41);ax.set_ylim(98.5,106.3);clean(ax);save(fig,"ex_profile.png")

# B: gap vs node
def sweep_panel(ax,node):
    rng=np.random.default_rng(7)
    base=[104,104.3,103.8,104.2,103.9,104.4,104.0,103.6,102.6,101.6,100.8,100.2]
    if not node:
        tail=[100.6,101.8,103.0,104.0,105.0,105.8,106.4]
        o,h,l,c=path(base+tail,rng,0.4); l[12]=97.6
    else:
        tail=[99.8,100.3,99.6,100.1,99.7,100.4,99.9,100.6,101.2]
        o,h,l,c=path(base+tail,rng,0.5)
        for i in range(12,20): l[i]=min(l[i],99.0+rng.uniform(-0.4,0.3))
    candles(ax,o,h,l,c)
    ax.axhline(99.9,color=GR,ls=":",lw=2.2,xmax=0.74)
    ax.text(0,99.4,"Asia low",color=GR,fontsize=18)
    lv=np.arange(96.6,107.4,0.45)
    if not node:
        vol=np.exp(-((lv-104)/1.3)**2)+0.08; vol[(lv>97)&(lv<100.5)]=0.05
        poc=lv[np.argmin(abs(lv-104))]; ax.annotate("Thin volume:\none wick, then\na fast reversal",xy=(12,97.8),xytext=(13.4,97.2),color=G,fontsize=18,fontweight="bold",arrowprops=dict(arrowstyle="->",color=G,lw=2))
    else:
        vol=0.35*np.exp(-((lv-104)/1.0)**2)+np.exp(-((lv-99.3)/0.9)**2)+0.05
        poc=lv[np.argmin(abs(lv-99.3))]; ax.add_patch(Rectangle((11.5,98.3),8.2,2.6,fill=False,ec=R,ls=":",lw=2.5))
        ax.text(8.5,97.2,"Chop inside the node",color=R,fontsize=18,fontweight="bold")
    profile(ax,lv,vol,24.5,4.5,poc=poc)
    ax.text(24.2,poc,"POC",color=OR,fontsize=18,fontweight="bold",ha="right",va="center")
    ax.set_xlim(-1,30);ax.set_ylim(96.6,107.6);clean(ax)
fig,axs=plt.subplots(1,2,figsize=(14,5.6))
for ax,node,t in zip(axs,[False,True],["1. Through a low-volume gap","2. Into a high-volume node"]):
    sweep_panel(ax,node); ax.set_title(t,fontsize=24,fontweight="bold",loc="left",color=G if not node else R)
fig.tight_layout(w_pad=3);save(fig,"ex_gap_node.png")

# C1: POC as exit
rng=np.random.default_rng(11)
rangecl=[103,104.2,103.4,102.6,103.6,104.4,103.2,102.4,103.4,104.0,103.0,102.2]
o,h,l,c=path(rangecl+[101.0,100.6,101.6,102.4,103.1,103.6],rng,0.5)
l[13]=98.8
fig,ax=plt.subplots(figsize=(13,5.4));ax.add_patch(Rectangle((-0.6,97),12.2,9,color="#F2F2F2",zorder=0))
ax.text(0,105.6,"Profiled range",color=GR,fontsize=18)
candles(ax,o,h,l,c)
ax.plot([-0.6,12.6],[101.7,101.7],color=GR,ls=":",lw=2); ax.text(0,101.2,"Range low",color=GR,fontsize=17)
ent=c[14]; lv=np.arange(100.6,105.6,0.4); poc=lv[np.argmin(abs(lv-103.4))]
profile(ax,lv,np.exp(-((lv-103.4)/1.1)**2),21,5,poc=poc)
ax.plot([-0.6,21],[poc,poc],color=OR,ls="--",lw=2.5)
ax.text(13.0,poc+0.45,"Target: POC",color=OR,fontsize=20,fontweight="bold")
ax.plot([14,17.3],[ent,ent],color=G,lw=3);ax.text(17.5,ent,"Entry",color=G,fontsize=20,fontweight="bold",va="center")
ax.plot([14,17.3],[ent-3.75,ent-3.75],color=R,lw=3);ax.text(17.5,ent-3.75,"Stop 3.5–4 pts",color=R,fontsize=20,fontweight="bold",va="center")
ax.text(12.6,98.0,"Sweep",color=R,fontsize=20,fontweight="bold",ha="right")
ax.set_xlim(-1,27);ax.set_ylim(97,106.4);clean(ax);save(fig,"ex_poc_exit.png")

# C2: POC as entry
rng=np.random.default_rng(5)
rangecl=[101,102.2,101.4,100.6,101.6,102.0,101.0,100.4,101.4,102.0,101.2,101.6]
up=[103,104.4,105.6,106.2,105.4,104.2,103.0,102.0,102.9,104.0,105.2,106.4]
o,h,l,c=path(rangecl+up,rng,0.45)
lv=np.arange(99.2,104.0,0.4); poc=lv[np.argmin(abs(lv-101.5))]
ri=12+8; o[ri]=c[ri-1]; l[ri]=poc-0.35; c[ri]=102.9; h[ri]=103.15; l[ri-1]=max(l[ri-1],poc+0.25)
fig,ax=plt.subplots(figsize=(13,5.6));ax.add_patch(Rectangle((-0.6,96.5),12.2,12,color="#F2F2F2",zorder=0))
ax.text(0,103.4,"Profiled range",color=GR,fontsize=18)
candles(ax,o,h,l,c)
profile(ax,lv,np.exp(-((lv-101.5)/1.0)**2),33,4.5,poc=poc)
ax.plot([-0.6,33],[poc,poc],color=OR,ls="--",lw=2.5);ax.text(37.9,poc,"POC",color=OR,fontsize=20,fontweight="bold",va="center")
ax.plot([-0.6,33],[107.6,107.6],color=G,ls="--",lw=2.5);ax.text(0,107.85,"Target: untaken session high (exit at the line or within 1 pt)",color=G,fontsize=18,fontweight="bold")
ent=c[ri]
ax.plot([ri,ri+3.4],[ent,ent],color=G,lw=3);ax.text(ri+3.6,ent,"Entry on its close",color=G,fontsize=18,fontweight="bold",va="center")
ax.plot([ri,ri+3.4],[ent-3.75,ent-3.75],color=R,lw=3);ax.text(ri+3.6,ent-3.75,"Stop 3.5–4 pts",color=R,fontsize=18,fontweight="bold",va="center")
ax.annotate("Reaction candle\nat the POC",xy=(ri,poc-0.3),xytext=(ri-11,97.6),color=OR,fontsize=18,fontweight="bold",arrowprops=dict(arrowstyle="->",color=OR,lw=2))
ax.set_xlim(-1,41);ax.set_ylim(96.5,108.6);clean(ax);save(fig,"ex_poc_entry.png")
