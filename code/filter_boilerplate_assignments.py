"""Remove obvious boilerplate facet assignments while retaining raw source evidence.
This is a narrow negative filter, not semantic cross-source verification.
"""
from pathlib import Path
import collections,gzip,json,re
from source_policy import require_allowed
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'website/data'
BAN=re.compile(r'cookie (?:policy|settings|consent)|we use cookies|privacy policy|copyright|all rights reserved|forward.looking statements|accounting (?:standard|guidance|policies)|FASB|\bASU\s+(?:No\.?\s*)?20\d{2}|software development stages|capitalization of software costs|internal.use software|fair value|deferred tax|repurchase|stock.based compensation|share.based compensation|pension|subsequent events|unaudited condensed|rights agreement|securities exchange act|indicate by check mark|vote your proxy|terms of use|access denied|captcha|enable javascript',re.I)
def load(p):return json.load(gzip.open(p,'rt'))
def save(p,d):
 require_allowed(d);p.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode(),compresslevel=6,mtime=0))
def run():
 paths=[p for folder in ['research','general_refresh_20261112','quality_refresh_20261112'] for p in sorted((D/folder).glob('*.gz'))]
 bad=collections.defaultdict(set)
 for p in paths:
  for key,profile in load(p).items():
   for eid,e in profile.get('evidence',{}).items():
    if BAN.search(e.get('text','')):bad[key].add(eid)
 stats=collections.Counter()
 def scrub(v,ids):
  if isinstance(v,list):
   for x in v:scrub(x,ids)
  elif isinstance(v,dict):
   for k in ['evidence_ids','other_evidence_ids']:
    if k in v:
     old=v[k];v[k]=[x for x in old if x not in ids];stats['removed_assignment_links']+=len(old)-len(v[k])
   if 'evidence_ids' in v and not v['evidence_ids']:
    v['status']='UNKNOWN_NO_RELEVANT_NONBOILERPLATE_EVIDENCE';v['missing_reason']='No relevant non-boilerplate evidence remains assigned to this business facet.'
   for x in list(v.values()):scrub(x,ids)
 for p in paths:
  data=load(p);before=json.dumps(data,sort_keys=True)
  for key,profile in data.items():
   scrub(profile,bad[key]);
   if 'main_facets' in profile:profile['main_filled']=sum(bool(f.get('evidence_ids')) for f in profile['main_facets'])
  if json.dumps(data,sort_keys=True)!=before:save(p,data);stats['shards_changed']+=1
  stats['shards_checked']+=1
 stats['companies_with_raw_boilerplate']=sum(bool(v) for v in bad.values())
 (ROOT/'code/Boilerplate_Assignment_Audit.json').write_text(json.dumps(dict(stats),indent=2)+'\n');print(dict(stats))
if __name__=='__main__':run()
