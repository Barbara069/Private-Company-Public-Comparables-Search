import json,pathlib,time
import lseg.data as ld
P=pathlib.Path(__file__).resolve().parent
mapping=json.loads((P/'target_mapping_560.json').read_text())
targets={t['company_id']:t for t in json.loads((P.parent/'global_comps_560/prepared/Targets_560.json').read_text())}
out=[];ld.open_session()
for t in mapping:
    if t['ric']:continue
    queries=[t['target_name']]
    display=targets[t['company_id']].get('capiq_display_name','').split(' (')[0]
    if display and display.lower()!=t['target_name'].lower():queries.append(display)
    variants=[]
    for q in queries:
        for flag in ['',' and ListingStatus eq \'DEL\'']:
            try:
                d=ld.discovery.search(query=q,view=ld.discovery.Views.EQUITY_QUOTES,filter="(RCSAssetCategoryLeaf eq 'Ordinary Share' or RCSAssetCategoryLeaf eq 'Depository Receipt')"+flag,select='DocumentTitle,RIC,IssueISIN,ListingStatus,RetireDate',top=8)
                records=json.loads(d.to_json(orient='records')) if d is not None else []
                variants.append(dict(query=q,filter=flag,results=records))
            except Exception as e:variants.append(dict(query=q,error=str(e)[:300]))
            time.sleep(.5)
    out.append(dict(target=t,searches=variants));print(t['input_ticker'],[(r.get('RIC'),r.get('DocumentTitle','')[:50]) for v in variants for r in v.get('results',[])][:10],flush=True)
    (P/'identity_exception_searches.json').write_text(json.dumps(out,indent=2))
ld.close_session()
