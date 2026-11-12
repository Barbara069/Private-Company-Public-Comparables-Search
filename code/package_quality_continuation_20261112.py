from pathlib import Path
import collections,csv,functools,gzip,json
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'outputs/public_research_website/data';O=R/'outputs/clean_research_delivery';csv.field_size_limit(2**31-1);load=lambda p:json.load(gzip.open(p,'rt'));idx=load(D/'research_catalog.json.gz');companies={c['key']:c for c in idx['companies']};updates={}
for path in (D/'quality_refresh_20261112').glob('*.gz'):updates.update(load(path))
@functools.lru_cache(maxsize=3)
def profiles(group):return load(D/(group+'.json.gz'))
counts={};cover=[]
for group in sorted(set(idx['groups'].values())):
 for key,p in profiles(group).items():
  std=p.get('industry_standard_facets',[]);cover.append({'company_id':key,'company_name':p['name'],'is_original_target':p['is_original_target'],'main_filled':sum(bool(f.get('evidence_ids')) for f in p['main_facets']),'main_total':32,'standard_industry_total':len(std),'standard_industry_filled':sum(bool(f.get('evidence_ids')) for f in std),'all_facts_verified':False})
with (O/'Extraction_Completeness.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(cover[0]));w.writeheader();w.writerows(cover)
for role,name in [('TARGET','Targets_560.csv.gz'),('PUBLIC','Public_Companies.csv.gz')]:
 p=O/name;tmp=p.with_suffix('.quality.pending');stats=collections.Counter()
 with gzip.open(p,'rt',encoding='utf-8-sig',newline='') as src,gzip.open(tmp,'wt',encoding='utf-8',newline='',compresslevel=6) as dst:
  reader=csv.DictReader(src);w=csv.DictWriter(dst,fieldnames=reader.fieldnames);w.writeheader()
  for row in reader:
   if row['dataset'] in ['Facet_Quality_Refresh_20261112','Reviewed_Comparable_MCD_20261112','Extraction_Completeness_20261112']:continue
   if row['dataset']=='Unified_Public_Research' and row['company_id'] in idx['groups']:
    row['record_json']=json.dumps(profiles(idx['groups'][row['company_id']])[row['company_id']],ensure_ascii=False);stats['current_profiles']+=1
   w.writerow(row);stats['rows']+=1
  for key,q in updates.items():
   c=companies[key]
   if bool(c['is_original_target'])!=(role=='TARGET'):continue
   for f in list(q.get('main_patch',{}).values())+q.get('industry_standard_facets',[]):
    for eid in f.get('evidence_ids',[]):
     e=q['evidence'][eid];s=q['sources'][e['source_id']];rec={'facet':f,'source':s,'evidence_id':eid,'exact_text':e['text'],'matching_changed':False};w.writerow({'dataset':'Facet_Quality_Refresh_20261112','company_id':key,'company_name':c['name'],'entity_role':role,'facet':f['name'],'source_url':s['url'],'source_date':s.get('document_date'),'text':e['text'],'record_json':json.dumps(rec,ensure_ascii=False)});stats['refreshed_source_observations']+=1
  for c in cover:
   if c['is_original_target']!=(role=='TARGET'):continue
   w.writerow({'dataset':'Extraction_Completeness_20261112','company_id':c['company_id'],'company_name':c['company_name'],'entity_role':role,'source_date':'2026-11-12','text':'Retrieved evidence coverage; not semantic verification','record_json':json.dumps(c)})
  if role=='TARGET':
   for path in (D/'matches').glob('*.gz'):
    for tid,rs in load(path).items():
     for r in rs:
      if r.get('Candidate Evidence Review')=='CORRECTED_2026-11-12':w.writerow({'dataset':'Reviewed_Comparable_MCD_20261112','company_id':tid,'company_name':r['Target Name'],'entity_role':role,'facet':'Public comparable — MCD','source_date':'2026-11-12','text':'Corrected candidate evidence; original target evidence and weights retained','record_json':json.dumps(r,ensure_ascii=False)});stats['mcd_recomputed_comparisons']+=1
 tmp.replace(p);counts[name]=dict(stats);print(name,dict(stats),flush=True)
(P/'quality_packaging_summary_20261112.json').write_text(json.dumps(counts,indent=2))
