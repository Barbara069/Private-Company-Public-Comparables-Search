import json,pathlib,urllib.request,time,datetime,concurrent.futures as cf,sys
from collect_web_evidence import TextParser
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'web_evidence';RAW=OUT/'sec';RAW.mkdir(exist_ok=True)
UA='Barbara Bai company research hb2885@columbia.edu'
targets=json.loads((ROOT/'prepared/Targets_560.json').read_text())
registry=json.loads(pathlib.Path('/tmp/sec_company_tickers.json').read_text())
(OUT/'sec_company_tickers.json').write_text(json.dumps(registry))
lookup={r['ticker']:r for r in registry.values()}

def get(url,path):
    if path.exists(): return path.read_bytes()
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept-Encoding':'identity'})
    with urllib.request.urlopen(req,timeout=25) as r:b=r.read()
    path.write_bytes(b);time.sleep(.4);return b

def collect(t):
    tic=t['ticker'].replace('.','-');reg=lookup.get(tic)
    row={'company_id':t['company_id'],'company_name':t['company_name'],'ticker':t['ticker'],'source_type':'SEC_EDGAR','status':'NO_EXACT_CURRENT_SEC_TICKER_MATCH'}
    if not reg:return row
    cik=reg['cik_str'];row.update(cik=cik,sec_name=reg['title'],identity_status='TICKER_LOOKUP_REQUIRES_ENTITY_REVIEW')
    u=f'https://data.sec.gov/submissions/CIK{cik:010d}.json';row['source_url']=u
    try:
        data=json.loads(get(u,RAW/f'{cik}_submissions.json'))
        row.update(sic=data.get('sic'),sic_description=data.get('sicDescription'),sec_name=data.get('name'),exchanges=data.get('exchanges'),tickers=data.get('tickers'))
        recent=data.get('filings',{}).get('recent',{})
        idx=next((i for i,f in enumerate(recent.get('form',[])) if f in ('10-K','20-F','40-F') and recent['filingDate'][i]<='2026-10-27'),None)
        if idx is None:row['status']='NO_ANNUAL_FORM_IN_RECENT_INDEX';return row
        accession=recent['accessionNumber'][idx];doc=recent['primaryDocument'][idx]
        filing=f'https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace("-","")}/{doc}'
        row.update(status='ANNUAL_FILING_IDENTIFIED_NOT_READ',form=recent['form'][idx],filing_date=recent['filingDate'][idx],report_date=recent['reportDate'][idx],annual_filing_url=filing)
        return row
    except Exception as e:row.update(status='SEC_FETCH_FAILED',error=str(e)[:180]);return row

def main():
    if '--all-annual' in sys.argv:
        rows=json.loads((OUT/'sec_index.json').read_text())
        jobs=[];seen=set()
        for r in rows:
            if not r.get('annual_filing_url') or r.get('text_file') or r['cik'] in seen:continue
            seen.add(r['cik']);jobs.append(r)
        def annual(r):
            try:
                cik=r['cik'];html=get(r['annual_filing_url'],RAW/f'{cik}_annual.html').decode('utf-8',errors='replace')
                p=TextParser();p.feed(html);text='\n'.join(' '.join(x.split()) for x in ''.join(p.parts).splitlines() if x.strip())
                fp=RAW/f'{cik}_annual.txt';fp.write_text(text)
                r.update(status='ANNUAL_TEXT_FETCHED_NOT_FACT_VERIFIED',text_file=str(fp),text_characters=len(text))
            except Exception as e:r.update(annual_text_status='FETCH_FAILED',annual_error=str(e)[:180])
            return r
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for i,r in enumerate(ex.map(annual,jobs),1):
                if i%50==0:print('Additional SEC annual texts',i,'/',len(jobs),flush=True)
        (OUT/'sec_index.json').write_text(json.dumps(rows,indent=2))
        print('Annual reports with text',sum(bool(r.get('text_file')) for r in rows),flush=True)
        return
    extra=['MCD','QSR','YUM','DPZ','PZZA','ARCO','PAYX','WDAY','TNET','NSP','INTU','SAP','ORCL']
    tasks=targets+[dict(company_id=x,company_name=lookup.get(x,{}).get('title',x),ticker=x) for x in extra]
    rows=[]
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for i,r in enumerate(ex.map(collect,tasks),1):
            rows.append(r)
            if i%80==0:print('SEC indices',i,'/',len(tasks),flush=True)
    (OUT/'sec_index.json').write_text(json.dumps(rows,indent=2))
    seed=set(['WEN','PCTY','JACK','MCD','QSR','WING','YUM','DPZ','PZZA','LOCO','SHAK','ARCO','PAYC','PAYX','ASUR','ADP','WDAY','TNET','NSP','INTU','SAP','ORCL'])
    for r in rows:
        if r['ticker'] not in seed or not r.get('annual_filing_url'):continue
        try:
            cik=r['cik'];html=get(r['annual_filing_url'],RAW/f'{cik}_annual.html').decode('utf-8',errors='replace')
            p=TextParser();p.feed(html);text='\n'.join(' '.join(x.split()) for x in ''.join(p.parts).splitlines() if x.strip())
            fp=RAW/f'{cik}_annual.txt';fp.write_text(text)
            r.update(status='ANNUAL_TEXT_FETCHED_NOT_FACT_VERIFIED',text_file=str(fp),text_characters=len(text))
            print('Annual text',r['ticker'],len(text),flush=True)
        except Exception as e:r.update(annual_text_status='FETCH_FAILED',annual_error=str(e)[:180])
    (OUT/'sec_index.json').write_text(json.dumps(rows,indent=2))
    print('SEC finished',len(rows),flush=True)
if __name__=='__main__':main()
