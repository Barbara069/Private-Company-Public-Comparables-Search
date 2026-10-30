import json,re
from pathlib import Path
p=Path(__file__).parent
c=json.loads((p/'original_live_companies.json').read_text())
g=json.loads((p/'live_ticker_profile.json').read_text())
def tick(x):return str(x).removesuffix('.0')
def norm(x):return tick(x).replace('.','').upper()
tm={norm(x['target_ciq_ticker']):x['target_company_name'] for x in c}
firmNames={}
for x in g:
 if norm(x['ticker']) in tm:firmNames.setdefault(x['gvkey'],set()).add(tm[norm(x['ticker'])])
gm={k:next(iter(v)) for k,v in firmNames.items() if len(v)==1}
manifest=[]
for x in c:
 t=tick(x['target_ciq_ticker']);cand=[a for a in g if norm(a['ticker'])==norm(t)]
 a=max(cand,key=lambda z:z['latestDate']) if cand else None
 manifest.append({'sheet':re.sub(r'[\[\]:*?/\\]','_',t)[:31],'ticker':t,'name':x['target_company_name'],'gvkey':a['gvkey'] if a else 'NA','date':a['latestDate'] if a else None,'row':a['latestRow'] if a else None})
assert len(manifest)==len({x['sheet'].lower() for x in manifest})==560
(p/'live_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False))
(p/'live_name_maps.json').write_text(json.dumps({'tickers':tm,'firms':gm},ensure_ascii=False))
print(json.dumps({'companies':560,'with_latest_record':sum(x['row'] is not None for x in manifest),'NA':sum(x['row'] is None for x in manifest),'ticker_names':len(tm),'unambiguous_firm_names':len(gm)}))
