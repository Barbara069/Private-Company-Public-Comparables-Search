import lseg.data as ld,json,pathlib,time
P=pathlib.Path(__file__).resolve().parent
todo=json.loads((P/'symbol_lookup_needed.json').read_text())
out=[];ld.open_session()
for t in todo:
    try:
        d=ld.discovery.search(query=t['company_name'],view=ld.discovery.Views.EQUITY_QUOTES,select='DocumentTitle,RIC,IssueISIN',top=5)
        rows=json.loads(d.to_json(orient='records')) if d is not None else []
        out.append(dict(target=t,results=rows));print(t['ticker'],[(r.get('RIC'),r.get('DocumentTitle','')[:70]) for r in rows],flush=True)
    except Exception as e:out.append(dict(target=t,error=str(e)[:500]));print(t['ticker'],type(e).__name__,flush=True)
    time.sleep(1)
(P/'missing_symbol_search_results.json').write_text(json.dumps(out,indent=2));ld.close_session()
