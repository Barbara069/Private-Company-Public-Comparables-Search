"""Review-selected exact source passages; full research only, blinded target snapshot untouched."""
import gzip,json,hashlib,re
from pathlib import Path
P=Path(__file__).resolve().parent;D=P.parents[1]/'outputs/public_research_website/data'
load=lambda p:json.load(gzip.open(p,'rt'))
idx=load(D/'research_catalog.json.gz');key=idx['aliases']['MCD'];path=D/(idx['groups'][key]+'.json.gz');ps=load(path);p=ps[key]
raw=json.loads((P/'downloads/latest_disclosures_20261111/MCD.json').read_text());docs=raw['documents'];annual=next(d for d in docs if d['form']=='10-K')
anchors={
'Primary Products':'McDonald’s menu features hamburgers',
'Primary Services':'The Company franchises and owns and operates McDonald',
'Core Business Activity':'The Company franchises and owns and operates McDonald',
'Business Model':'The Company is primarily a franchisor',
'Revenue Model':'The Company’s revenues consist of sales by Company-owned',
'Value Chain Position':'The Company is primarily a franchisor',
'Geography Served':'The Company franchises and owns and operates McDonald',
'Product Specialization':'McDonald’s menu features hamburgers',
'Distribution Channels':'◦ Drive Thru:',
'Delivery Model':"• D ouble Down on the 4D's:",
'Pricing Structure':'Conventional franchisees contribute to the Company’s revenue',
'Recurring Revenue Profile':'Conventional franchisees contribute to the Company’s revenue',
'Contract Duration':'The Company’s revenues consist of sales by Company-owned',
'Capital Intensity':'• Capital expenditures of $3.4 billion',
'Labor Intensity':'Company-owned and operated restaurant margins are measured',
'Supply Chain Complexity':'The Company and its franchisees purchase food, packaging',
'IP Dependence':'The Company owns or is licensed to use valuable intellectual property',
'Brand Dependence':'The Company owns or is licensed to use valuable intellectual property',
'Competitive Positioning':'McDonald’s restaurants compete with international',
'Company Size Category':'The Company franchises and owns and operates McDonald',
}
old={f['name']:dict(f) for f in p['main_facets']};quarantined={}
def add(text,doc):
 s={'source_type':'SEC','url':doc['source_url'],'document_type':doc['form'],'document_date':doc['filing_date'],'report_period':doc.get('report_date'),'retrieved_at':raw['checked_at'],'record_locator':'SEC accession '+doc['accession'],'text_type':'EXACT_SOURCE_SUBSTRING','review':'FACET_RELEVANCE_REVIEWED_2026-11-12'}
 sid=hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest()[:20];eid=hashlib.sha256((sid+'\n'+text).encode()).hexdigest()[:20];p['sources'][sid]=s;p['evidence'][eid]={'source_id':sid,'text':text};assert text in doc['text'];return eid
for f in p['main_facets']:
 name=f['name'];quarantined[name]=f.get('evidence_ids',[])+f.get('other_evidence_ids',[]);ids=[]
 if name in anchors:
  # Newest applicable filing first; retain annual descriptions when the interim does not restate them.
  for doc in sorted(docs,key=lambda d:d['filing_date'],reverse=True):
   paras=[s.strip() for s in doc['text'].split('\n') if anchors[name] in s and 35<len(s.strip())<=2400]
   if paras:ids.append(add(paras[0],doc))
   if len(ids)>=2:break
 if name in ['Primary Products','Product Specialization']:
  b=p['business_description'];text=next(s for s in re.split(r'(?<=\.)\s+',b['text']) if s.startswith('Its menu features'))
  eid=hashlib.sha256((b['source_id']+'\n'+text).encode()).hexdigest()[:20];p['evidence'][eid]={'source_id':b['source_id'],'text':text};ids.append(eid)
 f['evidence_ids']=ids[:3];f['other_evidence_ids']=[];f['status']='FACET_RELEVANCE_REVIEWED_SOURCE_EXCERPTS' if ids else 'UNKNOWN_PENDING_RELEVANT_EVIDENCE';f['missing_reason']=None if ids else 'Prior assignments withdrawn during company review; no sufficiently specific passage admitted yet.'
 types=sorted({p['sources'][p['evidence'][e]['source_id']]['source_type'] for e in ids});f['cross_validation']={'status':'SEC_LSEG_AGREE_ON_BURGER_MENU_SOURCE_DATES_DIFFER' if name in ['Primary Products','Product Specialization'] else 'RELEVANCE_REVIEWED_NOT_INDEPENDENTLY_CONFIRMED' if ids else 'NO_EVIDENCE','source_types':types,'fact_verified':False,'scope_and_period_review_required':True}
 p['main_filled']=sum(bool(f['evidence_ids']) for f in p['main_facets'])
p['facet_assignment_review_20261112']={'removed_from_display':quarantined,'basis':'Reject accounting standards, internal software, benefits and unrelated passages as commercial products/services. Research profile review only; no restricted target data altered.'}
with gzip.open(path,'wt') as f:json.dump(ps,f,ensure_ascii=False,separators=(',',':'))
shard=hashlib.sha256(key.encode()).hexdigest()[:1];op=D/f'general_refresh_20261112/group_{shard}.json.gz';o=load(op)
o[key]={'main_patch':{f['name']:f for f in p['main_facets']},'evidence':p['evidence'],'sources':p['sources']}
with gzip.open(op,'wt') as f:json.dump(o,f,ensure_ascii=False,separators=(',',':'))
(P/'mcd_general_facet_review_20261112.json').write_text(json.dumps({'company_id':key,'filled':p['main_filled'],'total':32,'profile_path':str(path),'overlay_path':str(op),'selected':{f['name']:[p['evidence'][e]['text'] for e in f['evidence_ids']] for f in p['main_facets']}},ensure_ascii=False,indent=2))
print(json.dumps({'filled':p['main_filled'],'overlay':str(op),'profile':str(path)}))
