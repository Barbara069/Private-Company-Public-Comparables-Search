"""Model execution and target-input isolation, not a claim of predictive accuracy."""
import copy,gzip,json,math,unittest
from pathlib import Path
from build_target_growth_forecasts import build_target,website_signals
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'website/data'
def read(n):return json.load(gzip.open(D/(n+'.json.gz'),'rt'))
class ForecastChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=read('target_growth_forecasts');cls.inputs=read('comparison_inputs')
 def test_all_output_paths_and_sources(self):
  self.assertEqual(len(self.data['targets']),560)
  for tid,f in self.data['targets'].items():
   self.assertEqual(set(f['allowed_inputs']['available_financials']),{'revenue','ebitda','debt'})
   for s in f['website_signals']:self.assertEqual(s['source_type'],'OFFICIAL_WEBSITE')
   if f['scenarios']:
    self.assertGreaterEqual(len(f['peers']),2);self.assertAlmostEqual(sum(p['weight'] for p in f['peers']),1)
    self.assertNotIn(f['canonical_key'],[p['key'] for p in f['peers']])
    for name,path in f['scenarios'].items():
     self.assertEqual([r['year'] for r in path],list(range(2026,2032)));self.assertEqual(path[0]['revenue_index'],100)
     for a,b in zip(path,path[1:]):self.assertTrue(math.isfinite(b['revenue_index']));self.assertAlmostEqual(a['revenue_index']*(1+b['growth']),b['revenue_index'])
    for i in range(6):self.assertLessEqual(f['scenarios']['bear'][i]['revenue_index'],f['scenarios']['base'][i]['revenue_index']);self.assertLessEqual(f['scenarios']['base'][i]['revenue_index'],f['scenarios']['bull'][i]['revenue_index'])
   else:self.assertEqual(f['status'],'INSUFFICIENT_PERMITTED_EVIDENCE')
 def test_wendy_and_paylocity_are_not_generic(self):
  w=self.data['targets']['IQ23557'];p=self.data['targets']['IQ254957567']
  self.assertTrue(w['scenarios']);self.assertTrue(p['scenarios'])
  self.assertNotEqual(w['scenarios']['base'],p['scenarios']['base'])
  self.assertNotAlmostEqual(w['scenarios']['base'][-1]['revenue_index'],127.62815625)
 def test_target_hidden_history_cannot_change_forecast(self):
  t=self.inputs['IQ23557'];f=self.data['targets']['IQ23557'];manifest=read('comparison_rebuild_manifest');sel=read(manifest['groups'][t['target_id']])[t['target_id']]
  series={p['key']:p['revenue_history'] for p in f['peers']};growth={p['key']:{'signals':p['growth_signals']} for p in f['peers']}
  a=build_target(t,sel,series,{},growth,f['canonical_key'])
  series[f['canonical_key']]=[{'period':'2025','period_end':'2025-12-31','value':10**99}]
  b=build_target(t,sel,series,{},growth,f['canonical_key'])
  self.assertEqual(a,b)
  bad=copy.deepcopy(t);bad['target_sec_history']=[100,1000]
  with self.assertRaises(ValueError):build_target(bad,sel,series,{},growth,f['canonical_key'])
 def test_foreign_domains_and_filing_mirrors_rejected(self):
  t=copy.deepcopy(self.inputs['IQ23557']);t['website_quotes']=[{'source_type':'OFFICIAL_WEBSITE','url':'https://evil.example/news','text':'We plan to open new locations and expand capacity in 2027.'},{'source_type':'OFFICIAL_WEBSITE','url':'https://www.wendys.com/investors/annual-report','text':'We plan to open new locations and expand capacity in 2027.'}]
  self.assertEqual(website_signals(t),[])
if __name__=='__main__':unittest.main()
