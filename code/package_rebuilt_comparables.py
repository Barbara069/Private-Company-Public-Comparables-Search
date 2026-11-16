"""Materialize one coherent result version for the website and comprehensive CSV."""
from pathlib import Path
import argparse,collections,gzip,hashlib,json
from source_policy import require_allowed
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'website/data'
def load(p):return json.load(gzip.open(p,'rt')) if p.suffix=='.gz' else json.loads(p.read_text())
def save(p,d):
 require_allowed(d);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode(),compresslevel=6,mtime=0))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',default=str(ROOT.parent/'cache'));a=ap.parse_args();cache=Path(a.cache)
 matches=load(cache/'matches.json.gz');features=load(cache/'target_matching_facets.json.gz');manifest=load(cache/'rebuild_manifest.json');assert len(matches)==560
 tids=sorted(matches);groups={}
 for i in range(0,len(tids),10):
  group='matches/group_'+str(i//10).zfill(2);save(D/(group+'.json.gz'),{tid:matches[tid] for tid in tids[i:i+10]})
  for tid in tids[i:i+10]:groups[tid]=group
 manifest['groups']=groups
 manifest['reproducibility_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [D/'comparison_inputs.json.gz',D/'research_catalog.json.gz',ROOT/'code/rebuild_permitted_comparables.py',ROOT/'code/matching_rules.json',ROOT/'code/scoring_policy_v3.json']}
 save(D/'comparison_rebuild_manifest.json.gz',manifest)
 save(D/'matching_target_facets.json.gz',features)
 from validate_rebuilt_comparables import validate
 results=validate();(ROOT/'code/Comparison_Rebuild_Validation.json').write_text(json.dumps(results,indent=2)+'\n')
 print('Packaged',sum(len(rs) for rs in matches.values()),'comparisons for',len(matches),'targets')
if __name__=='__main__':main()
