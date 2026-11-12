"""Full-universe product relevance audit and source-linked industry gap filling. Research only."""
from pathlib import Path
import collections,gzip,hashlib,json,re,sys,time
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'outputs/public_research_website/data';sys.path.insert(0,str(P));from public_facet_rules import acceptable,specificity
load=lambda p:json.load(gzip.open(p,'rt'));idx=load(D/'research_catalog.json.gz');classes=load(D/'industry_classifications.json.gz');schema={m['code']:m for m in json.loads((P/'industry_dictionary_schema.json').read_text())['modules']};latest={};stats=collections.Counter();updates=collections.defaultdict(dict);start=time.time()
for path in (P/'downloads/latest_disclosures_20261111').glob('*.json'):
 if path.name=='summary.json':continue
 q=json.loads(path.read_text());key=idx['aliases'].get(q.get('company_id'))
 if key:latest[key]=path
rules={
'58':{'01':r'(?:our|company.s|operates?|chain of|primarily|competition of).{0,90}(?:quick.service|fast.casual|full.service restaurant|casual.dining)|competes among quick.service', '02':r'(?:restaurants|locations|units).{0,100}(?:franchised|company.operated)|(?:franchised|company.operated).{0,100}(?:restaurants|locations|units)', '03':r'comparable (?:restaurant |store |unit )?sales.{0,100}(?:increas|decreas|growth|declin|%|percent)|same.store sales.{0,100}(?:%|percent|growth)', '04':r'(?:guest counts|traffic|average check).{0,100}(?:increas|decreas|%|percent)|comparable sales are driven by changes in guest counts', '05':r'average unit volume.{0,100}(?:\$|million|thousand)|average (?:annual |restaurant )?sales per (?:restaurant|unit).{0,100}\$', '06':r'(?:of the |operated |approximately |total of )[\d,]+.{0,40}(?:restaurants|locations)|(?:restaurants|locations) at (?:year.end|September|December|June|March)', '07':r'menu (?:features|includes|consists|offers|specializ).{0,120}(?:hamburger|burger|chicken|pizza|sandwich|beverage|coffee)', '08':r'(?:digital|delivery|drive.thr|online).{0,100}(?:sales|orders).{0,60}(?:%|percent)|(?:%|percent).{0,100}(?:sales|orders).{0,60}(?:digital|delivery|drive.thr)', '09':r'(?:restaurant.level|restaurant.margin|company.owned and operated restaurant margins).{0,100}(?:profit|costs|margin|%|percent|sales)'},
'73':{'01':r'(?:company|we|business|provides?|offers?).{0,100}(?:payroll software|human capital management|consulting services|staffing services|advertising services|business.process outsourcing)', '02':r'(?:company|we|our services).{0,100}(?:managed services|outsourcing|staffing|consulting|software.as.a.service)', '03':r'(?:per.employee|per.user|per.seat|per.transaction|per.billable.hour).{0,100}(?:fee|price|charge|month|year)|(?:fee|price|charge).{0,100}(?:per.employee|per.user|per.seat|per.transaction)', '04':r'(?:customer|client|service).{0,60}(?:contracts?|agreements?).{0,100}(?:\d+.year|years|months|multi.year|annual|renew)', '05':r'(?:our|company|revenue).{0,100}(?:recurring revenue|subscription revenue|renewable contracts)|(?:recurring|subscription) revenues?.{0,100}(?:%|percent|million|billion)', '06':r'(?:implementation|transition|onboarding|migration).{0,100}(?:customers|clients|services|projects)', '07':r'(?:client|customer).{0,25}retention.{0,80}(?:%|percent)|(?:%|percent).{0,80}(?:client|customer).{0,25}retention', '08':r'(?:our|company|we|platform|software|solutions).{0,100}(?:cloud.based|on.premise|SaaS|software.as.a.service)', '09':r'(?:software|platform|suite|solutions).{0,120}(?:payroll|human capital|human resources|accounting|ERP|CRM|cybersecurity)', '10':r'net (?:revenue|dollar) retention.{0,100}(?:%|percent|defined|calculate)', '11':r'(?:annual recurring revenue|\bARR\b).{0,100}(?:defined|define|calculate|million|billion|\$)', '12':r'(?:we|company|platform).{0,100}(?:transaction processing|data processing|payment processing)', '13':r'(?:we|company|services).{0,100}(?:temporary staffing|permanent placement|recruitment services)', '14':r'temporary (?:staffing|employees|workers).{0,100}(?:hours|assignments|clients|revenue)', '15':r'permanent placement.{0,100}(?:placements|revenue|fees|volume)', '16':r'(?:bill rates?|pay rates?|bill.pay spread).{0,100}(?:temporary|staffing|hours|margin)', '17':r'(?:advertising|agency).{0,100}(?:retainer|media buying|commissions|project fees)', '18':r'(?:provides?|offers?|services include).{0,100}(?:janitorial|building maintenance|security guard|protective services)', '19':r'(?:rental fleet|equipment rental).{0,100}(?:utilization|fleet|equipment)'},
'65':{'01':r'(?:properties|portfolio).{0,100}(?:office|industrial|retail|multifamily|apartments|self.storage|hotel)|(?:we|company).{0,80}(?:property management|real estate brokerage)', '02':r'(?:we|company).{0,80}(?:owns?|leases?|operates?|manages?).{0,80}(?:properties|real estate|buildings|apartments)', '03':r'occupancy.{0,80}(?:%|percent|leased|defined)|(?:%|percent).{0,60}(?:occupied|leased)', '04':r'(?:weighted.average remaining lease term|\bWALE\b|lease terms?).{0,100}(?:years|months)', '05':r'(?:rent per|rental rate per).{0,60}(?:square foot|square meter|unit|sqm|sq.ft)', '06':r'(?:properties|portfolio).{0,100}(?:located in|across|markets including)', '07':r'(?:revenues?|income).{0,100}(?:rental|property management fees|leasing commissions)'},
'63':{'01':r'(?:we|company|products|insurance).{0,100}(?:property and casualty|life insurance|health insurance|annuities|reinsurance)', '02':r'(?:we|company).{0,100}(?:underwrites?|reinsures?|insurance broker|insurance distribution)', '03':r'(?:premiums written|earned premiums|net premiums).{0,120}(?:%|percent|million|billion|business line)', '04':r'combined ratio.{0,100}(?:%|percent|defined|calculate)', '05':r'(?:loss and loss adjustment expense ratio|loss ratio|LAE ratio).{0,100}(?:%|percent|defined)', '06':r'(?:medical benefit ratio|medical loss ratio).{0,100}(?:%|percent|defined)', '07':r'(?:our|company|we).{0,100}(?:reinsurance agreements|catastrophe reinsurance|reinsurance protection)', '08':r'(?:annuities|life insurance|policy liabilities).{0,100}(?:duration|guarantees|surrender)', '09':r'(?:asset.liability matching|asset.liability management|duration matching).{0,120}', '10':r'(?:risk.based capital|solvency coverage ratio|Solvency II).{0,100}(?:%|percent|ratio|capital)'}
}
compiled={code:{f'I{code}-{k}':re.compile(v,re.I) for k,v in rs.items()} for code,rs in rules.items()}
# Extract contiguous paragraphs; split long paragraphs into exact sentence spans.
def passages(text):
 for para in text.split('\n'):
  if 40<=len(para.strip())<=2200:yield para.strip()
  elif len(para)>2200:
   for m in re.finditer(r'.+?(?:[.!?](?=\s+[A-Z])|$)',para,re.S):
    t=m.group().strip()
    if 40<=len(t)<=2200:yield t
ban=re.compile(r'accounting (?:standard|guidance)|internal.use software|FASB|ASU No\.|fair value hierarchy|deferred tax|table of contents',re.I)
def add(p,t,s):
 sid=hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest()[:20];eid=hashlib.sha256((sid+'\n'+t).encode()).hexdigest()[:20];p['sources'][sid]=s;p['evidence'][eid]={'text':t,'source_id':sid};return eid
for gi,group in enumerate(sorted(set(idx['groups'].values()))):
 path=D/(group+'.json.gz');ps=load(path);changed=False
 for key,p in ps.items():
  stats['profiles_audited']+=1;delta={};new_ev={};new_src={};raw=[]
  b=p.get('business_description') or {}
  if b.get('source_id') in p['sources']:raw.append((b['text'],p['sources'][b['source_id']]))
  # Cache full document paragraphs once per company, not per facet.
  if key in latest:
   q=json.loads(latest[key].read_text())
   for doc in q.get('documents',[]):
    if not doc.get('text'):continue
    stats['retained_documents_searched']+=1;s={'source_type':'SEC','url':doc['source_url'],'document_type':doc['form'],'document_date':doc['filing_date'],'report_period':doc.get('report_date'),'record_locator':doc['accession'],'retrieved_at':q['checked_at'],'text_type':'EXACT_SOURCE_SUBSTRING'};raw.extend((t,s) for t in passages(doc['text']))
  products=next(f for f in p['main_facets'] if f['name']=='Primary Products');old=products.get('evidence_ids',[]);bad=[e for e in old if not acceptable(p['evidence'][e]['text'],'Primary Products')]
  if bad:
   stats['profiles_with_rejected_product_evidence']+=1;stats['rejected_product_passages']+=len(bad);choices=[(p['evidence'][e]['text'],p['sources'][p['evidence'][e]['source_id']]) for e in old if e not in bad];choices.extend((t,s) for t,s in raw if acceptable(t,'Primary Products'))
   choices.sort(key=lambda ts:(specificity(ts[0],'Primary Products'),ts[1].get('document_date','')),reverse=True);ids=[];urls=set()
   for t,s in choices:
    if s.get('url') in urls:continue
    eid=add(p,t,s);ids.append(eid);urls.add(s.get('url'))
    if len(ids)==3:break
   products['evidence_ids']=ids;products['other_evidence_ids']=[e for e in products.get('other_evidence_ids',[]) if acceptable(p['evidence'][e]['text'],'Primary Products') and e not in ids];products['status']='RELEVANCE_GATE_REVIEWED; SEMANTIC_REVIEW_PENDING';products['cross_validation']={'status':'MEANING_REVIEW_REQUIRED' if ids else 'NO_EVIDENCE','fact_verified':False};delta['main_patch']={'Primary Products':products};stats['product_fields_repaired']+=bool(ids);stats['product_fields_withdrawn_no_replacement']+=not bool(ids)
  primary=(classes.get(key) or {}).get('primary_sic') or {};code=str(primary.get('code',''))[:2];std=p.get('industry_standard_facets',[]);byid={f.get('standard_id'):f for f in std if f.get('scope_key')=='issuer'};count=0
  if code in compiled and re.search(r'SEC SIC|Compustat SIC|US[_ .-]?SIC',primary.get('system',''),re.I):
   for f in schema[code]['fields']:
    oldf=byid.get(f['id']);rx=compiled[code].get(f['id'])
    if not rx or (oldf or {}).get('evidence_ids'):continue
    choices=[(t,s) for t,s in raw if rx.search(t) and not ban.search(t) and not re.search(r'our competitors|may adversely|could adversely|hypothetical',t,re.I)];choices.sort(key=lambda ts:(ts[1].get('document_date',''),len(rx.findall(ts[0]))),reverse=True);ids=[];urls=set()
    for t,s in choices:
     if s.get('url') in urls:continue
     eid=add(p,t,s);ids.append(eid);urls.add(s.get('url'))
     if len(ids)==3:break
    if not ids:continue
    nf={'name':f['name'],'standard_id':f['id'],'scope_key':'issuer','evidence_ids':ids,'other_evidence_ids':[],'status':'RETRIEVED_STANDARD_FIELD_EVIDENCE; APPLICABILITY_AND_MEANING_REVIEW_PENDING','cross_validation':{'status':'MEANING_SCOPE_AND_PERIOD_REVIEW_REQUIRED','fact_verified':False},'used_in_matching':False}
    if oldf:std[std.index(oldf)]=nf
    else:std.append(nf)
    count+=1;stats['industry_newly_supported_'+code]+=1
   if count:delta['industry_standard_facets']=std;p['industry_standard_facets']=std;stats['profiles_with_industry_gap_fills']+=1;stats['industry_fields_newly_supported']+=count
  if not delta:continue
  p['main_filled']=sum(bool(f.get('evidence_ids')) for f in p['main_facets']);ids=[e for f in delta.get('main_patch',{}).values() for e in f.get('evidence_ids',[])+f.get('other_evidence_ids',[])];ids += [e for f in delta.get('industry_standard_facets',[]) for e in f.get('evidence_ids',[])]
  for eid in ids:
   ev=p['evidence'][eid];new_ev[eid]=ev;new_src[ev['source_id']]=p['sources'][ev['source_id']]
  delta.update({'evidence':new_ev,'sources':new_src,'main_filled':p['main_filled'],'updated_at':'2026-11-12','matching_changed':False});updates[hashlib.sha256(key.encode()).hexdigest()[0]][key]=delta;changed=True;stats['changed_profiles']+=1
 if changed:
  with gzip.open(path,'wt',compresslevel=6) as f:json.dump(ps,f,ensure_ascii=False,separators=(',',':'))
 if gi%20==0:print('Audited',stats['profiles_audited'],'industry fills',stats['industry_fields_newly_supported'],'seconds',round(time.time()-start),flush=True)
dest=D/'quality_refresh_20261112';dest.mkdir(exist_ok=True)
for shard,rows in updates.items():
 with gzip.open(dest/f'group_{shard}.json.gz','wt',compresslevel=6) as f:json.dump(rows,f,ensure_ascii=False,separators=(',',':'))
summary={**stats,'shards':list(updates),'bytes':sum(p.stat().st_size for p in dest.glob('*.gz')),'new_source_downloads':False,'all_facts_verified':False,'scoring_recomputed':False,'industry_rules_supported_sic2':list(rules)};(P/'quality_continuation_summary_20261112.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
