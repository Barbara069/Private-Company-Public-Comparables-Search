"""Update the existing two comprehensive CSVs atomically; keep new SEC full text."""
from pathlib import Path
import collections,csv,gzip,json,functools
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'outputs/public_research_website/data';OUT=ROOT/'outputs/clean_research_delivery';csv.field_size_limit(2**31-1)
load=lambda p:json.load(gzip.open(p,'rt',encoding='utf-8'));index=load(D/'research_catalog.json.gz');by={x['key']:x for x in index['companies']};fields=['dataset','company_id','company_name','entity_role','facet','source_url','source_date','text','record_json'];allstats={}
@functools.lru_cache(maxsize=3)
def group(name):return load(D/(name+'.json.gz'))
for role,name in [('TARGET','Targets_560.csv.gz'),('PUBLIC','Public_Companies.csv.gz')]:
 src=OUT/name;tmp=src.with_suffix('.20261111.pending');stats=collections.Counter()
 with gzip.open(src,'rt',encoding='utf-8-sig',newline='') as f,gzip.open(tmp,'wt',encoding='utf-8',newline='',compresslevel=6) as g:
  writer=csv.DictWriter(g,fieldnames=fields);writer.writeheader()
  for r in csv.DictReader(f):
   if r['dataset'] in ['SEC_Availability_20261111','Downloaded_SEC_Disclosure_20261111','Extraction_Completeness_20261111']:continue
   if r['dataset']=='Unified_Public_Research' and r['company_id'] in index['groups']:
    p=group(index['groups'][r['company_id']])[r['company_id']];r['record_json']=json.dumps(p,ensure_ascii=False);r['source_date']='2026-11-11';stats['updated_research_profiles']+=1
   writer.writerow(r)
  def emit(ds,key,label,text,obj,url='',facet=''):
   writer.writerow(dict(dataset=ds,company_id=key,company_name=label,entity_role=role,facet=facet,source_url=url,source_date='2026-11-11',text=text,record_json=json.dumps(obj,ensure_ascii=False)));stats[ds]+=1
  for path in (P/'downloads/latest_disclosures_20261111').glob('*.json'):
   if path.name=='summary.json':continue
   r=json.loads(path.read_text());key=index['aliases'].get(r.get('company_id'));c=by.get(key);partition='TARGET' if c and c.get('is_original_target') else 'PUBLIC'
   if partition!=role:continue
   metadata={k:v for k,v in r.items() if k not in ['documents','submissions']};metadata['documents']=[{k:v for k,v in d.items() if k!='text'} for d in r.get('documents',[])];metadata['used_in_pseudo_private_matching']=False
   emit('SEC_Availability_20261111',key or r['company_id'],r.get('company_name',''),'SEC availability refresh',metadata,r.get('submissions_url',''))
   for d in r.get('documents',[]):
    if d.get('acquisition')=='DOWNLOADED' and d.get('text'):emit('Downloaded_SEC_Disclosure_20261111',key or r['company_id'],r.get('company_name',''),d['text'],{**d,'cik':r['cik'],'research_only':True,'used_in_pseudo_private_matching':False},d['source_url'])
  with (OUT/'Extraction_Completeness.csv').open(encoding='utf-8-sig',newline='') as h:
   for row in csv.DictReader(h):
    if (row['is_original_target']=='True')==(role=='TARGET'):emit('Extraction_Completeness_20261111',row['company_id'],row['company_name'],'Source-backed extraction coverage; not fact verification',row)
 tmp.replace(src);allstats[role]=dict(stats);print(name,dict(stats),flush=True)
(P/'packaging_summary_20261111.json').write_text(json.dumps(allstats,indent=2))
