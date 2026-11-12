"""Resumable evidence extraction, not a claim of independent fact verification.
Research only: never opens restricted target snapshots or matching score inputs.
"""
from pathlib import Path
import collections,csv,datetime,gzip,hashlib,json,re,sys,time
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'outputs/public_research_website/data';OUT=ROOT/'outputs/clean_research_delivery';sys.path.insert(0,str(P));from public_facet_rules import acceptable,specificity
load=lambda p:json.load(gzip.open(p,'rt',encoding='utf-8'))
index=load(D/'research_catalog.json.gz');meta=json.loads((P/'general_facet_dictionary.json').read_text());schema=json.loads((P/'industry_dictionary_schema.json').read_text());bycode={m['code']:m for m in schema['modules']};classifications=load(D/'industry_classifications.json.gz')
# Use existing extractor's literal main-field discovery patterns, then its relevance gates.
import ast
patterns={}
for n in ast.parse((ROOT/'outputs/global_comps_560/score_comp_draft.py').read_text()).body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PATTERNS' for t in n.targets):patterns=ast.literal_eval(n.value)
patterns.update({'Customer Type':r'\bB2B\b|\bB2C\b|\bB2G\b|business.to.business|business.to.consumer|(?:customers|clients) (?:include|are|consist of)|serves? (?:businesses|consumers|government)|sells?.{0,30}(?:businesses|consumers|government)', 'Customer Size':r'(?:small|medium|mid.market|large|enterprise).{0,35}(?:businesses|companies|employers|customers|clients)|(?:customers|clients).{0,35}(?:small|medium|mid.market|enterprise)'});compiled={f:re.compile(patterns.get(f,re.escape(f)),re.I) for f in [m['name'] for m in meta]}

def qualified(t,name):
 if name in ['Customer Type','Customer Size']:return 40<=len(t)<=1800 and bool(compiled[name].search(t)) and not re.search(r'cookie|privacy|risk factors|may adversely|could adversely',t,re.I)
 return acceptable(t,name)

def units(text):return [t.strip() for t in re.split(r'\n+|(?<=[.!?])\s+(?=[A-Z])',text[:100000]) if 40<=len(t.strip())<=1800]
def add_source(p,s,text):
 sid=hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest()[:20];eid=hashlib.sha256((sid+'\n'+text).encode()).hexdigest()[:20];p['sources'].setdefault(sid,s);p['evidence'].setdefault(eid,{'text':text,'source_id':sid});return eid

def cv(p,ids):
 qs=[p['evidence'][e] for e in ids];ss=[p['sources'][q['source_id']] for q in qs];types=sorted({s.get('source_type','UNKNOWN') for s in ss});norm={re.sub(r'\s+',' ',q['text']).lower().strip() for q in qs};origins={('S&P_GLOBAL' if re.search(r'WRDS|CAPITAL.?IQ|COMPUSTAT',s.get('source_type',''),re.I) else 'ISSUER' if s.get('source_type') in ['SEC','OFFICIAL_WEBSITE'] else s.get('source_type','UNKNOWN')) for s in ss}
 return {'status':'UNKNOWN_NO_EVIDENCE' if not ids else 'SHARED_WORDING_NOT_INDEPENDENT_CONFIRMATION' if len(ids)>1 and len(norm)==1 else 'MULTISOURCE_MEANING_REVIEW_REQUIRED' if len(ids)>1 else 'SINGLE_SOURCE_NOT_INDEPENDENTLY_CONFIRMED','source_types':types,'upstream_origin_count_upper_bound':len(origins),'fact_verified':False,'scope_period_independence_review_required':True}

# Fields with explicit retrieval rules; other standard fields remain unknown rather than guessed.
IRULES={'58':{'I58-01':r'quick.service|fast.casual|full.service restaurant|drinking place','I58-02':r'franchis.{0,120}(?:operated|operates|restaurants|locations)|company.operated.{0,120}franchis','I58-06':r'\b[\d,]+\s+(?:restaurants|locations|units)\b','I58-07':r'menu.{0,100}(?:hamburger|chicken|pizza|sandwich|beverage)|(?:hamburger|chicken|pizza).{0,100}menu'},'73':{'I73-01':r'provides?.{0,80}(?:software|consulting|staffing|advertising|cleaning)|software.{0,50}(?:payroll|accounting|human capital)','I73-03':r'per.employee|per.user|per.seat|per.transaction|per.billable.hour','I73-08':r'cloud.based|on.premise|software.as.a.service|\bSaaS\b','I73-09':r'payroll|human capital management|enterprise resource planning|customer relationship management'},'65':{'I65-01':r'(?:owns?|leases?|operates?).{0,100}(?:properties|real estate|commercial buildings)|property.{0,70}leasing','I65-02':r'(?:company|we).{0,60}(?:owns?|leases?|operates?).{0,90}(?:properties|sites|real estate)','I65-07':r'rental (?:income|revenues?)|property management fees'},'63':{'I63-01':r'property and casualty|life insurance|health insurance|reinsurance'},'62':{'I62-01':r'brokerage|investment advisory|asset management|market making'},'36':{},'28':{}}
latest={}
for path in (P/'downloads/latest_disclosures_20261111').glob('*.json'):
 if path.name=='summary.json':continue
 r=json.loads(path.read_text());k=index['aliases'].get(r.get('company_id'))
 if k:latest[k]=path
stats=collections.Counter();changes=[];coverage=[];start=time.time();groups=sorted(set(index['groups'].values()))
for gi,group in enumerate(groups):
 path=D/(group+'.json.gz');profiles=load(path)
 for key,p in profiles.items():
  if p.get('updated_at')=='2026-11-11' and len(p.get('main_facets',[]))==32:
   standard=p.get('industry_standard_facets',[]);stats['companies']+=1;stats['resumed_existing_profiles']+=1;stats['main_with_evidence']+=p['main_filled'];stats['main_unknown']+=32-p['main_filled'];stats['industry_standard_fields']+=len(standard);stats['industry_standard_with_evidence']+=sum(bool(f['evidence_ids']) for f in standard)
   coverage.append({'company_id':key,'company_name':p['name'],'is_original_target':p['is_original_target'],'main_filled':p['main_filled'],'main_total':32,'main_coverage_percent':round(p['main_filled']/32*100,2),'unknown_general_facets':'; '.join(f['name'] for f in p['main_facets'] if not f['evidence_ids']),'standard_industry_total':len(standard),'standard_industry_filled':sum(bool(f['evidence_ids']) for f in standard),'all_facts_verified':False})
   continue
  byname={f['name']:f for f in p['main_facets']};raw=[];seen=set()
  for q in ([p.get('business_description')]+list(p['evidence'].values()) if key in latest else [p.get('business_description')]):
   if not q or not q.get('text'):continue
   s=p['sources'].get(q.get('source_id'))
   if not s:continue
   tok=(q['text'],s.get('url'))
   if tok in seen:continue
   seen.add(tok);raw.extend((t,s) for t in units(q['text']))
  if key in latest:
   r=json.loads(latest[key].read_text())
   # Existing canonical CIK linkage is reused, not newly inferred by company name.
   for doc in r.get('documents',[]):
    if not doc.get('text'):continue
    source={'source_type':'SEC','url':doc['source_url'],'document_type':doc['form'],'document_date':doc['filing_date'],'report_period':doc['report_date'],'retrieved_at':r['checked_at'],'record_locator':'SEC accession '+doc['accession'],'identity_basis':'EXISTING_CANONICAL_CIK_LINKAGE; NOT_NEW_INDEPENDENT_IDENTITY_VERIFICATION','text_type':'EXACT_SOURCE_SUBSTRING'}
    raw.extend((t,source) for t in units(doc['text']))
  raw=list({(t,s.get('url'),s.get('report_period')):(t,s) for t,s in raw}.values());raw.sort(key=lambda x:(x[1].get('document_date','')!='UNKNOWN',x[1].get('document_date',''),x[1].get('source_type')=='SEC'),reverse=True)
  for m in meta:
   f=byname.setdefault(m['name'],{'name':m['name'],'status':'UNKNOWN','evidence_ids':[],'other_evidence_ids':[]});old=list(f.get('evidence_ids',[]));found=[];urls=set()
   # Retain previous observations. Fresh explicit passages can supplement, never silently erase them.
   for t,s in (raw if key in latest or not old else []):
    if not compiled[m['name']].search(t) or not qualified(t,m['name']):continue
    if s.get('url') in urls:continue
    found.append(add_source(p,s,t));urls.add(s.get('url'))
    if len(found)==3:break
   if found:
    f['evidence_ids']=found;f['other_evidence_ids']=list(dict.fromkeys(old+f.get('other_evidence_ids',[])));f['other_evidence_ids']=[e for e in f['other_evidence_ids'] if e not in found];f['status']='AUTOMATED_SOURCE_EXCERPTS_REQUIRE_REVIEW';f['cross_validation']=cv(p,found)
    if found!=old:
     changes.append({'company_id':key,'company_name':p['name'],'is_target':p['is_original_target'],'facet':m['name'],'source_observations':[{'text':p['evidence'][e]['text'],'source':p['sources'][p['evidence'][e]['source_id']]} for e in found],'cross_validation':f['cross_validation']});stats['main_fields_updated']+=1
     if not old:stats['main_fields_newly_supported']+=1
   else:f['cross_validation']=cv(p,old)
   f['facet_id']=m['id'];f['priority']=m['priority'];stats['main_with_evidence' if f['evidence_ids'] else 'main_unknown']+=1
  p['main_facets']=[byname[m['name']] for m in meta];p['main_filled']=sum(bool(f['evidence_ids']) for f in p['main_facets']);p['updated_at']='2026-11-11';p['verified_all_facts']=False
  c=classifications.get(key,{});primary=c.get('primary_sic') or {};code=str(primary.get('code',''))[:2];standard=[]
  if code in bycode and re.search(r'SEC SIC|Compustat SIC|US[_ .-]?SIC',primary.get('system',''),re.I):
   for f in bycode[code]['fields']:
    ids=[];pat=IRULES.get(code,{}).get(f['id'])
    if pat:
     for t,s in raw:
      if re.search(pat,t,re.I) and not re.search(r'cookie|privacy|our competitors|may adversely|could adversely',t,re.I):
       ids.append(add_source(p,s,t))
       if len(ids)==3:break
    standard.append({'name':f['name'],'standard_id':f['id'],'scope_key':'issuer','evidence_ids':list(dict.fromkeys(ids)),'status':'AUTOMATED_SOURCE_EXCERPTS_REQUIRE_REVIEW' if ids else 'UNKNOWN','cross_validation':cv(p,list(dict.fromkeys(ids)))})
   p['industry_standard_facets']=standard;stats['industry_standard_fields']+=len(standard);stats['industry_standard_with_evidence']+=sum(bool(f['evidence_ids']) for f in standard)
  stats['companies']+=1
  coverage.append({'company_id':key,'company_name':p['name'],'is_original_target':p['is_original_target'],'main_filled':p['main_filled'],'main_total':32,'main_coverage_percent':round(p['main_filled']/32*100,2),'unknown_general_facets':'; '.join(f['name'] for f in p['main_facets'] if not f['evidence_ids']),'standard_industry_total':len(standard),'standard_industry_filled':sum(bool(f['evidence_ids']) for f in standard),'all_facts_verified':False})
 with gzip.open(path,'wt',encoding='utf-8',compresslevel=6) as f:json.dump(profiles,f,ensure_ascii=False,separators=(',',':'))
 if gi%10==0:print('Profiles',stats['companies'],'new main fields',stats['main_fields_newly_supported'],'seconds',round(time.time()-start),flush=True)
with gzip.open(P/'extraction_updates_20261111.json.gz','wt',encoding='utf-8') as f:json.dump(changes,f,ensure_ascii=False)
with (OUT/'Extraction_Completeness.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(coverage[0]));w.writeheader();w.writerows(coverage)
summary={**stats,'as_of':'2026-11-11','all_facts_verified':False,'all_sources_downloaded':False,'lseg_current_connection':'CONNECTION_REFUSED','sec_scan_limit_per_document_characters':100000,'industry_retrieval_rules':'limited explicit rules; unimplemented fields remain unknown','similarity_recomputed':False,'meaning_cross_validation':'source-provenance screening; distinct source claims remain pending semantic review'};(P/'extraction_summary_20261111.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
