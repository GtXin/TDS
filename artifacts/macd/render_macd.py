"""Render two educational MACD charts from deterministic synthetic close prices."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

OUT=Path(__file__).resolve().parent
font_path=Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
if font_path.exists():
    font_manager.fontManager.addfont(str(font_path))
    plt.rcParams['font.family']='Arial Unicode MS'
plt.rcParams.update({'font.size':11,'axes.unicode_minus':False,'savefig.facecolor':'white'})
BLUE='#2563eb';ORANGE='#d97706';GREEN='#0f766e';PURPLE='#7c3aed';GRAY='#64748b';RED='#dc2626'

def ema(values,period):
    result=np.empty(len(values),dtype=float)
    result[0]=values[0]
    alpha=2/(period+1)
    for i in range(1,len(values)):
        result[i]=alpha*values[i]+(1-alpha)*result[i-1]
    return result

# 160 earlier bars warm up both price EMAs and the signal EMA before display.
warmup=160
x=np.arange(141)
anchors_x=[0,20,35,45,65,80,105,115,140]
anchors_y=[100,104,120,118,110,116,125,124,112]
shown=np.interp(x,anchors_x,anchors_y)+.12*np.sin(.63*x)
closes=np.r_[np.full(warmup,100.0),shown]
fast=ema(closes,12);slow=ema(closes,26)
dif=fast-slow;dea=ema(dif,9);hist=dif-dea
assert np.allclose(dif,fast-slow)
assert np.allclose(hist,dif-dea)
assert np.all(hist[dif>dea]>0) and np.all(hist[dif<dea]<0)
close,fast,slow,dif,dea,hist=[a[warmup:] for a in [closes,fast,slow,dif,dea,hist]]
# Compare each upward leg's own price/DIF peaks, whose timestamps may differ.
p1=15+int(np.argmax(close[15:56]));p2=65+int(np.argmax(close[65:121]))
m1=15+int(np.argmax(dif[15:56]));m2=65+int(np.argmax(dif[65:121]))
assert close[p2]>close[p1]+2
assert 0<dif[m2]<dif[m1]*.85
assert hist.min()<0<hist.max()
with (OUT/'synthetic_macd.csv').open('w',newline='') as f:
    writer=csv.writer(f)
    writer.writerow(['bar','display_bar','close','ema12','ema26','dif','dea','histogram'])
    # Retain all warm-up inputs so calculations are reproducible.
    full_fast=ema(closes,12);full_slow=ema(closes,26)
    full_dif=full_fast-full_slow;full_dea=ema(full_dif,9)
    for i in range(len(closes)):
        writer.writerow([i,i-warmup,closes[i],full_fast[i],full_slow[i],full_dif[i],full_dea[i],full_dif[i]-full_dea[i]])

def style(ax):
    ax.set_xlim(-2,142)
    ax.grid(axis='y',color='#e2e8f0',lw=.7);ax.set_axisbelow(True)
    for side in ['top','right']:ax.spines[side].set_visible(False)
    for side in ['left','bottom']:ax.spines[side].set_color('#cbd5e1')
    ax.tick_params(length=0,labelsize=10)

def macd_panel(ax,faded=False):
    alpha=.4 if faded else .8
    ax.bar(x,hist,color=np.where(hist>=0,RED,GREEN),width=.85,alpha=alpha,label='柱状图 = DIF − DEA',zorder=2)
    ax.plot(x,dif,color=BLUE,lw=2.1,label='DIF：EMA12 − EMA26',zorder=3)
    ax.plot(x,dea,color=ORANGE,lw=1.7,alpha=.7 if faded else 1,label='DEA：DIF 的 EMA9',zorder=3)
    ax.axhline(0,color=GRAY,lw=.9)
    ax.set_ylabel('指标值')
    style(ax)

fig,axes=plt.subplots(2,1,figsize=(11,6.9),sharex=True,gridspec_kw={'height_ratios':[1.1,1]})
fig.subplots_adjust(left=.08,right=.97,top=.82,bottom=.13,hspace=.25)
fig.suptitle('MACD 怎么看：价格、两条线和柱状图',fontsize=21,y=.975)
fig.text(.5,.9,'同一组模拟收盘价；常用参数 12、26、9；横轴每一步是一根 K 线。',ha='center',fontsize=11,color=GRAY)
axes[0].plot(x,close,color='#334155',lw=2,label='收盘价')
axes[0].plot(x,fast,color=BLUE,lw=1.6,label='EMA12（较快）')
axes[0].plot(x,slow,color=ORANGE,lw=1.6,label='EMA26（较慢）')
axes[0].set_ylabel('价格');style(axes[0]);axes[0].legend(loc='upper left',fontsize=9,ncol=3,frameon=False)
macd_panel(axes[1]);axes[1].legend(loc='lower left',bbox_to_anchor=(0,1.02),fontsize=9,ncol=3,frameon=False)
axes[1].set_xlabel('时间／K 线序号 →')
fig.text(.5,.045,'EMA 更重视近期价格；DIF 比较快慢均价，DEA 平滑 DIF，柱子显示两条线的差距。',ha='center',fontsize=11,color=GRAY)
fig.savefig(OUT/'macd-components.png',dpi=170);plt.close(fig)

fig,axes=plt.subplots(2,1,figsize=(11,7.1),sharex=True,gridspec_kw={'height_ratios':[1,1]})
fig.subplots_adjust(left=.08,right=.97,top=.81,bottom=.15,hspace=.27)
fig.suptitle('指标背离示例：价格更高，DIF 峰值更低',fontsize=21,y=.975)
fig.text(.5,.9,'同一组模拟数据；分别比较两段上行中的价格峰值与 DIF 峰值。',ha='center',fontsize=11,color=GRAY)
for ax in axes:
    ax.axvspan(15,55,color=BLUE,alpha=.045,zorder=0)
    ax.axvspan(65,120,color=PURPLE,alpha=.045,zorder=0)
axes[0].plot(x,close,color='#334155',lw=2);style(axes[0]);axes[0].set_ylabel('价格')
axes[0].set_ylim(98,132)
axes[0].scatter([p1,p2],close[[p1,p2]],color=PURPLE,s=45,zorder=5)
axes[0].plot([p1,p2],close[[p1,p2]],ls='--',color=PURPLE,lw=1.7)
for i in [p1,p2]:axes[0].annotate(f'{close[i]:.1f}',(i,close[i]),xytext=(0,9),textcoords='offset points',ha='center',fontsize=11,color=PURPLE)
axes[0].text(74,130,'价格：后一高点更高',ha='center',fontsize=12,color=PURPLE)
macd_panel(axes[1],faded=True)
axes[1].set_ylim(min(hist.min(),dif.min())-.5,dif[m1]+1.45)
axes[1].scatter([m1,m2],dif[[m1,m2]],color=PURPLE,s=45,zorder=5)
axes[1].plot([m1,m2],dif[[m1,m2]],ls='--',color=PURPLE,lw=1.7,zorder=4)
for i in [m1,m2]:axes[1].annotate(f'{dif[i]:.2f}',(i,dif[i]),xytext=(0,9),textcoords='offset points',ha='center',fontsize=11,color=PURPLE)
axes[1].text(82,dif[m1]+.95,'DIF：后一峰值更低',ha='center',fontsize=12,color=PURPLE)
axes[1].set_xlabel('时间／K 线序号 →')
fig.text(.5,.07,'价格峰值与指标峰值的时间可以不同；这里比较的是各段内的峰值。',ha='center',fontsize=10.5,color=GRAY)
fig.text(.5,.025,'这是 MACD 指标背离的示例；缠论背驰还须结合级别、中枢和走势结构判断。',ha='center',fontsize=10.5,color=GRAY)
fig.savefig(OUT/'macd-divergence.png',dpi=170);plt.close(fig)
print(f'Price peaks: bar{p1}={close[p1]:.3f}, bar{p2}={close[p2]:.3f}')
print(f'DIF peaks: bar{m1}={dif[m1]:.3f}, bar{m2}={dif[m2]:.3f}')
print('PASS: price rises to a higher peak while the corresponding later DIF peak is lower; EMA and histogram identities pass.')
