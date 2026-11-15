from pathlib import Path
import csv,gzip,hashlib,json,collections
P=Path(__file__).resolve().parent;OUT=P.parents[1]/'outputs/clean_research_delivery';csv.field_size_limit(2**31-1);stats=collections.Counter()
for role,name in [('TARGET','Targets_560.csv.gz'),('PUBLIC','Public_Companies.csv.gz')]:
 counts=collections.Counter();seen=set()
 with gzip.open(OUT/name,'rt',encoding='utf-8-sig',newline='') as f:
  r=csv.DictReader(f);assert r.fieldnames==['dataset','company_id','company_name','entity_role','facet','source_url','source_date','text','record_json']
  for row in r:
   ds=row['dataset']
   if ds in ['Unified_Public_Research','SEC_Availability_20261111','Downloaded_SEC_Disclosure_20261111','Extraction_Completeness_20261111']:
    assert row['entity_role']==role;counts[ds]+=1;obj=json.loads(row['record_json'])
    if ds=='Unified_Public_Research':assert row['company_id'] not in seen;seen.add(row['company_id']);assert len(obj['main_facets'])==32
    if ds=='Downloaded_SEC_Disclosure_20261111':assert row['text']==obj['text'];assert hashlib.sha256(row['text'].encode()).hexdigest()==obj['text_sha256'];assert not obj['used_in_pseudo_private_matching'];assert row['source_url']==obj['source_url'];assert obj['filing_date'] and obj['form']
 for k,v in counts.items():stats[k]+=v
 print(name,dict(counts),flush=True)
assert stats['Unified_Public_Research']==38859 and stats['Extraction_Completeness_20261111']==38859
assert stats['Downloaded_SEC_Disclosure_20261111']==643 and stats['SEC_Availability_20261111']==582
(P/'csv_readback_validation_20261111.json').write_text(json.dumps(dict(stats),indent=2));print('PASS: two CSVs read back; new source full text, hashes, roles, dates and links verified.',flush=True)
