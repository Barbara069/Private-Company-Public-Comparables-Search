"""Resumable public-reference collection. Never uses rich target facts for target profiles."""
import concurrent.futures as cf,datetime as dt,hashlib,json,pathlib,re,time,sys
import requests
from bs4 import BeautifulSoup
P=pathlib.Path(__file__).resolve().parent
O=P/'global_run_20261028';O.mkdir(exist_ok=True)
def save(p,x):
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str))
def universe():
    import lseg.data as ld
    ld.open_session();rows=[]
    base="ListingStatus eq 'LIS' and IsPrimaryIssueRIC eq true and RCSAssetCategoryLeaf eq 'Ordinary Share'"
    # Separate capitalization bands avoid the discovery service's 10,000-hit window.
    bands=["MktCapCompanyUsd ge 10000000000","MktCapCompanyUsd ge 1000000000 and MktCapCompanyUsd lt 10000000000","MktCapCompanyUsd ge 100000000 and MktCapCompanyUsd lt 1000000000","MktCapCompanyUsd ge 10000000 and MktCapCompanyUsd lt 100000000","MktCapCompanyUsd lt 10000000"]
    for k,band in enumerate(bands):
        for skip in range(0,10000,1000):
            p=O/f'universe_{k}_{skip}.json'
            if p.exists():a=json.loads(p.read_text())
            else:
                d=ld.discovery.search(view=ld.discovery.Views.EQUITY_QUOTES,filter=base+' and '+band,select='RIC,DocumentTitle,IssuerOAPermID,IssueISIN,RCSExchangeCountryLeaf,ExchangeName,MktCapCompanyUsd',top=1000,skip=skip,order_by='MktCapCompanyUsd desc')
                a=json.loads(d.to_json(orient='records'));save(p,a)
            rows.extend(a);print('Global listed reference',k,skip,len(a),'cumulative',len(rows),flush=True)
            if len(a)<1000:break
    # Universe without a market cap remains a separate discovery limitation.
    unique={r['RIC']:r for r in rows if r.get('RIC')}
    save(O/'listed_universe.json',list(unique.values()));ld.close_session()
def profiles():
    import lseg.data as ld
    u=json.loads((O/'listed_universe.json').read_text());rics=[r['RIC'] for r in u]
    fields=['TR.CommonName','TR.BusinessSummary','TR.HeadquartersCountry','TR.TRBCBusinessSector','TR.TRBCIndustryGroup','TR.TRBCIndustry','TR.PrimaryRIC','TR.ISIN','TR.CUSIP','TR.ExchangeName']
    ld.open_session();rows=[]
    cache=O/'profile_batches';cache.mkdir(exist_ok=True)
    for start in range(0,len(rics),100):
        batch=rics[start:start+100];key=hashlib.sha256(json.dumps([batch,fields]).encode()).hexdigest()[:20];p=cache/(key+'.json')
        if p.exists():a=json.loads(p.read_text())
        else:
            a=[]
            for attempt in range(3):
                try:
                    d=ld.get_data(batch,fields,header_type=ld.HeaderType.NAME)
                    a=json.loads(d.to_json(orient='records'));save(p,a);break
                except Exception as e:
                    print('Profile request retry',start,str(e)[:160],flush=True);time.sleep(2)
        rows.extend(a)
        if start%1000==0:save(O/'public_profiles.json',rows);print('Public descriptions',min(start+100,len(rics)),'/',len(rics),flush=True)
    save(O/'public_profiles.json',rows);ld.close_session()
def shortlist():
    import lseg.data as ld
    rics=sorted({r['candidate_ric'] for r in json.loads((O/'retrieval_top25.json').read_text())})
    prior=json.loads((O/'shortlist_profiles.json').read_text()) if (O/'shortlist_profiles.json').exists() else []
    present={r['Instrument'] for r in prior};rics=[r for r in rics if r not in present]
    fields=['TR.CommonName','TR.BusinessSummary','TR.HeadquartersCountry','TR.TRBCBusinessSector','TR.TRBCIndustryGroup','TR.TRBCIndustry','TR.PrimaryRIC','TR.ISIN','TR.CUSIP','TR.ExchangeName','TR.TotalRevenue','TR.EBITDA','TR.TotalDebt','TR.TotalRevenue.date','TR.TotalRevenue.currency','TR.TotalRevenue.fperiod']
    params={'Period':'FY0','Curn':'USD','Scale':0};ld.open_session();cache=O/'shortlist_batches';cache.mkdir(exist_ok=True)
    batches=[rics[i:i+75] for i in range(0,len(rics),75)]
    def get(batch):
        key=hashlib.sha256(json.dumps([batch,fields,params]).encode()).hexdigest()[:20];p=cache/(key+'.json')
        if p.exists():return json.loads(p.read_text())
        for attempt in range(3):
            try:
                d=ld.get_data(batch,fields,parameters=params,header_type=ld.HeaderType.NAME);a=json.loads(d.to_json(orient='records'));save(p,a);return a
            except Exception as e:
                print('Shortlist retry',str(e)[:140],flush=True);time.sleep(3)
        return []
    rows=list(prior)
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for i,a in enumerate(ex.map(get,batches),1):
            rows.extend(a)
            if i%10==0:save(O/'shortlist_profiles.json',rows);print('Shortlist descriptions',i,'/',len(batches),flush=True)
    save(O/'shortlist_profiles.json',rows);ld.close_session();print('Shortlist profile rows',len(rows),flush=True)
def websites():
    targets=json.loads((P/'prepared/Targets_560.json').read_text());old=json.loads((P/'web_evidence/collection.json').read_text())
    ok={r['company_id'] for r in old if r['status']=='FETCHED_TEXT_NOT_FACT_VERIFIED' and r.get('text_file')}
    missing=[t for t in targets if t['company_id'] not in ok]
    raw=O/'website_retry';raw.mkdir(exist_ok=True)
    def fetch(t):
        ident=t['company_id'];cache=raw/(ident+'.json')
        if cache.exists():return json.loads(cache.read_text())
        results=[];url=t['website'];url=url if '://' in url else 'https://'+url
        for suffix in ['', '/about-us','/about','/company/about-us/']:
            link=url.rstrip('/')+suffix
            try:
                r=requests.get(link,timeout=16,headers={'User-Agent':'Mozilla/5.0 (compatible; CompanyResearch/1.0)'})
                if r.status_code!=200:continue
                soup=BeautifulSoup(r.content,'html.parser')
                for e in soup(['script','style','noscript','svg','nav','header','footer']):e.decompose()
                text='\n'.join(x.strip() for x in soup.get_text('\n').splitlines() if len(x.strip())>25)
                if len(text)<300 or re.search('verify you are human|access denied|enable javascript and cookies|just a moment',text[:1200],re.I):continue
                f=raw/(hashlib.sha256(link.encode()).hexdigest()[:16]+'.txt');f.write_text(text)
                results.append(dict(company_id=ident,company_name=t['company_name'],role='TARGET',requested_url=link,source_url=r.url,text_file=str(f),text_characters=len(text),status='FETCHED_TEXT_NOT_FACT_VERIFIED',source_type='COMPANY_WEBSITE',source_date='UNKNOWN',retrieved_at=dt.datetime.now(dt.timezone.utc).isoformat()))
                if len(results)>=2:break
            except Exception:pass
        save(cache,results);return results
    extra=[]
    with cf.ThreadPoolExecutor(max_workers=12) as pool:
        for i,a in enumerate(pool.map(fetch,missing),1):
            extra.extend(a)
            if i%20==0:print('Website retry',i,'/',len(missing),'readable sources',len(extra),flush=True)
    save(O/'website_retry_collection.json',extra)
    print('Additional targets',len({r['company_id'] for r in extra}),flush=True)
if __name__=='__main__':
    {'universe':universe,'profiles':profiles,'websites':websites,'shortlist':shortlist}[sys.argv[1]]()
