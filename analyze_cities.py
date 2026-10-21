"""Reproduce the eight-city 2026 comparison from saved public source snapshots.
Python standard library only. Data are observations, not homogenised series.
"""
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict, Counter
from statistics import mean
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import calendar, csv, json, math, re

ROOT=Path(__file__).parent
RAW=ROOT/'raw'; OUT=ROOT/'analysis'; OUT.mkdir(exist_ok=True)
CUTOFF=date(2026,9,30)
SPECS=[
 ('Perth','009021','Perth Airport M.O.',2452765,True),
 ('Adelaide','023013','Parafield Airport',1491015,True),
 ('Melbourne','086282','Melbourne Airport',5435590,True),
 ('Sydney','066037','Sydney Airport AMO',5638830,True),
 ('Brisbane','040004','Amberley AMO',2833524,True),
 ('Darwin','014015','Darwin Airport',159284,True),
 ('Alice Springs','015590','Alice Springs Airport',30875,True),
 ('Hobart','094029','Hobart (Ellerslie Road)',255250,True),
 ('Brisbane check','040211','Archerfield Airport',None,False),
]
BASES={'2000–2025':(2000,2025),'1981–2010':(1981,2010),'1980–1989':(1980,1989)}
KEYS=['tmax_c','tmin_c','tmean_c','rain_mm']
ELEM={'TMAX':'tmax_c','TMIN':'tmin_c','PRCP':'rain_mm'}
WINDOWS=[('Jan–Sep',(1,1),(9,30)),('Jan–Apr',(1,1),(4,30)),
 ('May–Sep',(5,1),(9,30)),('Aug–Sep',(8,1),(9,30))]

def write_csv(name,rows):
 if rows:
  with (OUT/name).open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def agg(rows,expected,threshold):
 r={'expected_days':expected}
 for k in KEYS:
  vals=[x[k] for x in rows if x[k] is not None]
  r[k+'_days']=len(vals)
  enough=len(vals)>= (expected if k=='rain_mm' else math.ceil(expected*threshold))
  r[k]=(sum(vals) if k=='rain_mm' else mean(vals)) if enough else None
 return r

def period_dates(y,start,end):
 ds=[];dt=date(y,*start);stop=date(y,*end)
 while dt<=stop:
  if (dt.month,dt.day)!=(2,29):ds.append(dt)
  dt+=timedelta(days=1)
 return ds

stations=[];daily=[];monthly=[];matched=[];comparisons=[];climos=[];validation=[];qc=[]
for city,bom,name,pop,primary in SPECS:
 ghcn='ASN00'+bom
 raw={}
 for l in (RAW/(ghcn+'.dly')).read_text().splitlines():
  y,m,e=int(l[11:15]),int(l[15:17]),l[17:21]
  if y<1980 or e not in ELEM:continue
  for d in range(1,calendar.monthrange(y,m)[1]+1):
   dt=date(y,m,d)
   if dt>CUTOFF:continue
   a=l[21+8*(d-1):29+8*(d-1)];v=int(a[:5]);v=None if v==-9999 else v/10
   raw[(dt,ELEM[e])]={'raw':v,'qflag':a[6].strip(),'mflag':a[5].strip(),'sflag':a[7].strip(),'source':'GHCN-Daily'}
 bydate={};dt=date(1980,1,1)
 while dt<=CUTOFF:
  r={'city':city,'station_bom':bom,'date':dt.isoformat()}
  for k in ['tmax_c','tmin_c','rain_mm']:
   a=raw.get((dt,k),{'raw':None,'qflag':'','mflag':'','sflag':'','source':'missing'})
   r[k]=a['raw'] if not a['qflag'] else None
   for suffix in ['raw','qflag','mflag','sflag','source']:r[k+'_'+suffix]=a[suffix]
   if a['qflag']:qc.append({'city':city,'date':dt.isoformat(),'element':k,'raw':a['raw'],'qflag':a['qflag']})
  r['tmean_c']=(r['tmax_c']+r['tmin_c'])/2 if r['tmax_c'] is not None and r['tmin_c'] is not None else None
  daily.append(r);bydate[dt]=r;dt+=timedelta(days=1)
 station={'city':city,'station_bom':bom,'station_ghcn':ghcn,'station_name':name,'population':pop,'primary':primary,
  'ghcn_url':'https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/'+ghcn+'.dly',
  'population_geography':'SUA 7001' if city=='Alice Springs' else 'GCCSA' if primary else 'not weighted'}
 stations.append(station)
 sm=[]
 for y in range(1980,2027):
  for m in range(1,13):
   if date(y,m,1)>CUTOFF:continue
   end=min(date(y,m,calendar.monthrange(y,m)[1]),CUTOFF)
   rows=[bydate[date(y,m,d)] for d in range(1,end.day+1)]
   sm.append({'city':city,'station_bom':bom,'year':y,'month':m,'period_end':end.isoformat(),'partial':end.day<calendar.monthrange(y,m)[1],**agg(rows,len(rows),.9)})
 monthly.extend(sm)
 for label,(lo,hi) in BASES.items():
  for m in range(1,13):
   r={'city':city,'baseline':label,'month':m}
   rs=[x for x in sm if lo<=x['year']<=hi and x['month']==m]
   for k in KEYS:
    vs=[x[k] for x in rs if x[k] is not None];r[k]=mean(vs) if vs else None;r[k+'_years']=len(vs)
   climos.append(r)
 for window,start,end in WINDOWS:
  periods=[]
  for y in range(1980,2027):
   dates=period_dates(y,start,end);rows=[bydate[d] for d in dates]
   periods.append({'city':city,'station_bom':bom,'window':window,'year':y,**agg(rows,len(rows),.98)})
  matched.extend(periods);current=periods[-1]
  for label,(lo,hi) in BASES.items():
   for k in KEYS:
    valid=[p for p in periods if lo<=p['year']<=hi and p[k] is not None]
    vals=[p[k] for p in valid];b=mean(vals) if vals else None;v=current[k]
    minimum_reference_years=8 if hi-lo+1==10 else 20
    supported=len(vals)>=minimum_reference_years
    comparisons.append({'city':city,'station_bom':bom,'primary':primary,'window':window,'baseline':label,'element':k,
      'current':v,'baseline_value':b,'anomaly':v-b if v is not None and b is not None and supported else None,
      'ratio':v/b if v is not None and b and supported else None,'current_days':current[k+'_days'],'expected_days':current['expected_days'],
      'baseline_years':len(vals),'baseline_year_list':';'.join(str(p['year']) for p in valid),
      'baseline_coverage_fraction':len(vals)/(hi-lo+1),'supported':supported,
      'warm_rank':1+sum(x>v for x in vals) if k!='rain_mm' and v is not None else None})

# Baseline means and sample counts, kept separate from 2026 observations.
cb={(r['city'],r['baseline'],r['month']):r for r in climos}
monthly2026=[]
for r in monthly:
 if r['year']!=2026 or r['partial']:continue
 for label in BASES:
  b=cb[(r['city'],label,r['month'])]
  q={**r,'baseline':label}
  for k in KEYS:
   q[k+'_baseline']=b[k];q[k+'_baseline_years']=b[k+'_years']
   enough=b[k+'_years']>=(8 if label=='1980–1989' else 20)
   q[k+'_anomaly']=r[k]-b[k] if r[k] is not None and b[k] is not None and enough else None
  monthly2026.append(q)

soi=[]
for line in (RAW/'soi_monthly.txt').read_text().splitlines():
 parts=line.strip().split(',')
 if len(parts)!=2:continue
 ym,v=parts
 if int(ym[:4])>=1980:soi.append({'year':int(ym[:4]),'month':int(ym[4:]),'soi':float(v)})

# ABS source workbook extraction: preserve consistent release and reference date.
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sheet_rows(fn,sheet):
 z=ZipFile(RAW/fn);strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
 out=[]
 for row in ET.fromstring(z.read('xl/worksheets/'+sheet+'.xml')).findall('.//s:row',ns):
  vals={}
  for c in row.findall('s:c',ns):
   v=c.find('s:v',ns);v=v.text if v is not None else ''
   if c.get('t')=='s':v=strings[int(v)]
   vals[re.sub('[0-9]','',c.get('r'))]=v
  out.append(vals)
 return out
national=int(next(r['AA'] for r in sheet_rows('population_all.xlsx','sheet6') if r.get('B')=='Total Australia'))
capitals={r.get('D','').replace('Greater ',''):int(r['AC']) for r in sheet_rows('population_all.xlsx','sheet5') if r.get('D','').startswith('Greater ')}
alice=int(next(r['AA'] for r in sheet_rows('population_sua.xlsx','sheet3') if r.get('A')=='7001'))
for s in stations:
 if s['primary']:assert s['population']==(alice if s['city']=='Alice Springs' else capitals[s['city']])
total=sum(s['population'] for s in stations if s['primary'])
weights={s['city']:s['population']/total for s in stations if s['primary']}
weighted=[]
for window,_,_ in WINDOWS:
 for label in BASES:
  for k in KEYS[:3]:
   rows=[r for r in comparisons if r['primary'] and r['window']==window and r['baseline']==label and r['element']==k]
   complete=all(r['anomaly'] is not None for r in rows)
   weighted.append({'window':window,'baseline':label,'element':k,
    'anomaly':sum(weights[r['city']]*r['anomaly'] for r in rows) if complete else None,
    'current':sum(weights[r['city']]*r['current'] for r in rows) if complete else None,
    'baseline_value':sum(weights[r['city']]*r['baseline_value'] for r in rows) if complete else None,
    'population':total,'national_population':national,'share':total/national})

write_csv('daily_observations_1980_2026.csv',daily)
for name,rows in [('monthly_observations',monthly),('monthly_2026_anomalies',monthly2026),('monthly_climatologies',climos),
 ('matched_periods',matched),('comparisons',comparisons),('population_weighted_proxy',weighted),('stations',stations),
 ('soi_monthly_1980_2026',soi),('bom_archive_overlap_checks',validation),('quality_flags',qc)]:write_csv(name+'.csv',rows)
result={'cutoff':CUTOFF.isoformat(),'stations':stations,'monthly':monthly,'monthly2026':monthly2026,'climatologies':climos,
 'comparisons':comparisons,'weighted':weighted,'soi':soi,'population':{'cities':total,'national':national,'share':total/national},
 'validation':{'overlapping_observations':len(validation),'different_observations':[r for r in validation if abs(r['difference'])>.001]}}
(OUT/'analysis.json').write_text(json.dumps(result,indent=2))
print('POPULATION',result['population'])
print('VALIDATION',result['validation'])
for label in ['Jan–Sep','Jan–Apr','May–Sep','Aug–Sep']:
 print('\n',label)
 for s in stations:
  rr=[r for r in comparisons if r['city']==s['city'] and r['window']==label and r['element']=='tmean_c']
  print(s['city'],[(r['baseline'],round(r['anomaly'],3) if r['anomaly'] is not None else None,r['baseline_years'],r['current_days']) for r in rr])
 print('WEIGHTED',[(r['baseline'],r['element'],round(r['anomaly'],3) if r['anomaly'] is not None else None) for r in weighted if r['window']==label])
