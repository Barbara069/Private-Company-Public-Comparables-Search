"""Validate source boundaries, identity exclusions, fixed weights and score arithmetic."""
from pathlib import Path
import gzip,json,math,hashlib
from urllib.parse import urlsplit
from source_policy import require_allowed
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'website/data'
def load(p):return json.load(gzip.open(p,'rt'))
def validate():
 manifest=load(D/'comparison_rebuild_manifest.json.gz');inputs=load(D/'comparison_inputs.json.gz');idx=load(D/'research_catalog.json.gz')
 assert len(inputs)==560 and set(manifest['groups'])==set(inputs)
 assert manifest['version']=='permitted-evidence-v3.2-2026-11-15'
 counts={'targets':560,'scored_pairs':0,'targets_with_candidates':0,'abstentions':0,'target_evidence_checks':0,'industry_scored_pairs':0}
 groups={g:load(D/(g+'.json.gz')) for g in set(manifest['groups'].values())}
 for tid,input in inputs.items():
  rows=groups[manifest['groups'][tid]][tid];assert len(rows)<=10
  if rows:counts['targets_with_candidates']+=1
  else:counts['abstentions']+=1
  frozen=None;previous=math.inf
  for i,r in enumerate(rows,1):
   require_allowed(r);counts['scored_pairs']+=1
   assert r['Target ID']==tid and r['Candidate Order']==i
   digest=hashlib.sha256(json.dumps(input,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
   assert r['Target Input Hash']==digest, 'Stale target input: '+tid
   assert r['Canonical Company ID']!=idx['aliases'].get(tid)
   assert r['Financial Inputs Used For Retrieval'] is False and r['Final Ranking Eligible'] is False
   assert r['Ranking Score']<=previous+.001;previous=r['Ranking Score']
   weights=[(f['block'],f['facet'],f.get('standard_id'),f['weight']) for f in r['Facet Details']]
   if frozen is None:frozen=weights
   else:assert frozen==weights,'Candidate-dependent weights'
   coverage=support=0;industry_observed=False
   for f in r['Facet Details']:
    assert f['weight']>=0
    if f['score'] is not None:
     assert 0<=f['score']<=100 and f['target']['text'] and f['candidate']['text']
     coverage+=f['weight'];support+=f['contribution']
     if f['block']=='INDUSTRY' and f['weight']>0:industry_observed=True
    else:assert f['contribution'] is None
    for e in f['target']['evidence']:
     assert e['source_type']=='OFFICIAL_WEBSITE'
     host=(urlsplit(e['url']).hostname or '').lower().removeprefix('www.')
     base=(urlsplit(input['website'] if input['website'].startswith('http') else 'https://'+input['website']).hostname or '').lower().removeprefix('www.')
     assert host==base or host.endswith('.'+base)
     assert not host.startswith(('ir.','investor.','investors.'))
     assert not any(x in host for x in ['sec.gov','lseg.com','capitaliq.com'])
     counts['target_evidence_checks']+=1
   assert abs(r['Evidence Coverage Percent']-coverage)<.011
   assert abs(r['Evidence Supported Points']-support)<.011
   s=100*support/coverage
   assert abs(r['Similarity Percent']-s)<.011
   rank=s*(.5+.5*min(1,coverage/60))
   assert abs(r['Ranking Score']-rank)<.011
   if industry_observed:counts['industry_scored_pairs']+=1
 assert counts['scored_pairs']==manifest['stats']['scored_candidates']
 assert counts['targets_with_candidates']==manifest['stats']['targets_with_scores']
 print(json.dumps(counts,indent=2));return counts
if __name__=='__main__':validate()
