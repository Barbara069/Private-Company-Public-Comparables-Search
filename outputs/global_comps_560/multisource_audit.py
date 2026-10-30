"""Add document provenance without changing scores or target selection inputs."""
import concurrent.futures as cf,csv,datetime as dt,hashlib,json,pathlib,re,sys,time,threading,difflib
from urllib.parse import urlparse,urljoin
import requests
from bs4 import BeautifulSoup
P=pathlib.Path(__file__).resolve().parent;R=P/'global_run_20261028';O=P/'multisource_audit_20261028';O.mkdir(exist_ok=True)
RAW=O/'raw';RAW.mkdir(exist_ok=True)
def load(p):return json.loads(pathlib.Path(p).read_text())
def store(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str))
def write(name,rows):
    store(O/(name+'.json'),rows)
    if rows:
        cols=list(dict.fromkeys(k for r in rows for k in r))
        with (O/(name+'.csv')).open('w') as f:
            w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
def host(u):
    if not isinstance(u,str):return ''
    return urlparse(u if '://' in u else 'https://'+u).netloc.lower().removeprefix('www.')
def norm(s):return ''.join(w for w in re.findall('[a-z0-9]+',str(s).lower()) if w not in {'the','inc','corp','corporation','limited','ltd','plc','co','company','holdings','holding','group','class','a','b'})
def cleanhtml(content):
    soup=BeautifulSoup(content,'html.parser')
    title=soup.title.get_text(' ',strip=True) if soup.title else ''
    links=[a.get('href','') for a in soup.find_all('a',href=True)]
    for e in soup(['script','style','noscript','svg','nav','header','footer']):e.decompose()
    text='\n'.join(s.strip() for s in soup.get_text('\n').splitlines() if len(s.strip())>20)
    return title,text,links
def fetchweb():
    candidates=load(R/'Candidate_Data.json');prior=load(P/'web_evidence/collection.json')
    prior+=load(R/'website_retry_collection.json')
    by= {}
    for x in prior:
        if x.get('status')=='FETCHED_TEXT_NOT_FACT_VERIFIED' and x.get('text_file'):by.setdefault(host(x.get('source_url') or x['requested_url']),[]).append(x)
    def get(c):
        ric=c['candidate_ric'];p=RAW/(hashlib.sha256(ric.encode()).hexdigest()[:16]+'_web.json')
        if p.exists():return load(p)
        h=host(c.get('candidate_website'));base={'ric':ric,'name':c['candidate_name'],'source_type':'OFFICIAL_WEBSITE','identity_status':'URL_FROM_WRDS_REFERENCE_NOT_MANUALLY_IDENTITY_VERIFIED'}
        if not h:return [dict(base,status='NO_WEBSITE_IN_AVAILABLE_REFERENCE',source_url=None)]
        if h in by:
            out=[dict(base,status='CACHED_OFFICIAL_TEXT_AVAILABLE',source_url=x.get('source_url') or x['requested_url'],text_file=x['text_file'],retrieved_at=x.get('retrieved_at'),source_date='UNKNOWN',title=x.get('source_title')) for x in by[h][:3]];store(p,out);return out
        out=[];home='https://'+h
        try:
            resp=requests.get(home,timeout=12,headers={'User-Agent':'Mozilla/5.0 (compatible; CompanyResearch/1.0)'})
            title,text,links=cleanhtml(resp.content)
            good=resp.status_code==200 and len(text)>250 and not re.search(r'just a moment|verify you are human|access denied|enable javascript and cookies',text[:1500],re.I)
            if not good:out.append(dict(base,status='BLOCKED_THIN_OR_HTTP_ERROR',source_url=resp.url,http_status=resp.status_code,title=title))
            else:
                f=p.with_suffix('.txt');f.write_text(text);out.append(dict(base,status='OFFICIAL_TEXT_FETCHED_NOT_FACT_VERIFIED',source_url=resp.url,text_file=str(f),retrieved_at=dt.datetime.now(dt.timezone.utc).isoformat(),source_date='UNKNOWN',title=title,content_hash=hashlib.sha256(text.encode()).hexdigest()))
                sub=next((urljoin(resp.url,u) for u in links if re.search(r'about|our-company|who-we-are|our-business',u,re.I) and host(urljoin(resp.url,u))==host(resp.url) and not re.search(r'news|blog|privacy|career|\.pdf',u,re.I)),None)
                if sub and sub.rstrip('/')!=resp.url.rstrip('/'):
                    s=requests.get(sub,timeout=10,headers={'User-Agent':'Mozilla/5.0'});title2,text2,_=cleanhtml(s.content)
                    if s.status_code==200 and len(text2)>250 and not re.search(r'verify you are human|access denied',text2[:1000],re.I):
                        f2=p.with_name(p.stem+'_about.txt');f2.write_text(text2);out.append(dict(base,status='OFFICIAL_TEXT_FETCHED_NOT_FACT_VERIFIED',source_url=s.url,text_file=str(f2),retrieved_at=dt.datetime.now(dt.timezone.utc).isoformat(),source_date='UNKNOWN',title=title2,content_hash=hashlib.sha256(text2.encode()).hexdigest()))
        except Exception as e:out.append(dict(base,status='FETCH_FAILED',source_url=home,error=str(e)[:180]))
        store(p,out);return out
    rows=[]
    with cf.ThreadPoolExecutor(max_workers=18) as pool:
        for i,a in enumerate(pool.map(get,candidates),1):
            rows.extend(a)
            if i%250==0:store(O/'public_web_index.json',rows);print('Public websites',i,'/',len(candidates),flush=True)
    store(O/'public_web_index.json',rows);print('Website complete',len(rows),flush=True)
LOCK=threading.Lock();NEXT=0.
def secget(url):
    global NEXT
    with LOCK:
        now=time.monotonic();pause=max(0,NEXT-now);NEXT=max(now,NEXT)+.18
    if pause:time.sleep(pause)
    r=requests.get(url,timeout=20,headers={'User-Agent':'Barbara Bai academic research hb2885@columbia.edu','Accept-Encoding':'gzip, deflate'});r.raise_for_status();return r
def fetchsec():
    cs=load(R/'Candidate_Data.json');reg={r['ticker']:r for r in load(P/'web_evidence/sec_company_tickers.json').values()}
    cached={int(x['cik']):x for x in load(P/'web_evidence/sec_index.json') if x.get('cik') and x.get('text_file')}
    def get(c):
        p=RAW/(hashlib.sha256(c['candidate_ric'].encode()).hexdigest()[:16]+'_sec.json')
        if p.exists():return load(p)
        ric=c['candidate_ric'];tic=ric.split('.')[0].replace('/','-');hit=reg.get(tic)
        row=dict(ric=ric,name=c['candidate_name'],source_type='SEC_ANNUAL_FILING',status='NO_CONSERVATIVE_SEC_TICKER_NAME_MATCH',source_url=None)
        if not hit:return row
        a=norm(c['candidate_name']);b=norm(hit['title']);similar=difflib.SequenceMatcher(None,a,b).ratio()
        if not (similar>=.72 or (min(len(a),len(b))>=5 and (a.startswith(b) or b.startswith(a)))):return dict(row,status='SEC_TICKER_NAME_MISMATCH_NOT_JOINED')
        cik=int(hit['cik_str']);row.update(cik=cik,identity_status='CURRENT_SEC_TICKER_AND_NAME_CONSERVATIVE_MATCH_REVIEW',sec_name=hit['title'])
        if cik in cached:
            s=cached[cik];row.update(status='CACHED_ANNUAL_TEXT_AVAILABLE',source_url=s['annual_filing_url'],text_file=s['text_file'],form=s['form'],filing_date=s['filing_date'],report_date=s.get('report_date'));store(p,row);return row
        try:
            suburl=f'https://data.sec.gov/submissions/CIK{cik:010d}.json';data=secget(suburl).json();f=data.get('filings',{}).get('recent',{})
            ix=next((i for i,v in enumerate(f.get('form',[])) if v in ('10-K','20-F','40-F') and f['filingDate'][i]<='2026-10-28'),None)
            if ix is None:row.update(status='NO_ANNUAL_FORM_IN_RECENT_INDEX',source_url=suburl)
            else:
                accession=f['accessionNumber'][ix].replace('-','');url=f'https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{f["primaryDocument"][ix]}'
                row.update(status='ANNUAL_IDENTIFIED_NOT_READ',source_url=url,form=f['form'][ix],filing_date=f['filingDate'][ix],report_date=f['reportDate'][ix])
                html=secget(url).content;_,text,_=cleanhtml(html);tp=p.with_suffix('.txt');tp.write_text(text)
                row.update(status='ANNUAL_TEXT_FETCHED_NOT_FACT_VERIFIED',text_file=str(tp),retrieved_at=dt.datetime.now(dt.timezone.utc).isoformat(),content_hash=hashlib.sha256(text.encode()).hexdigest())
        except Exception as e:row.update(status='SEC_FETCH_FAILED',error=str(e)[:180])
        store(p,row);return row
    rows=[]
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        for i,row in enumerate(pool.map(get,cs),1):
            rows.append(row)
            if i%250==0:store(O/'public_sec_index.json',rows);print('SEC checks',i,'/',len(cs),flush=True)
    store(O/'public_sec_index.json',rows);print('SEC complete',len(rows),flush=True)
if __name__=='__main__':{'web':fetchweb,'sec':fetchsec}[sys.argv[1]]()
