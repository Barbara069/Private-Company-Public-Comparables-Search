"""Execute target-specific peer + website scenarios with a strict target firewall.
Uses only permitted existing snapshots. No target filings/vendor financials enter
its growth calculation. Historical-peer extrapolation is labeled as such.
"""
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlsplit
import csv,datetime,gzip,hashlib,json,math,re,statistics
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'website/data'
WORK=ROOT.parents[2]
VERSION='peer-website-growth-v1-2026-11-20'
CONCEPTS=['Revenues','RevenueFromContractWithCustomerExcludingAssessedTax','SalesRevenueNet','RevenueFromContractWithCustomerIncludingAssessedTax']
def load(name):return json.load(gzip.open(DATA/(name+'.json.gz'),'rt'))
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def host(url):return (urlsplit(url if '://' in url else 'https://'+url).hostname or '').lower().removeprefix('www.')
def website_signals(target):
 domain=host(target['website']);out=[];seen=set()
 for q in target.get('website_quotes',[]):
  url=q.get('url','');text=q.get('text','');domain_q=host(url)
  if not domain or not(domain_q==domain or domain_q.endswith('.'+domain)):continue
  if q.get('source_type')!='OFFICIAL_WEBSITE' or re.search(r'investor|annual.report|10[- ]?[kq]|/sec[/-]|financial.results|earnings.release',url+' '+text,re.I):continue
  norm=re.sub(r'\W+',' ',text.lower()).strip()
  if norm in seen or len(text)<40:continue
  seen.add(norm)
  if re.search(r'closures|shutdown|(?:restaurant|store|factory|location|office).{0,30}clos|clos.{0,25}(?:restaurant|store|factory|locations)|delay|cancel|churn|declin|customer.loss',text,re.I):kind='DOWNSIDE_OPERATIONAL_SIGNAL'
  elif re.search(r'plan.{0,35}(build|open|launch|expand)|will.{0,30}(open|launch|expand)|expanding|expansion|new (?:plant|factory|locations|markets|products)|capacity|backlog|retention',text,re.I):kind='GROWTH_OPPORTUNITY_NOT_QUANTIFIED'
  elif re.search(r'grown|growth|hiring|new faces|customers|restaurants|locations',text,re.I):kind='CONTEXT_ONLY_NO_NUMERIC_EFFECT'
  else:continue
  out.append({'signal_id':'WEB_'+digest([target['target_id'],url,text])[:16],'text':text,'url':url,'source_type':'OFFICIAL_WEBSITE','observed_at':q.get('observed_at','UNKNOWN'),'document_date':q.get('document_date','UNKNOWN'),'classification':kind,'base_log_growth_adjustment':0,'numeric_effect_status':'NO_CALIBRATED_EFFECT; scenario width only for operational signals','text_sha256':hashlib.sha256(text.encode()).hexdigest()})
 return out[:12]
def xbrl_annual(path,meta):
 from lxml import html
 try:root=html.fromstring(path.read_bytes())
 except Exception:return []
 contexts={};facts=defaultdict(lambda:defaultdict(list))
 for e in root.iter():
  if str(e.tag).split(':')[-1].lower()!='context':continue
  if any(str(x.tag).split(':')[-1].lower() in ['explicitmember','typedmember','segment','scenario'] for x in e.iter()):continue
  ds={str(x.tag).split(':')[-1].lower():x.text for x in e.iter() if str(x.tag).split(':')[-1].lower() in ['startdate','enddate']}
  try:
   if 300<=(datetime.date.fromisoformat(ds['enddate'])-datetime.date.fromisoformat(ds['startdate'])).days<=400:contexts[e.get('id')]=ds
  except Exception:pass
 for e in root.iter():
  name=e.get('name') or '';concept=name.split(':')[-1];ctx=e.get('contextref');unit=e.get('unitref') or ''
  if not name.startswith('us-gaap:') or concept not in CONCEPTS or ctx not in contexts:continue
  if not unit.lower().startswith('usd'):continue
  text=''.join(e.itertext()).strip()
  try:
   val=float(re.sub('[^0-9.-]','',text))*10**int(e.get('scale','0'))
   if e.get('sign')=='-':val=-val
   if not math.isfinite(val) or val<=0:continue
  except Exception:continue
  ds=contexts[ctx];facts[concept][ds['enddate']].append({'period':ds['enddate'][:4],'period_end':ds['enddate'],'start':ds['startdate'],'value':val,'currency':'USD','source':'SEC_INLINE_XBRL','source_url':meta['annual_filing_url'],'source_date':meta.get('filing_date'),'record_locator':f'{name}; contextRef={ctx}; unitRef={unit}; scale={e.get("scale","0")}','raw_text':text,'file_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 for concept in CONCEPTS:
  selected=[]
  for date,rs in facts[concept].items():
   vals={r['value'] for r in rs}
   if len(vals)==1:selected.append(rs[0])  # conflicting contexts are not averaged
  if len(selected)>=2:return sorted(selected,key=lambda x:x['period_end'])[-5:]
 return []
def peer_paths(series,guidance=None):
 series=sorted([r for r in series if r['value'] and r['value']>0],key=lambda r:r['period_end'])
 if len(series)<2 or int(series[-1]['period_end'][:4])<2023:return None
 changes=[]
 for a,b in zip(series,series[1:]):
  days=(datetime.date.fromisoformat(b['period_end'])-datetime.date.fromisoformat(a['period_end'])).days
  if 300<=days<=400:changes.append(math.log(b['value']/a['value']))
 if not changes:return None
 g=statistics.median(changes[-3:])
 if not -.70<math.expm1(g)<1.50:return None
 return {'historical_log_growth':g,'historical_changes':changes,'series':series,'guidance':guidance}
def build_target(target,selected,series,guidance,growth_profiles,own_key):
 allowed={'target_id','target_name','website','available_financials','financial_provenance','website_quotes','status','matching_input_allowlist','treatment'}
 if set(target)-allowed:raise ValueError('Unapproved target fields in forecasting bundle')
 if set(target.get('available_financials',{}))-{'revenue','ebitda','debt'}:raise ValueError('Unapproved target financial fields')
 signals=website_signals(target);op=sum(x['classification']=='GROWTH_OPPORTUNITY_NOT_QUANTIFIED' for x in signals);risk=sum(x['classification']=='DOWNSIDE_OPERATIONAL_SIGNAL' for x in signals)
 base={'target_id':target['target_id'],'company_name':target['target_name'],'canonical_key':own_key,'version':VERSION,'baseline_year':2026,'years':[2027,2028,2029,2030,2031],
 'allowed_inputs':{'website':target['website'],'available_financials':target.get('available_financials',{}),'financial_provenance':target.get('financial_provenance',{}),'allowed_source_types':['INSTRUCTOR_WORKBOOK','OFFICIAL_WEBSITE'],'excluded':['TARGET_SEC','TARGET_VENDOR_FINANCIAL_HISTORY','TARGET_MARKET_CAP','TARGET_CONSENSUS','TARGET_ACTUAL_MULTIPLES','TARGET_CASH']},
 'website_signals':signals,'target_website_base_adjustment':0,'target_signal_method':'Website operational opportunities/risks expand upside/downside log-growth sensitivities by 50% of the empirical peer dispersion. This is an explicit analyst assumption, not a fitted causal effect. Unquantified website statements do not increase the base forecast.',
 'input_hash':digest({'target':target,'selected':selected}),'source_snapshot':'Existing LSEG snapshot 2026-10-28 and retained peer SEC/IR documents through 2026-11-16; not a live data refresh.'}
 total=sum(max(float(p['Ranking Score']),0)**2 for p in selected);peers=[];excluded=[]
 for p in selected:
  key=p['Canonical Company ID'];name=p['Candidate Name'];weight=max(float(p['Ranking Score']),0)**2
  if key==own_key:excluded.append({'name':name,'reason':'SAME_ECONOMIC_ISSUER_AS_TARGET'});continue
  model=peer_paths(series.get(key,[]),guidance.get(key))
  if not model:excluded.append({'name':name,'reason':'NO_USABLE_CONSOLIDATED_ANNUAL_REVENUE_SERIES'});continue
  public_signals=[s for s in growth_profiles.get(key,{}).get('signals',[]) if s['category'] in ['reported_growth','guidance','expansion','pricing','capacity']][:5]
  growth_quality=.5 if any(re.search(r'acquisition|acquired|merger|dispos',s['text'],re.I) for s in public_signals) else 1.
  peers.append({'key':key,'name':name,'ric':p['Candidate RIC'],'rank':p.get('Rank',p.get('Candidate Order')),'ranking_score':p['Ranking Score'],'similarity_percent':p['Similarity Percent'],'raw_weight':weight,'growth_quality_factor':growth_quality,'quality_note':'M&A/disposal exposure in peer growth passages: weight halved; reported growth is not organic' if growth_quality<1 else 'No M&A/disposal detected in selected growth passages; not a full organic-growth audit','model':model,'growth_signals':public_signals,'selection_status':'EXISTING_PROVISIONAL_COMPS_NOT_FINAL_REVIEWED'})
 covered=sum(p['raw_weight'] for p in peers)/total if total else 0
 base.update(excluded_peers=excluded,selected_peer_count=len(selected),financial_peer_count=len(peers),weighted_peer_data_coverage=covered)
 if not signals or len(peers)<2 or covered<.20:
  base.update(status='INSUFFICIENT_PERMITTED_EVIDENCE',reason='Need target official-website evidence and at least two selected independent peers with usable annual revenue and >=20% of selected-basket score weight. Missing inputs are not replaced with generic growth rates.',peers=[{k:v for k,v in p.items() if k!='model'} for p in peers],scenarios={});return base
 total_ok=sum(p['raw_weight']*p['growth_quality_factor'] for p in peers)
 for p in peers:p['weight']=p['raw_weight']*p['growth_quality_factor']/total_ok
 anchor=statistics.median(p['model']['historical_log_growth'] for p in peers)
 vals=[x for p in peers for x in p['model']['historical_changes']];dispersion=statistics.pstdev(vals) if len(vals)>1 else 0
 # No fixed 0/5/10 path: company basket, observed growth and dispersion determine scenarios.
 peer_calendar={};assumptions=[]
 for p in peers:
  model=p['model'];annual=model['series'];last=annual[-1];end_month=int(last['period_end'][5:7]);levels={int(r['period']):r['value'] for r in annual};g=model['historical_log_growth'];kind='HISTORICAL_PEER_GROWTH_EXTRAPOLATION_NOT_CONSENSUS'
  if model['guidance']:
   gd=model['guidance'];levels.update({int(y):float(v) for y,v in gd['revenue_levels'].items()});end_month=gd['fiscal_end_month'];kind='DATED_PEER_GUIDANCE_THEN_EXPLICIT_FADE'
   ly=max(levels);g=math.log(levels[ly]/levels[ly-1]) if ly-1 in levels else g;p['guidance_source_ids']=gd['source_ids']
  lasty=max(levels)
  for y in range(lasty+1,2033):
   if y>=2027:g=anchor+.6*(g-anchor)
   levels[y]=levels[y-1]*math.exp(g)
  cal={}
  for year in range(2026,2032):
   if end_month==12:cal[year]=levels.get(year)
   else:cal[year]=(end_month/12)*levels[year]+(1-end_month/12)*levels[year+1]
  peer_calendar[p['key']]=cal;p['forecast_basis']=kind;p['revenue_history']=annual;p['calendarization']='Fiscal-end-month weighted adjacent fiscal years; uniform within-year approximation';p['growth_path']=[{'year':y,'growth':cal[y]/cal[y-1]-1} for y in range(2027,2032)]
  p['historical_growth_reference']=math.expm1(model['historical_log_growth']);del p['model'];del p['raw_weight']
 mu={y:sum(p['weight']*math.log(peer_calendar[p['key']][y]/peer_calendar[p['key']][y-1]) for p in peers) for y in range(2027,2032)}
 paths={}
 for scenario,sign,scale in [('bear',-1,1+.5*bool(risk)),('base',0,0),('bull',1,1+.5*bool(op))]:
  idx=100.;path=[{'year':2026,'revenue_index':100.,'growth':None,'peer_reference_growth':None,'website_scenario_adjustment':0}]
  for y in range(2027,2032):
   delta=sign*scale*dispersion*.5**((y-2027)/2);growth=math.expm1(mu[y]+delta);idx*=1+growth
   path.append({'year':y,'revenue_index':idx,'growth':growth,'peer_reference_growth':math.expm1(mu[y]),'website_scenario_adjustment':delta})
  paths[scenario]=path
 base.update(status='PROVISIONAL_PEER_WEBSITE_FORECAST',reason='Executed company-specific peer-plus-website scenarios; proxy peer selection and historical extrapolation are not calibrated forecast accuracy.',peers=peers,scenarios=paths,
 assumptions={'peer_weights':'Ranking Score squared × growth-quality factor (0.5 for M&A/disposal flagged in retained peer growth passages, otherwise 1), normalized over fixed financially usable selected peers; exclusions and lost basket weight disclosed. Not calibrated probabilities.','long_run_log_growth_anchor':anchor,'anchor_basis':'Median historical log growth of this selected peer basket, not a universal economy/industry forecast','fade_persistence':.6,'empirical_log_growth_dispersion':dispersion,'website_upside_multiplier':1+.5*bool(op),'website_downside_multiplier':1+.5*bool(risk),'website_signal_half_life_years':2,'target_financial_baseline':'Only instructor revenue/EBITDA/debt shown. Unknown units/period block a dated currency forecast; index 2026=100 is conditional.'},
 effective_peer_count=1/sum(p['weight']**2 for p in peers),calibration='NOT_PERFORMED',self_history_used=False)
 return base

def append_master_csv(payload,path):
 import os
 if not path.exists():return
 csv.field_size_limit(100_000_000);tmp=path.with_suffix(path.suffix+'.tmp')
 datasets={'Pseudo_Private_Growth_Forecasts','Target_Website_Growth_Signals','Peer_Growth_Financial_Observations'}
 with gzip.open(path,'rt',newline='') as old,gzip.open(tmp,'wt',newline='') as out:
  reader=csv.DictReader(old);writer=csv.DictWriter(out,fieldnames=reader.fieldnames);writer.writeheader()
  for row in reader:
   if row['dataset'] not in datasets:writer.writerow(row)
  seen=set()
  for tid,f in payload['targets'].items():
   writer.writerow({'dataset':'Pseudo_Private_Growth_Forecasts','company_id':tid,'company_name':f['company_name'],'entity_role':'PSEUDO_PRIVATE_TARGET','source_date':payload['as_of'],'record_json':json.dumps(f,separators=(',',':'))})
   for signal in f['website_signals']:
    writer.writerow({'dataset':'Target_Website_Growth_Signals','company_id':tid,'company_name':f['company_name'],'entity_role':'PSEUDO_PRIVATE_TARGET','source_url':signal['url'],'source_date':signal['observed_at'],'text':signal['text'],'record_json':json.dumps(signal,separators=(',',':'))})
   for peer in f['peers']:
    for obs in peer.get('revenue_history',[]):
     key=(peer['key'],obs['period_end'],obs['source_url'],obs['value'])
     if key in seen:continue
     seen.add(key);writer.writerow({'dataset':'Peer_Growth_Financial_Observations','company_id':peer['key'],'company_name':peer['name'],'entity_role':'PUBLIC_PEER','facet':'Consolidated revenue','source_url':obs['source_url'],'source_date':obs['source_date'],'text':obs['raw_text'],'record_json':json.dumps(obs,separators=(',',':'))})
 os.replace(tmp,path)

def main():
 catalog=load('research_catalog')['companies'];inputs=load('comparison_inputs');manifest=load('comparison_rebuild_manifest');financial=load('financial_history');refresh=json.load(open(DATA/'research_refresh_20261112.json'));prototype=load('private_forecast_prototype')
 aliases={a:c['key'] for c in catalog for a in [c.get('id'),*c.get('original_target_ids',[]),*c.get('rics',[])] if a};growth_profiles={};ci_keys={}
 for shard in set(refresh['growth_company_shards'].values()):growth_profiles.update(load('growth/group_'+shard))
 for key,profile in growth_profiles.items():
  for s in profile.get('signals',[]):
   match=re.search(r'/edgar/data/(\d+)/',s['source'].get('url',''))
   if match:ci_keys[int(match[1])]=key;break
 series={k:[{'period':r['period'].removeprefix('FY'),'period_end':r['period_end'],'value':r['values']['revenue'],'currency':r['currency'],'source':r['source'],'source_url':r['source_url'],'source_date':r.get('retrieved_at'),'record_locator':'TR.TOTALREVENUE; '+r['period'],'raw_text':str(r['values']['revenue'])} for r in rows if r['values']['revenue']] for k,rows in financial['companies'].items()}
 groups={g:load(g) for g in set(manifest['groups'].values())};needed={p['Canonical Company ID'] for group in groups.values() for ps in group.values() for p in ps}
 index=json.loads((WORK/'outputs/global_comps_560/web_evidence/sec_index.json').read_text());parsed=0
 for meta in index:
  if not meta.get('cik'):continue
  key=ci_keys.get(int(meta['cik'])) or aliases.get(meta.get('company_id'))
  if not key or key not in needed:continue
  path=WORK/f'outputs/global_comps_560/web_evidence/sec/{int(meta["cik"])}_annual.html'
  if not path.exists() or not meta.get('annual_filing_url'):continue
  obs=xbrl_annual(path,meta)
  if obs:series[key]=obs;parsed+=1
 guidance={};ref_sources={s['source_id']:s for s in prototype['source_observations']}
 for p in prototype['config']['peers']:
  matches={c['key'] for c in catalog if any(r.split('.')[0]==p['issuer_id'] for r in c.get('rics',[]))}
  if len(matches)==1:guidance[next(iter(matches))]=p
 out={}
 for tid,t in inputs.items():
  own=aliases.get(tid);selected=groups.get(manifest['groups'].get(tid),{}).get(tid,[]);out[tid]=build_target(t,selected,series,guidance,growth_profiles,own)
 for tid,f in out.items():
  rev=f['allowed_inputs']['available_financials'].get('revenue')
  for path in f['scenarios'].values():
   for row in path:row['conditional_revenue_original_units']=None if rev is None else rev*row['revenue_index']/100
 stats={'targets':len(out),'executed':sum(x['status']=='PROVISIONAL_PEER_WEBSITE_FORECAST' for x in out.values()),'abstained':sum(not x['scenarios'] for x in out.values()),'peer_SEC_series_extracted':parsed,'target_source_firewall':'INSTRUCTOR_REVENUE_EBITDA_DEBT_AND_OFFICIAL_BUSINESS_WEBSITE_ONLY'}
 payload={'version':VERSION,'as_of':'2026-11-20','stats':stats,'targets':out,'target_by_key':{v['canonical_key']:tid for tid,v in out.items() if v['canonical_key']},'peer_guidance_sources':{k:v for k,v in ref_sources.items() if not v.get('issuer_id','').startswith('GC_')}}
 with gzip.GzipFile(filename=str(DATA/'target_growth_forecasts.json.gz'),mode='wb',mtime=0) as f:f.write(json.dumps(payload,separators=(',',':')).encode())
 # Keep derived forecasts and source observations inside the comprehensive CSV.
 append_master_csv(payload,ROOT.parent/'Research_Data.csv.gz')
 print(json.dumps(stats));print('Wendy',json.dumps({k:out['IQ23557'].get(k) for k in ['status','financial_peer_count','weighted_peer_data_coverage','effective_peer_count']}));print('Wendy base',out['IQ23557']['scenarios'].get('base'))
if __name__=='__main__':main()
