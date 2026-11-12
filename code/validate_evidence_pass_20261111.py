from pathlib import Path
import collections,gzip,hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'outputs/public_research_website/data';load=lambda p:json.load(gzip.open(p,'rt',encoding='utf-8'));idx=load(D/'research_catalog.json.gz');schema=json.loads((P/'industry_dictionary_schema.json').read_text());ids={f['id'] for m in schema['modules'] for f in m['fields']};meta=json.loads((P/'general_facet_dictionary.json').read_text());names={m['name'] for m in meta};stats=collections.Counter()
for group in sorted(set(idx['groups'].values())):
 for key,p in load(D/(group+'.json.gz')).items():
  assert len(p['main_facets'])==32 and {f['name'] for f in p['main_facets']}==names
  assert p['main_filled']==sum(bool(f['evidence_ids']) for f in p['main_facets'])
  assert p['research_mode']=='UNRESTRICTED_PUBLIC_COMPANY_RESEARCH'
  assert all(f['standard_id'] in ids and f['scope_key']=='issuer' for f in p.get('industry_standard_facets',[]))
  for f in p['main_facets']+p.get('industry_standard_facets',[]):
   for eid in f.get('evidence_ids',[])+f.get('other_evidence_ids',[]):
    assert eid in p['evidence'];q=p['evidence'][eid];assert q['text'] and q['source_id'] in p['sources']
  stats['companies']+=1;stats['original_target_profiles']+=p['is_original_target'];stats['main_with_evidence']+=p['main_filled'];stats['main_total']+=32;stats['main_fully_populated_profiles']+=p['main_filled']==32
before=json.loads((P/'unified_research/comparison_input_boundary_hash.json').read_text());assert hashlib.sha256((P/'blinded_target_inputs.json').read_bytes()).hexdigest()==before['sha256']
seen=0
for f in (P/'downloads/latest_disclosures_20261111').glob('*.json'):
 if f.name=='summary.json':continue
 for doc in json.loads(f.read_text()).get('documents',[]):
  if doc.get('text'):assert hashlib.sha256(doc['text'].encode()).hexdigest()==doc['text_sha256'];seen+=1
stats['sec_text_hashes_verified']=seen
policy=json.loads((P/'scoring_policy_v3.json').read_text());assert sum(x['weight_percent'] for x in policy['general_weights'])==100
result={**stats,'restricted_target_inputs_unchanged':True,'source_references_structurally_valid':True,'semantic_review_complete':False,'all_facts_verified':False,'new_similarity_scores_computed':False};(P/'validation_20261111.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
