import collections,hashlib,json,pathlib,zipfile,math
from repair_conflicted_facets import P,I,R,O,load,save,quality
from strict_facet_checks import strict_reasons
def main():
 rows=load(O/'Corrected_Facets.json');by={(x['Entity Role'],x['Entity ID'],x['Facet']):x for x in rows};dis=load(O/'Conflict_Dispositions.json');oldflags={(x['Entity Role'],x['Entity ID'],x['Facet']) for x in load(I/'Company_Facet_Validation.json') if x['Validation Status']=='POSSIBLE_CONFLICT_NEEDS_SOURCE_REVIEW'}
 assert len(rows)==len(by)==113310
 assert {(x['Entity Role'],x['Entity ID'],x['Facet']) for x in dis}==oldflags
 assert all(not x['Eligible For Scoring'] and x['Corrected Value'] is None for x in rows if x['Repair Action']=='UNRESOLVED_VALUE_QUARANTINED')
 assert all(x['Source Type']=='OFFICIAL_WEBSITE' for x in rows if x['Entity Role']=='TARGET' and x['Eligible For Scoring'])
 assert all(x['Source Link'] for x in rows if x['Eligible For Scoring'])
 assert quality('Your feedback is our priority, please feel free to reach out.','Revenue Model','Example')
 assert not quality('We charge a monthly fee based on the number of employees using the software.','Revenue Model','Example')
 assert strict_reasons('AAON equipment is easy to startup, commission, and service.','Revenue Model')
 assert strict_reasons('I want to allow this site to sell or share my personal information.','Revenue Model')
 assert strict_reasons('Ms. Bowman joined Akebia in October 2016 and is Senior Vice President.','Core Business Activity')
 assert all(not strict_reasons(x['Corrected Value'],x['Facet']) for x in rows if x['Eligible For Scoring'] and not x['Human Reviewed Fact'])
 for x in rows:
  if x['Company Name']=='TRON Inc' and x['Human Reviewed Fact']:assert x['Fact As Of Date']=='2025-12-31' and x['Source Date']=='2026-03-25'
 ds=load(O/'Corrected_Facet_Scores.json');rs=load(O/'Corrected_Comp_Results.json');groups=collections.defaultdict(list)
 for d in ds:
  groups[d['Target ID'],d['Candidate RIC']].append(d)
  if d['Facet']=='FF49 Industry':continue
  a=by['TARGET',d['Target ID'],d['Facet']];b=by['PUBLIC',d['Candidate RIC'],d['Facet']]
  if not a['Eligible For Scoring'] or not b['Eligible For Scoring']:assert d['Facet Similarity Percent'] is None
 assert len(groups)==len(rs)==5490 and len(ds)==87840
 for r in rs:
  d=groups[r['Target ID'],r['Candidate RIC']];obs=sum(x['Proposed Weight'] for x in d if x['Facet Similarity Percent'] is not None);n=sum(x['Proposed Weight']*x['Facet Similarity Percent'] for x in d if x['Facet Similarity Percent'] is not None)
  assert abs(obs-r['Weighted Evidence Coverage'])<1e-4
  if obs:assert abs(n/obs-r['Partial Observed-Facet Similarity'])<=.011;assert abs(sum((x['Contribution Percent Points'] or 0) for x in d)-r['Partial Observed-Facet Similarity'])<.02
  if r['Similarity Percent'] is None:assert r['Rank'] is None
  else:assert abs(r['Similarity Percent']-r['Partial Observed-Facet Similarity'])<.001
  assert r['Ranking Scope'].startswith('RERANKED_WITHIN_PREVIOUS_10')
 original=hashlib.sha256((R/'Comp_Results.csv').read_bytes()).hexdigest()
 with zipfile.ZipFile(R/'Global_Comps_560_Dataframes.zip') as z:
  n=next(n for n in z.namelist() if n.endswith('Comp_Results.csv'));assert original==hashlib.sha256(z.read(n)).hexdigest()
 v={'all_3016_flags_have_applied_dispositions':True,'all_facet_keys_unique':True,'quarantined_values_excluded_from_all_scores':True,'target_external_information_leakage':False,'all_scored_values_have_source_links':True,'fee_feedback_regression_check':True,'scores_and_weights_reconcile':True,'original_ranking_hash_unchanged':original,'new_ranking_scope':'Previous ten candidate rows only','all_conflicts_factually_resolved':False};save('validation',v);print(json.dumps(v),flush=True)
if __name__=='__main__':main()
