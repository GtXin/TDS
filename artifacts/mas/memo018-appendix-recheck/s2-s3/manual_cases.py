"""Manual arithmetic and financial figures; no CC imports or execution."""
from pathlib import Path
import json
import os

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/tds-memo018-recheck-s23-mpl")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
ASSETS = ROOT / "docs/memo/memoWX_020_Chan_bi"
BASE = [(8,11),(6,9),(9,12),(11,14),(13,16),(12,15),(10,13),
        (8,11),(5,8),(7,10),(10,13),(12,15),(14,17),(12,15),(11,14.5),
        (10,14),(12,18),(8,12),(6,10),(4,8),(3,7),(5,9)]


def candidates(data):
    values = []
    for i in range(1,len(data)-1):
        a,b,c=data[i-1:i+2]
        if b[0]>max(a[0],c[0]) and b[1]>max(a[1],c[1]):
            values.append((i,"T",b[1]))
        elif b[0]<min(a[0],c[0]) and b[1]<min(a[1],c[1]):
            values.append((i,"B",b[0]))
    return values


def no_inclusion(data):
    for a,b in zip(data,data[1:]):
        assert not ((a[0]<=b[0] and a[1]>=b[1]) or (b[0]<=a[0] and b[1]>=a[1]))


def no_gap(data,s,e):
    assert all(max(data[i][0],data[i+1][0])<=min(data[i][1],data[i+1][1]) for i in range(s,e))


def half_up(data,s,e):
    # Arithmetic ledger for source341–372, not a CC call.
    assert data[s][0] < min(data[e-1][0],data[e][0])
    assert data[e][1] > max(data[s][1],data[s+1][1])
    assert all(x[1]<=data[e][1] for x in data[s+1:e])


def half_down(data,s,e):
    assert data[s][1] > max(data[e-1][1],data[e][1])
    assert data[e][0] < min(data[s][0],data[s+1][0])
    assert all(x[0]>=data[e][0] for x in data[s+1:e])


strong_prev=BASE[:17]
strong_prev[15]=(5.5,14)
assert candidates(strong_prev)==[(1,'B',6),(4,'T',16),(8,'B',5),(12,'T',17),(15,'B',5.5)]
assert 12-8==4 and 15-12==3
half_down(strong_prev,4,8);half_up(strong_prev,8,12)
no_gap(strong_prev,12,15)
assert 17-5.5 >= .95*(17-5)

strong_next=BASE[:15]+[(7,12),(9,13),(10,14),(11,15),(12,16),(9,12)]
assert candidates(strong_next)==[(1,'B',6),(4,'T',16),(8,'B',5),(12,'T',17),(15,'B',7),(19,'T',16)]
no_gap(strong_next,12,15)
assert 17-7 < .95*(17-5)
half_up(strong_next,15,19)
assert 19-15==4 and 17-7>=.95*(16-7)
assert (19,'T',16) not in candidates(strong_next[:17])

repair_accept=BASE[:18]
repair_accept[12]=(14,15.5)
repair_accept[15]=(4,14)
assert candidates(repair_accept)==[(1,'B',6),(4,'T',16),(8,'B',5),(12,'T',15.5),(15,'B',4),(16,'T',18)]
no_gap(repair_accept,12,15)
half_up(repair_accept,8,12)
assert 15-12==3 and 4<=5 and 15.5<=16
assert all(x[0]>=4 for x in repair_accept[5:15])
assert 18>15.5 and 4<5

repair_reject=BASE[:15]+[(4,14),(12,15),(8,12),(3,9),(6,11)]
repair_reject[12]=(14,15.5)
assert candidates(repair_reject)==[(1,'B',6),(4,'T',16),(8,'B',5),(12,'T',15.5),(15,'B',4),(16,'T',15),(18,'B',3)]
assert 15<=15.5
half_down(repair_reject,12,18)
assert 18-12>=4
for data in [strong_prev,strong_next,repair_accept,repair_reject]:no_inclusion(data)

cases=[
    {"name":"strong_prev","ranges":strong_prev,"events":"B15 amplitude11.5 >=0.95*12=11.4; standard gap-adjusted span3 fails; append strong_prev, dep15","paths":[[4,8,12,15]],"dep":15},
    {"name":"strong_next","ranges":strong_next,"events":"B15 amplitude10<11.4, future B15->T19 standard amplitude9,10>=8.55; append strong_next dep19 then standard T19","paths":[[4,8,12,15,19]],"dep":19},
    {"name":"repair_accept","ranges":repair_accept,"events":"T12.top15.5<=T4.top16; B15.low4<=B8.low5; future T16.top18>15.5 confirms before standard reverse; absorb B8->T12 and extend T4->B15; dep16","paths":[[4,15]],"dep":16},
    {"name":"repair_reject","ranges":repair_reject,"events":"T16.top15<=15.5, then T12->B18 passes standard first; do not absorb; append T12->B18","paths":[[4,8,12,18]],"dep":18},
]
(OUT/'manual-cases.json').write_text(json.dumps({"nature":"Manual source-branch/arithmetic assertions; no CC imports/execution","base_ranges":BASE,"cases":cases},indent=2)+'\n')


def chart(selected,filename,title):
    path=ASSETS/filename
    assert not path.exists(), 'Back up before replacing chart'
    fig,axes=plt.subplots(2,1,figsize=(14,8.6),sharex=True,sharey=True,layout='constrained')
    for ax,case in zip(axes,selected):
        data=case['ranges']
        for i,(low,high) in enumerate(data):
            o=low+.3*(high-low);c=low+.7*(high-low)
            if i%2:o,c=c,o
            color='#208476' if c>o else '#c24b53'
            ax.vlines(i,low,high,color=color,linewidth=1.1)
            ax.add_patch(Rectangle((i-.29,min(o,c)),.58,abs(c-o),facecolor=color,edgecolor=color,alpha=.68))
        fxs=candidates(data)
        lookup={i:price for i,kind,price in fxs}
        for i,kind,price in fxs:
            ax.annotate(f'{kind}{i}',(i,price),xytext=(0,9 if kind=='T' else -15),textcoords='offset points',ha='center',fontsize=9)
        for points in case['paths']:
            ax.plot(points,[lookup[i] for i in points],color='#2056a0',lw=2.4,marker='o',ms=4)
        if case['name']=='repair_accept':
            ax.plot([4,8,12],[16,5,15.5],color='#bd7b25',lw=1.6,ls='--',label='Before repair: T4-B8-T12')
            ax.legend(loc='lower left',fontsize=9)
        endpoint=15 if case['name'] in ['strong_prev','strong_next','repair_accept'] else 18
        price=lookup[endpoint]
        if case['dep']!=endpoint:
            dep=case['dep']
            ax.axvspan(endpoint,dep,color='#e1c979',alpha=.14)
            ax.annotate(f'Geometry {endpoint}; dependency {dep}',xy=(endpoint,price),xytext=(9.2,1.0),arrowprops={'arrowstyle':'->'},fontsize=10)
        ax.set_title(case['name']+' — '+({'strong_prev':'11.5 >= 11.4; dep15','strong_next':'10 < 11.4, but10 >= 0.95*9; dep19','repair_accept':'18 > 15.5 confirms; old rebound removed','repair_reject':'future standard reverse arrives first; old rebound retained'}[case['name']]),loc='left',fontsize=11)
        ax.set_ylim(0,20.5);ax.set_xlim(-.7,21.5);ax.set_ylabel('Price');ax.grid(alpha=.18);ax.spines[['top','right']].set_visible(False)
    axes[-1].set_xticks(range(22));axes[-1].set_xlabel('Ordered source index; each Mi=Ri has a single raw member')
    fig.suptitle(title+'\nManual source-code trace; no CC runtime output',fontsize=13)
    fig.supxlabel('O/C are synthetic30%/70% of each H/L range, alternating colors; only H/L drive conditions.',fontsize=9)
    fig.savefig(path,dpi=140)
    plt.close(fig)


chart(cases[:2],'cc-stroke-strong-recheck.png','Strong profile: separate variants of the existing main sequence')
chart(cases[2:],'cc-stroke-repair-recheck.png','Default5k repair guard: two separate future continuations')
print('Four source-branch manual cases and two aligned price charts passed; no CC execution.')
