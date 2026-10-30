"""Read-only preparation of the user's 560-company sources.

This stage does not claim to have researched global comparable companies.
Preserves source cells, missingness, duplicate labels and observation dates.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv, datetime as dt, hashlib, json, math, re, zipfile
import openpyxl

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'sources'
OUT = ROOT / 'prepared'
OUT.mkdir(exist_ok=True)
ASOF = dt.datetime(2026, 10, 27)
LINKS = {
 'capiq':'https://drive.google.com/file/d/1cJwV_NyfypLGy59GsNmKSjj0XhYJQs13/view',
 'wrds':'https://drive.google.com/file/d/14NvyjcLDPbrm4fGh03xJpMrAJ9Q-VeqB/view',
 'ff49':'https://drive.google.com/file/d/1YOpOHcT2RQAZYt4SZoITthOI67ypJzeF/view',
 'mapping':'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Siccodes49.zip'}

def clean(v):
 if isinstance(v, (dt.datetime,dt.date)): return v.isoformat()[:10]
 if isinstance(v,float) and not math.isfinite(v): return None
 return v

def dump(name, rows):
 rows=[{k:clean(v) for k,v in r.items()} for r in rows]
 (OUT/(name+'.json')).write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
 if rows:
  with (OUT/(name+'.csv')).open('w',newline='',encoding='utf-8-sig') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 return rows

def unique_headers(headers):
 count=Counter();out=[]
 for i,h in enumerate(headers,1):
  h=str(h or 'Unnamed_'+str(i));count[h]+=1
  out.append(h if count[h]==1 else h+' [duplicate '+str(count[h])+']')
 return out

cap=openpyxl.load_workbook(SRC/'capiq.xlsx',read_only=True,data_only=True)
tables={};source_cells=[]
for sh in cap:
 vals=sh.values;headers=unique_headers(next(vals));rows=[]
 for ri,vals in enumerate(vals,2):
  row=dict(zip(headers,vals));row['_source_row']=ri;rows.append(row)
  if sh.title=='Match notes':continue
  for ci,(h,v) in enumerate(zip(headers,vals),1):
   if v is not None:
    source_cells.append({'company_id':row.get('IQ_COMPANY_ID'),'ticker':row.get('ticker'),
     'field':h,'value':clean(v),'source':'CapIQ_560.xlsx','sheet':sh.title,
     'cell':openpyxl.utils.get_column_letter(ci)+str(ri),'source_url':LINKS['capiq'],
     'observation_date':'UNKNOWN unless specified by the field','extracted_on':ASOF.date().isoformat()})
 tables[sh.title]=rows
 dump('CapIQ_'+re.sub('[^A-Za-z0-9]+','_',sh.title),rows)
descriptions=tables['Business Description']
assert len(descriptions)==560 and len({r['IQ_COMPANY_ID'] for r in descriptions})==560
lookup={s:{r['IQ_COMPANY_ID']:r for r in rows} for s,rows in tables.items() if s!='Match notes'}

# Official FF49 definitions. Valid unassigned four-digit SICs go to Other;
# invalid/missing input remains UNKNOWN.
z=zipfile.ZipFile(SRC/'Siccodes49.zip')
definition=z.read('Siccodes49.txt').decode('utf-8-sig')
(SRC/'Siccodes49.txt').write_text(definition)
ranges=[];group=None
for line in definition.splitlines():
 m=re.match(r'^\s*(\d{1,2})\s+([A-Za-z]+)\s+(.+)',line)
 if m:group=(int(m[1]),m[2].upper(),m[3].strip());continue
 m=re.match(r'^\s*(\d{4})-(\d{4})\s*(.*)',line)
 if m and group:ranges.append({'sic_from':int(m[1]),'sic_to':int(m[2]),'ff49_id':group[0],
  'ff49':group[1],'industry_name':group[2],'range_description':m[3],'source_url':LINKS['mapping']})
dump('FF49_SIC_Mapping',ranges)
def ffmap(sic):
 try: v=int(str(sic).strip())
 except (ValueError,TypeError):return None,None,None,'INVALID_OR_MISSING_SIC'
 if not 100<=v<=9999:return None,None,None,'INVALID_OR_MISSING_SIC'
 hits=[r for r in ranges if r['sic_from']<=v<=r['sic_to']]
 if len(hits)>1:raise ValueError(('overlapping mapping',sic))
 if hits:
  r=hits[0];return r['ff49_id'],r['ff49'],r['industry_name'],'EXPLICIT_RANGE'
 return 49,'OTHER','Almost Nothing','VALID_SIC_REMAINDER_OTHER'

ffw=openpyxl.load_workbook(SRC/'ff49.xlsx',read_only=True,data_only=True)
ffsh=ffw.active;vals=ffsh.values;ffheaders=unique_headers(next(vals));ffrows=[]
for ri,v in enumerate(vals,2):
 row=dict(zip(ffheaders,v));row['_source_row']=ri;ffrows.append(row)
ffd=defaultdict(dict)
for r in ffrows:ffd[r[ffheaders[1]]][r['Date']]=r
latest_ff=max(r['Date'] for r in ffrows if r['Date']<=ASOF)
fflatest=[r for r in ffrows if r['Date']==latest_ff]
assert len(fflatest)==49
dump('FF49_Latest_49',fflatest)

# Inspect the whole history instead of trusting the pre-made Latest Ratios tab.
wr=openpyxl.load_workbook(SRC/'wrds.xlsx',read_only=True,data_only=True)
sh=wr['10 Years'];vals=sh.values;wrheaders=unique_headers(next(vals));latest={};ties=Counter();n_history=0
for ri,v in enumerate(vals,2):
 n_history+=1;r=dict(zip(wrheaders,v));r['_source_row']=ri
 if not isinstance(r.get('Date'),dt.datetime) or r['Date']>ASOF:continue
 ticker=str(r.get('Ticker') or '').strip().upper();gv=str(r.get('Global Company Key') or '')
 if not ticker:continue
 key=(ticker,gv)
 if key not in latest or r['Date']>latest[key]['Date']:latest[key]=r
 elif r['Date']==latest[key]['Date']:ties[key]+=1
by_ticker=defaultdict(list)
for (t,g),r in latest.items():by_ticker[t].append(r)

def norm(s):
 s=re.sub(r'\([^)]*\)','',str(s or '')).casefold()
 s=re.sub(r'\b(incorporated|inc|corporation|corp|company|co|limited|ltd|plc|the)\b','',s)
 return re.sub('[^a-z0-9]','',s)

facets=[('Primary Products',12),('Primary Services',12),('Core Business Activity',16),
 ('Customer Segment',12),('End Markets',5),('Business Model',8),('Revenue Model',10),
 ('Value Chain Position',8),('Geography Served',3),('Company Size Category',3),
 ('Product Specialization',2),('Customer Concentration',0),('Distribution Channels',2),
 ('Delivery Model',2),('Pricing Structure',0),('Recurring Revenue Profile',0),
 ('Capital Intensity',2),('Labor Intensity',0),('Regulatory Exposure',1),
 ('Competitive Positioning',0),('Product Differentiation',0),('Customer Switching Costs',0),
 ('Revenue Cyclicality',0),('Company Maturity',0),('Technology Dependence',0),
 ('Geographic Concentration',0),('Supply Chain Complexity',0),('Contract Duration',0),
 ('IP Dependence',0),('Brand Dependence',0),('FF49 Industry',2)]
assert sum(w for _,w in facets)==100
dump('Scoring_Weights',[{'facet':f,'proposed_weight':w/100,
 'status':'PROPOSED_NOT_CALIBRATED','score_scale':'0,25,50,75,100; UNKNOWN/NOT_APPLICABLE excluded',
 'missing_rule':'No shared-none bonus; report weighted coverage; do not auto-accept with missing core evidence',
 'note':'0-weight facets retained as context; sector-specific scoring awaits calibration'} for f,w in facets])

# Conservative source excerpts, not fictional categories. Full source description
# is retained. No claim that these regex excerpts replace semantic review.
records=[];masters=[];wrmatched=[];benchmarks=[];reviews=[]
for d in descriptions:
 iq=d['IQ_COMPANY_ID'];t=d['ticker'];name=d['company_name_original'];fi,ff,fn,mapstatus=ffmap(d['sic4'])
 text=str(d.get('Business Description') or '');sentences=re.split(r'(?<=[.;])\s+(?=[A-Z])',text)
 def evidence(pattern):return ' '.join(s for s in sentences if re.search(pattern,s,re.I)) or None
 ev={
 'Primary Products':evidence(r'\b(products?|offers?|manufactures?|produces?|sells?)\b'),
 'Primary Services':evidence(r'\b(services?|consulting|outsourc|franchis|repair|maintenance)\b'),
 'Core Business Activity':sentences[0] if sentences else None,
 'Customer Segment':evidence(r'\b(customers?|clients?|serves?|consumers?|employers?|institutions?|patients?)\b'),
 'End Markets':evidence(r'\b(markets?|industries|sectors?)\b'),
 'Business Model':evidence(r'\b(operates?|engages?|provides?|manufactures?|franchises?)\b'),
 'Revenue Model':evidence(r'\b(revenue|fees?|royalties|subscriptions?|commissions?|licens|rental|leasing|premiums?)\b'),
 'Value Chain Position':evidence(r'\b(manufactur|distribut|retail|franchis|platform|broker|producer|supplier)\w*'),
 'Geography Served':evidence(r'\b(United States|Canada|Europe|Asia|internationally|worldwide|globally|countries)\b'),
 'Product Specialization':evidence(r'\b(segments?|businesses|divisions?)\b'),
 'Distribution Channels':evidence(r'\b(through|channels?|distributors?|representatives?|dealers?|sales force)\b'),
 'Delivery Model':evidence(r'\b(cloud|on-premise|online|in-store|delivery|drive-thr|hosted)\w*'),
 'Pricing Structure':evidence(r'\b(per.employee|per.user|per.seat|fixed.fee|hourly|pricing)\b'),
 'Recurring Revenue Profile':evidence(r'\b(recurring|subscriptions?|renewal)\w*'),
 'Regulatory Exposure':evidence(r'\b(regulat|FDA|Medicare|licensed|compliance)\w*'),
 'Contract Duration':evidence(r'\b(multiyear|multi.year|long.term contract|annual contract)\b'),
 'IP Dependence':evidence(r'\b(patent|proprietary|intellectual property)\w*')}
 rnum=d['_source_row'];src_cell='J'+str(rnum)
 key=lookup['Key Financials'].get(iq,{})
 capex=key.get('CY2025 Capital Expenditure');rev=key.get('CY2025 Total Revenue')
 capratio=abs(capex)/rev if isinstance(capex,(int,float)) and isinstance(rev,(int,float)) and rev>0 else None
 for f,w in facets:
  value=ev.get(f);status='SOURCE_EXCERPT_REQUIRES_REVIEW' if value else 'UNKNOWN'
  loc=f"Business Description!{src_cell}";url=LINKS['capiq'];note='Exact source excerpt; not web-verified or normalized.'
  if f=='Company Size Category':
   v=d.get('Global No. of Employees');value='Employees: '+str(v) if v is not None else None
   status='SOURCE_RAW_VALUE_NO_SIZE_CATEGORY' if value else 'UNKNOWN';loc=f'Business Description!N{rnum}';note='No unvalidated small/mid/large threshold applied.'
  if f=='Capital Intensity':
   value=capratio;status='DERIVED_CAPEX_REVENUE_PROXY' if value is not None else 'UNKNOWN'
   loc=f"Key Financials!AA{key.get('_source_row')},J{key.get('_source_row')}";note='abs(CY2025 CapEx)/CY2025 Revenue; raw source signs retained elsewhere. Units must be consistent; not a verified qualitative category.'
  if f=='FF49 Industry':value=ff;status=mapstatus;loc=f'Business Description!G{rnum}; Siccodes49.txt';url=LINKS['mapping'];note='SIC-based company classification, not segment revenue composition.'
  records.append({'company_id':iq,'ticker':t,'company_name':name,'facet':f,'value_or_excerpt':value,
   'status':status,'proposed_weight':w/100,
   'information_source':'WEB_OFFICIAL_FF49_DEFINITION' if f=='FF49 Industry' else 'PROVIDED_CAPITAL_IQ_EXCEL',
   'source_scope':'INDUSTRY_CLASSIFICATION' if f=='FF49 Industry' else 'COMPANY',
   'source_workbook':'Siccodes49.txt' if f=='FF49 Industry' else 'CapIQ_560.xlsx',
   'source_url':url,'source_location':loc,
   'source_date':'UNKNOWN','retrieved_on':ASOF.date().isoformat(),'note':note})
 choices=by_ticker.get(str(t).upper(),[])
 # Historical ticker alone is not enough: require normalized name consistency and
 # a single GVKEY. Keep ambiguous historical entities out of comparisons.
 valid=[r for r in choices if norm(r.get('Company Name'))==norm(name)]
 if len(choices)==1 and len(valid)==1:wrrow=valid[0];match='TICKER_AND_NAME_CONSISTENT_NOT_IDENTIFIER_AUDITED'
 elif len(choices)==0:wrrow=None;match='NO_EXACT_TICKER'
 else:wrrow=None;match='AMBIGUOUS_OR_NAME_MISMATCH_REQUIRES_ID_REVIEW'
 if wrrow:
  wrmatched.append({'company_id':iq,'target_ticker':t,'match_status':match,**wrrow})
 display=re.sub(r'\s*\([^)]*\)\s*$','',str(d.get('Company Name') or ''))
 identity='NAME_DIFFERENCE_REVIEW' if norm(display)!=norm(name) else 'SOURCE_NAME_CONSISTENT'
 master={'company_id':iq,'ticker':t,'company_name':name,'capiq_display_name':d.get('Company Name'),
  'website':d.get('Website'),'exchange':d.get('exchange'),'sic4':str(d['sic4']).zfill(4),
  'ff49':ff,'ff49_name':fn,'ff49_mapping_status':mapstatus,'capiq_identity_status':identity,
  'business_description':text,'country':d.get('Country/Region'),'employees':d.get('Global No. of Employees'),
  'founded':d.get('Year Founded'),'source_company_status':d.get('Company Status'),
  'wrds_match_status':match,'wrds_ratio_date':wrrow.get('Date') if wrrow else None,
  'ff49_latest_date':latest_ff,'global_comp_research_status':'NOT_YET_RESEARCHED',
  'facet_status':'SOURCE_EXCERPTS_ONLY_NOT_FINAL','source_url':LINKS['capiq'],
  'source_location':f'Business Description!A{rnum}:X{rnum}'}
 for sheet in ['Key Financials','Financial Data','Trading Multiples','Operating Statistics','Credit Health Panel']:
  for col,val in lookup.get(sheet,{}).get(iq,{}).items():
   if col not in ['IQ_COMPANY_ID','company_name_original','ticker','exchange','sic2','sic3','sic4','primary_sic_industry','Company Name','_source_row']:
    master[sheet+' | '+col]=val
 a=key.get('CY2025 Total Revenue');b=key.get('CY2022 Total Revenue')
 master['Derived CY2022–2025 revenue CAGR']=(a/b)**(1/3)-1 if isinstance(a,(int,float)) and isinstance(b,(int,float)) and a>0 and b>0 else None
 master['Derived abs CY2025 CapEx / revenue']=capratio
 masters.append(master)
 industry=ffd.get(ff,{})
 bench=industry.get(latest_ff)
 br={'company_id':iq,'ticker':t,'company_name':name,'ff49':ff,'benchmark_date':latest_ff,
  'NFIRM':bench.get('NFIRM') if bench else None,'wrds_company_date':wrrow.get('Date') if wrrow else None,
  'source_url':LINKS['ff49'],'source_sheet':ffsh.title,'source_row':bench.get('_source_row') if bench else None,
  'date_alignment':'SAME_MONTH' if wrrow and wrrow['Date']==latest_ff else 'DO_NOT_COMPARE_AS_CONTEMPORANEOUS'}
 if bench:
  for h,v in bench.items():
   if h.endswith('_Median') or '_Median [duplicate' in h:br[h]=v
 benchmarks.append(br)
 # Generate date-aligned metric comparison records, keeping all targets and gaps.
 reasons=[]
 if identity!='SOURCE_NAME_CONSISTENT':reasons.append(identity)
 if wrrow is None:reasons.append(match)
 elif wrrow['Date']!=latest_ff:reasons.append('WRDS_LAST_DATE_DIFFERS_FROM_2025_12_31')
 if ff is None:reasons.append(mapstatus)
 reviews.append({'company_id':iq,'ticker':t,'company_name':name,'data_review':'; '.join(reasons) or 'NO_FLAG_IN_PREPARATION',
  'facet_review':'NOT_WEB_VERIFIED','comps_review':'NOT_YET_RESEARCHED',
  'suggested_query':f'{display or name} competitors public companies same products customers business model'})

# Consistent schema despite missing fields in some credit records.
allkeys=list(dict.fromkeys(k for r in masters for k in r))
masters=[{k:r.get(k) for k in allkeys} for r in masters]
dump('Targets_560',masters);dump('Target_Facet_Evidence',records);dump('FF49_Benchmarks_560',benchmarks)
dump('WRDS_Matched_Latest',wrmatched);dump('Review_Queue',reviews)
dump('CapIQ_Field_Provenance',source_cells)
comparison=[]
wrbyid={r['company_id']:r for r in wrmatched}
for m in masters:
 w=wrbyid.get(m['company_id']);industry=ffd.get(m['ff49'],{});b=industry.get(w['Date']) if w else None
 for h in ffheaders:
  if not (h.endswith('_Median') or '_Median [duplicate' in h):continue
  metric=h.replace('_Median','');ambiguous='[duplicate' in metric or (metric+' [duplicate 2]') in wrheaders
  v=w.get(metric) if w and not ambiguous else None;med=b.get(h) if b else None
  numeric=lambda x:isinstance(x,(int,float)) and not isinstance(x,bool)
  delta=v-med if numeric(v) and numeric(med) else None
  comparison.append({'company_id':m['company_id'],'ticker':m['ticker'],'ff49':m['ff49'],
   'metric':metric,'company_ratio_date':w['Date'] if w else None,'company_value':v,
   'industry_median_same_date':med,'difference':delta,
   'status':'AMBIGUOUS_DUPLICATE_METRIC' if ambiguous else 'COMPARABLE_SAME_MONTH' if delta is not None else 'MISSING_OR_UNMATCHED',
   'company_source_url':LINKS['wrds'],'company_source_location':f"10 Years!row {w['_source_row']}" if w else None,
   'industry_source_url':LINKS['ff49'],'industry_source_location':f"{ffsh.title}!row {b['_source_row']}" if b else None})
dump('Date_Aligned_Comparisons',comparison)
manifest=[]
for key in ['capiq','wrds','ff49']:
 p=SRC/(key+'.xlsx');manifest.append({'source_key':key,'source_url':LINKS[key],
  'local_file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
  'retrieved_on':ASOF.date().isoformat(),'note':'Downloaded original file; no Drive modifications.'})
dump('Source_Manifest',manifest)
summary={'targets':len(masters),'facet_records':len(records),'financial_source_cells':len(source_cells),
 'ff49_industries':len(fflatest),'ff49_latest_date':latest_ff.date().isoformat(),
 'ff49_mapped_targets':sum(bool(r['ff49']) for r in masters),'wrds_history_rows':n_history,
 'wrds_unambiguous_ticker_name_matches':len(wrmatched),
 'wrds_match_status':dict(Counter(m['wrds_match_status'] for m in masters)),
 'capiq_identity_status':dict(Counter(m['capiq_identity_status'] for m in masters)),
 'date_aligned_comparison_values':sum(r['difference'] is not None for r in comparison),
 'global_comps_researched_targets':0,'final_scored_targets':0}
(OUT/'progress.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
