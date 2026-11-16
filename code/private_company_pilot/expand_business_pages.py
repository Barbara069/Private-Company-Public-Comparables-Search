from pathlib import Path
import json,gzip,concurrent.futures
import os
R=Path(os.environ.get("PILOT_OUTPUT",str(Path(__file__).parent)));R.mkdir(parents=True,exist_ok=True)
collector=Path(__file__).with_name('collect_websites.py');scope={'__file__':str(collector)};exec(collector.read_text().split('records=[];inputs={}')[0],scope)
inputs=json.load(gzip.open(R/'private_inputs.json.gz','rt'));records=json.load(gzip.open(R/'downloaded_websites.json.gz','rt'))
urls={'GC_MISTPLAY':['https://business.mistplay.com/','https://business.mistplay.com/about-us','https://business.mistplay.com/advertise'],'GC_BRIGHTWAYINSURANCE':['https://www.brightway.com/why','https://www.brightway.com/franchise/our-model','https://www.brightway.com/franchise/faq-ggia']}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for rec in ex.map(lambda j:scope['fetch'](*j),[(tid,inputs[tid]['website'],u) for tid,us in urls.items() for u in us]):
  records.append(rec);inputs[rec['target_id']]['website_quotes']+=rec['quotes'];print(rec['target_id'],rec['status'],rec['requested_url'],len(rec['quotes']))
for v in inputs.values():v['website_quotes']=list({(q['url'],q['text']):q for q in v['website_quotes']}.values())
for name,data in [('expanded_inputs.json.gz',inputs),('downloaded_websites_expanded.json.gz',records)]:
 (R/name).write_bytes(gzip.compress(json.dumps(data,separators=(',',':'),ensure_ascii=False).encode(),mtime=0))
