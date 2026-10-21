from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap

ROOT=Path(__file__).parent
d=json.loads((ROOT/'analysis/analysis.json').read_text())
out=ROOT/'outputs'
out.mkdir(parents=True,exist_ok=True)
ss=[s for s in d['stations'] if s['primary']]
names=[s['city'] for s in ss]+['Population-weighted']
def point(city,base):
 return next(r['anomaly'] for r in d['comparisons'] if r['city']==city and r['window']=='Jan–Sep' and r['baseline']==base and r['element']=='tmean_c')
def weighted(base):
 return next(r['anomaly'] for r in d['weighted'] if r['window']=='Jan–Sep' and r['baseline']==base and r['element']=='tmean_c')
a=np.array([point(s['city'],'2000–2025') for s in ss]+[weighted('2000–2025')])
b=np.array([point(s['city'],'1981–2010') for s in ss]+[weighted('1981–2010')])
heat=np.array([[next(r['tmean_c_anomaly'] for r in d['monthly2026'] if r['city']==s['city'] and r['month']==m and r['baseline']=='2000–2025') for m in range(1,10)] for s in ss])
w=np.array([s['population'] for s in ss]);w=w/w.sum()
heat=np.vstack([heat,w@heat])
soi=[next(r['soi'] for r in d['soi'] if r['year']==2026 and r['month']==m) for m in range(1,10)]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.labelcolor':'#243B4A','text.color':'#243B4A','xtick.color':'#526675','ytick.color':'#243B4A'})
fig=plt.figure(figsize=(15,8.3),facecolor='#FAFBFB')
gs=fig.add_gridspec(1,2,width_ratios=[1,1.65],left=.14,right=.975,top=.76,bottom=.23,wspace=.19)
ax=fig.add_subplot(gs[0,0]);hm=fig.add_subplot(gs[0,1]);y=np.arange(9)
ax.set_facecolor('#FAFBFB');ax.hlines(y,a,b,color='#ADBFC5',linewidth=3,zorder=1)
ax.scatter(a,y,color='#246B83',s=65,zorder=3,label='2000–2025')
ax.scatter(b,y,color='#BC623A',s=65,zorder=3,label='1981–2010')
ax.set_yticks(y,names);ax.set_ylim(8.65,-.7);ax.set_xlim(0,1.65);ax.set_xticks([0,.5,1,1.5],['0','+0.5','+1.0','+1.5'])
ax.grid(axis='x',color='#DDE4E7',linewidth=.8);ax.set_axisbelow(True)
ax.set_title('January to September\n2026',loc='left',fontsize=13,pad=28,fontweight='bold')
ax.set_xlabel('Mean temperature anomaly (°C)',labelpad=10)
for spine in ax.spines.values():spine.set_visible(False)
ax.tick_params(length=0,pad=9)
ax.axhline(7.5,color='#C6D2D8',linewidth=1)
for i in [8]:
 ax.text(a[i],i-.23,f'+{a[i]:.2f}',ha='center',color='#246B83',fontweight='bold',fontsize=10)
 ax.text(b[i],i-.23,f'+{b[i]:.2f}',ha='center',color='#BC623A',fontweight='bold',fontsize=10)
ax.legend(loc='lower left',bbox_to_anchor=(-.02,1.015),ncol=2,frameon=False,columnspacing=.8,handletextpad=.3,fontsize=10)
cmap=LinearSegmentedColormap.from_list('climate',['#367C96','#F5F6F3','#C36536'])
im=hm.imshow(heat,cmap=cmap,norm=TwoSlopeNorm(vmin=-2,vcenter=0,vmax=2.5),aspect='auto')
hm.set_title('Month by month\nMean temperature vs 2000–2025',loc='left',fontsize=13,pad=28,fontweight='bold')
hm.set_xticks(range(9),['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep']);hm.xaxis.tick_top();hm.tick_params(length=0,pad=8)
hm.set_yticks([]);hm.set_ylim(8.65,-.7)
for i in range(9):
 for j in range(9):hm.text(j,i,f'{heat[i,j]:+.1f}',ha='center',va='center',fontsize=10,fontweight='bold' if i==8 else 'normal')
hm.set_xticks(np.arange(-.5,9,1),minor=True);hm.set_yticks(np.arange(-.5,9,1),minor=True);hm.grid(which='minor',color='white',linewidth=2);hm.tick_params(which='minor',length=0)
for spine in hm.spines.values():spine.set_visible(False)
hm.axhline(7.5,color='#C6D2D8',linewidth=2)
for j,v in enumerate(soi):hm.text(j,9.45,f'{v:+.1f}',ha='center',va='center',fontsize=10,clip_on=False)
hm.text(-.62,9.45,'SOI',ha='right',va='center',fontsize=10,clip_on=False)
fig.text(.035,.95,'A warmer 2026, with a stronger signal since May',fontsize=23,fontweight='bold')
fig.text(.035,.901,'Eight city proxies · 18.30 million residents · 66.3% of Australia’s population',fontsize=13,color='#526675')
fig.text(.035,.135,'Mean temperature = daily (maximum + minimum) / 2. Population weights: ABS, June 2025. SOI is a separate, unitless monthly index.',fontsize=10,color='#526675')
fig.text(.035,.099,'Sources: BoM station observations distributed by NOAA GHCN-Daily; BoM SOI; ABS population estimates.',fontsize=10,color='#526675')
fig.text(.035,.063,'Adelaide: Parafield. Brisbane: Amberley (Ipswich). Other cities use airports except Hobart (Ellerslie Road). Historical YTD reference: 22–30 valid years.',fontsize=9.5,color='#526675')
fig.text(.035,.028,'Station series are not homogenised. This is a population-weighted station proxy, not a national gridded exposure estimate.',fontsize=9.5,color='#526675')
fig.savefig(out/'Australian_cities_climate_2026.png',dpi=170,facecolor=fig.get_facecolor())
print(out/'Australian_cities_climate_2026.png')
