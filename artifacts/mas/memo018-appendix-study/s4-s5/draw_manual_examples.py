"""Manual arithmetic and explanatory charts; never imports or executes CC code."""
from pathlib import Path
import json, os
os.environ['MPLCONFIGDIR']='/tmp/tds-s4-s5-mpl'
os.environ['XDG_CACHE_HOME']='/tmp/tds-s4-s5-cache'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parents[4]
SEG=[10,18,14,22,17,20,12,16,8,13,11,17,14,21,16,20,12]
CENTER=[10,18,12,16,13,19,14,22,18]

def legs(endpoints):return [(min(a,b),max(a,b)) for a,b in zip(endpoints,endpoints[1:])]
s=legs(SEG);z=legs(CENTER)
# Check exact comparisons stated in the manuscript, not a replica of the engine.
assert max(s[i][0] for i in [0,1,2])==14
assert min(s[i][1] for i in [0,1,2])==18
for indexes,values in [([1,3,5],[(14,18),(17,22),(12,20)]),([6,8,10],[(12,16),(8,13),(11,17)]),([11,13,15],[(14,17),(16,21),(12,20)])]:
 assert [s[i] for i in indexes]==values
assert 18<22 and 20<=22 and 12<17 and not 18<17
assert 17>13 and 12>8 and 11>=8 and not 13<12
assert 17<21 and 20<=21 and 12<16 and not 17<16
for start,end,direction in [(0,2,'up'),(3,7,'down'),(8,12,'up')]:
 assert (end-start+1)>=3 and (end-start+1)%2==1
 assert max(s[i][0] for i in range(start,start+3))<=min(s[i][1] for i in range(start,start+3))
 assert SEG[start]==(min(SEG[start:end+2]) if direction=='up' else max(SEG[start:end+2]))
 assert SEG[end+1]==(max(SEG[start:end+2]) if direction=='up' else min(SEG[start:end+2]))
zd=max(z[i][0] for i in [1,2,3]); zg=min(z[i][1] for i in [1,2,3])
assert (zd,zg)==(13,16)
assert max(z[5][0],zd)<=min(z[5][1],zg)
assert max(z[7][0],zd)>min(z[7][1],zg)
assert z[7][0]>zg
assert max(z[i][1] for i in [1,3,5])==19
assert min(z[i][0] for i in [1,3,5])==12
assert max(16,zd)<=min(22,zg)
assert max(16,16,20)==min(20,22,22)==20

def style(ax):
 ax.set_facecolor('#f8fafc');ax.grid(True,color='#dbe3ec',lw=.65);ax.set_axisbelow(True)
 ax.set_ylabel('Price');ax.spines[['top','right']].set_visible(False)

def inputs(ax,points,prefix):
 ax.plot(range(len(points)),points,c='#52657d',marker='o',lw=1.3,markersize=4)
 for i,(a,b) in enumerate(zip(points,points[1:])):
  ax.text(i+.5,(a+b)/2+.35,f'{prefix}{i}',fontsize=8,ha='center',color='#334155')
 for i,p in enumerate(points):ax.annotate(str(p),(i,p),xytext=(0,9 if i%2 else -15),textcoords='offset points',ha='center',fontsize=8)

fig,axs=plt.subplots(3,1,figsize=(13,9),sharex=True,sharey=True,gridspec_kw={'height_ratios':[1.2,1.1,.85]})
for ax in axs:style(ax);ax.set_ylim(6,24.7)
inputs(axs[0],SEG,'B');axs[0].set_title('Input: continuous alternating strokes B0-B15 (constructed endpoints)',loc='left',fontsize=12)
for a,b,color,label,ls in [(0,3,'#007f73','N0: FROZEN at later evidence B15','-'),(3,8,'#b45309','N1 -> soft N0','--'),(8,13,'#6d28d9','N2 -> pending / forming','--')]:
 axs[1].plot([a,b],[SEG[a],SEG[b]],c=color,lw=3,ls=ls,marker='o',label=label)
 axs[1].text((a+b)/2,23.6,f'B{a}-B{b-1}',color=color,fontsize=9,ha='center')
axs[1].plot(range(len(SEG)),SEG,c='#cbd5e1',lw=1,zorder=0)
axs[1].legend(loc='lower left',fontsize=8,ncol=3)
axs[1].set_title('Derived geometry: source strokes do not overlap; endpoint time / price is shared',loc='left',fontsize=11)
for inds,color in [([1,3,5],'#007f73'),([6,8,10],'#b45309'),([11,13,15],'#6d28d9')]:
 for j,bi in enumerate(inds):
  lo,hi=s[bi]; x=bi+.5
  axs[2].vlines(x,lo,hi,color=color,lw=4)
  axs[2].text(x,hi+.55,f'e{j}:B{bi}',fontsize=8,ha='center',color=color)
axs[2].set_title('Feature intervals: first top -> bottom -> next top (manual source-code comparisons)',loc='left',fontsize=11)
axs[2].set_xticks(range(len(SEG)),[f'P{i}' for i in range(len(SEG))]);axs[2].set_xlabel('Shared endpoint order (not a market timestamp)')
fig.suptitle('CC segment study: MANUAL trace; no CC runtime output',fontsize=15,weight='bold')
fig.text(.5,.012,'Price lines / intervals only: input is strokes, original OHLC is unavailable. Synthetic teaching data; no candles inferred.',ha='center',fontsize=9,color='#475569')
fig.tight_layout(rect=[0,.035,1,.96])
out=ROOT/'docs/memo/memoWX_021_Chan_xianduan/manual-segment-sequence.png';fig.savefig(out,dpi=150);plt.close(fig)

fig,axs=plt.subplots(2,1,figsize=(12,7.5),sharex=True,sharey=True)
for ax in axs:style(ax);ax.set_ylim(8.3,24)
inputs(axs[0],CENTER,'L');axs[0].set_title('Input: completed base legs E, A/B/C, bridge+Z3, bridge+Z4',loc='left',fontsize=12)
for i,label in [(0,'E: evidence'),(1,'A'),(2,'B'),(3,'C / Z2'),(4,'bridge'),(5,'Z3'),(6,'bridge'),(7,'Z4: close')]:
 axs[0].text(i+.5,23.1,label,fontsize=8,ha='center')
axs[1].plot(range(len(CENTER)),CENTER,c='#cbd5e1',lw=1.5)
axs[1].add_patch(Rectangle((1,13),3,3,facecolor='#10b981',alpha=.3,label='Core members L1-L3'))
axs[1].add_patch(Rectangle((4,13),2,3,facecolor='#2563eb',alpha=.22,label='Extension L4-L5; core unchanged'))
axs[1].hlines([13,16],1,6,colors='#007f73',lw=2)
axs[1].text(2.3,14.25,'Fixed [ZD,ZG] = [13,16]',fontsize=11,color='#005e54')
axs[1].hlines([12,19],1,6,colors='#64748b',lw=1,ls=':')
axs[1].text(4.5,19.5,'GG=19; DD=12',fontsize=9,color='#475569')
axs[1].plot([7,8],[22,18],c='#be123c',lw=3,marker='o',label='L7 closing evidence: NOT a member')
axs[1].axvline(6,c='#2563eb',ls='--',lw=1)
axs[1].annotate('Geometry ends T6\nClose observed T8',(6,14),xytext=(6.4,10),fontsize=9,arrowprops={'arrowstyle':'->','color':'#64748b'})
axs[1].text(.5,11.1,'E not member',fontsize=9,ha='center')
axs[1].set_xticks(range(len(CENTER)),[f'T{i}' for i in range(len(CENTER))]);axs[1].set_xlabel('Shared source endpoint order')
axs[1].set_title('EXTEND result: members {1,2,3,4,5}; evidence index 7; CLOSED upward',loc='left',fontsize=12)
axs[1].legend(loc='upper left',fontsize=8,ncol=1)
fig.suptitle('CC center study: MANUAL geometry; no CC runtime output',fontsize=15,weight='bold')
fig.text(.5,.015,'Constructed completed legs, not raw candlesticks. Closed-interval intersection; core bounds stay fixed during extension.',ha='center',fontsize=9,color='#475569')
fig.tight_layout(rect=[0,.04,1,.95]);fig.savefig(ROOT/'docs/memo/memoWX_022_Chan_zhongshu/manual-center-sequence.png',dpi=150);plt.close(fig)
( ROOT/'artifacts/mas/memo018-appendix-study/s4-s5/manual_arithmetic.json').write_text(json.dumps({'segment_endpoints':SEG,'center_endpoints':CENTER,'center_core':[zd,zg],'checks':'all arithmetic assertions passed; no CC imports/execution'},indent=2)+'\n')
print('Arithmetic assertions and two charts generated; CC not imported or executed.')
