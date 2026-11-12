from pathlib import Path
import gzip,hashlib,json
P=Path(__file__).resolve().parent;D=P.parents[1]/'outputs/public_research_website/data';load=lambda p:json.load(gzip.open(p,'rt'));stats={'overlay_profiles':0,'industry_new_evidence_records':0,'source_refs_checked':0};idx=load(D/'research_catalog.json.gz')
for path in (D/'quality_refresh_20261112').glob('*.gz'):
 for key,q in load(path).items():
  stats['overlay_profiles']+=1
  for f in list(q.get('main_patch',{}).values())+q.get('industry_standard_facets',[]):
   for eid in f.get('evidence_ids',[]):
    e=q['evidence'][eid];s=q['sources'][e['source_id']];assert e['text'] and s['url'].startswith('https://');stats['source_refs_checked']+=1
  for f in q.get('industry_standard_facets',[]):
   if 'RETRIEVED_STANDARD_FIELD_EVIDENCE' in f.get('status',''):assert f.get('used_in_matching') is False;stats['industry_new_evidence_records']+=1
r=json.loads((P/'mcd_rescore_result_20261112.json').read_text());assert r['target_evidence_hash_unchanged'];stats['mcd_pairs_recomputed']=r['mcd_pairs_recomputed']
for path in (D/'matches').glob('*.gz'):
 for tid,rs in load(path).items():
  if tid=='IQ23557':
   assert not any(r['Candidate RIC']=='2702.T' for r in rs);m=next(r for r in rs if r['Candidate RIC']=='MCD');assert m['Similarity Percent']==59.34
   for f in m['Facet Details']:
    if f['facet']=='Primary Products':assert 'internal-use' not in f['candidate']['text'] and 'hamburgers' in f['candidate']['text']
key=idx['aliases']['MCD'];p=load(D/(idx['groups'][key]+'.json.gz'))[key];primary=next(f for f in p['main_facets'] if f['name']=='Primary Products');assert all('hamburgers' in p['evidence'][eid]['text'] for eid in primary['evidence_ids'])
stats.update({'mcd_research_and_comparison_passed':True,'all_semantics_verified':False});(P/'quality_continuation_validation_20261112.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats))
