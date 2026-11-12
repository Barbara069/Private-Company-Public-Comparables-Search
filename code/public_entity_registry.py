"""Active reference adapter: count DLCs once and quarantine ambiguous WRDS joins."""
from pathlib import Path
import gzip,json
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
RAW=ROOT/'outputs/global_comps_560/global_run_20261028/candidate_reference.json'
CHECKED=P/'entity_identity_review/candidate_reference_identity_checked.json.gz'
def load_reference(eligible_only=True):
 if CHECKED.exists():
  with gzip.open(CHECKED,'rt') as f:rows=json.load(f)
 else:rows=json.loads(RAW.read_text())
 return [r for r in rows if r.get('description_eligible_for_matching',True)] if eligible_only else rows
def canonicalize_pairs(pairs):
 refs=load_reference(False);aliases={a:r for r in refs for a in r.get('entity_alias_rics',[r['candidate_ric']])};out=[];seen=set()
 for pair in pairs:
  c=aliases.get(pair['Candidate RIC'])
  if not c or not c.get('description_eligible_for_matching',True):continue
  key=(pair['Target ID'],c.get('canonical_company_id',c['issuer_id']))
  if key in seen:continue
  seen.add(key)
  out.append({**pair,'Candidate RIC':c['candidate_ric'],'Candidate Name':c['candidate_name'],'Candidate Issuer ID':c['issuer_id'],'Canonical Company ID':c.get('canonical_company_id'),'Candidate Description':c['description'],'Candidate Source':c['description_source'],'Candidate Source URL':c['source_link'],'Candidate Record Locator':c['source_locator'],'Country':c['listing_country'],'Exchange':c['exchange']})
 return out

def load_public_research_evidence(rics):
 """Candidate-side enrichment only. Never called for target website inputs."""
 website=ROOT/'outputs/public_research_website/data';catalog=website/'research_catalog.json.gz'
 if not catalog.exists():return {}
 with gzip.open(catalog,'rt') as f:index=json.load(f)
 wanted={ric:index['aliases'].get(ric) for ric in rics};wanted_keys=set(wanted.values());by_key={}
 for group in {index['groups'][k] for k in wanted.values() if k in index['groups']}:
  with gzip.open(website/(group+'.json.gz'),'rt') as f:profiles=json.load(f)
  for key,p in profiles.items():
   if key not in wanted_keys:continue
   quotes=[]
   for e in p['evidence'].values():
    s=p['sources'][e['source_id']]
    quotes.append({'text':e['text'],'url':s['url'],'source_type':s['source_type'],'document_type':s.get('document_type'),'document_date':s.get('document_date','UNKNOWN'),'report_period':s.get('report_period','UNKNOWN'),'record_locator':s.get('record_locator'),'observed_at':s.get('retrieved_at',s.get('observed_at','UNKNOWN')),'verification':'UNRESTRICTED_PUBLIC_CANDIDATE_RESEARCH; not independent fact verification'})
   overview=p.get('business_description')
   if overview:
    s=p['sources'][overview['source_id']];quotes.append({'text':overview['text'],'url':s['url'],'source_type':s['source_type'],'document_type':s.get('document_type'),'document_date':s.get('document_date','UNKNOWN'),'record_locator':s.get('record_locator'),'verification':'DIRECT_PUBLIC_RESEARCH_BUSINESS_DESCRIPTION'})
   by_key[key]={'quotes':list({(q['url'],q['text']):q for q in quotes}.values()),'modules':p['industry_modules'],'business_description':overview,'sources':p['sources']}
 return {ric:by_key[key] for ric,key in wanted.items() if key in by_key}
