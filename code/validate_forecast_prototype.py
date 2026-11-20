"""Arithmetic, frozen-output and target-source boundary checks, not predictive validation."""
from pathlib import Path
import gzip,json,math
from urllib.parse import urlsplit
from source_policy import require_allowed
from forecast_private import run,validate,validate_target_input_boundary
ROOT=Path(__file__).resolve().parents[1]
def check():
 # Prevent target-side public financial leakage before any arithmetic runs.
 for forbidden in [{'cash':100},{'market_cap':100},{'revenue_history':[1,2]},
                   {'revenue_0':100,'financial_provenance':{'revenue_0':{'source_type':'SEC'}}}]:
  try:validate_target_input_boundary(forbidden)
  except ValueError:pass
  else:raise AssertionError('Unauthorized target input accepted')
 approved={'revenue_0':100,'EBITDA_0':20,'debt':30,'financial_provenance':{
  k:{'source_type':'INSTRUCTOR_WORKBOOK','source_locator':'supplied.xlsx!Sheet1!'+cell,
     'period':'2026 baseline (test fixture)','currency':'USD','unit':'million'}
  for k,cell in [('revenue_0','A2'),('EBITDA_0','B2'),('debt','C2')]}}
 assert validate_target_input_boundary(approved)
 p=ROOT/'website/data/private_forecast_prototype.json.gz';d=json.load(gzip.open(p,'rt'));require_allowed(d)
 fresh=run(d['config']);checks=validate(d['config'],fresh)
 assert fresh==d['results'],'Saved forecast differs from its frozen model inputs'
 source_ids=set()
 for s in d['source_observations']:
  assert s['source_id'] not in source_ids;source_ids.add(s['source_id'])
  if s['target_input_allowed']:
   assert s['issuer_id']=='GC_NETCHEX'
   host=(urlsplit(s['url']).hostname or '').removeprefix('www.')
   assert host=='netchex.com' or host.endswith('.netchex.com')
   assert s['source_type']=='OFFICIAL_WEBSITE'
 for event in d['signals']:
  assert all(s.startswith('NETCHEX_') for s in event['source_ids'])
 assert len(d['readiness'])==8 and sum(r['status']=='INDEXED_PROTOTYPE_ONLY' for r in d['readiness'])==1
 print('Forecast prototype checks:',checks);return checks
if __name__=='__main__':check()
