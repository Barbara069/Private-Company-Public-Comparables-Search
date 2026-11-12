"""Refresh SEC availability; date-bound, resumable and never a claim of fact verification."""
from pathlib import Path
import concurrent.futures,datetime,hashlib,json,threading,time
import urllib.request,types
from lxml import html
P=Path(__file__).resolve().parent;O=P/'downloads/latest_disclosures_20261111';O.mkdir(exist_ok=True)
rows=json.loads((P.parents[1]/'outputs/global_comps_560/web_evidence/sec_index.json').read_text());cutoff='2026-11-11'
headers={'User-Agent':'Barbara Bai academic company research hb2885@columbia.edu','Accept-Encoding':'identity'}
lock=threading.Lock();last=[0.0]
def get(url):
 with lock:
  wait=.3-(time.monotonic()-last[0])
  if wait>0:time.sleep(wait)
  last[0]=time.monotonic()
 request=urllib.request.Request(url,headers=headers)
 with urllib.request.urlopen(request,timeout=30) as response:body=response.read().decode('utf-8','replace')
 return types.SimpleNamespace(text=body,json=lambda:json.loads(body))
# Reuse original downloaded text only for the exact same accession URL.
cache={}
for r in json.loads((P/'downloads/sec_quarterly/all_records.json').read_text()):
 if r.get('text'):cache[r.get('source_url')]=r['text']
for r in rows:
 if r.get('annual_filing_url') and r.get('text_file') and Path(r['text_file']).exists():cache[r['annual_filing_url']]=Path(r['text_file']).read_text()
for old in (P/'downloads/latest_disclosures_20261030').glob('*.json'):
 if old.name=='summary.json':continue
 for doc in json.loads(old.read_text()).get('documents',[]):
  if doc.get('text'):cache[doc['source_url']]=doc['text']
for ric,name,cik in [('MSFT.O','Microsoft Corporation',789019),('NVDA.O','NVIDIA Corporation',1045810),('AAPL.O','Apple Inc.',320193),('AMZN.O','Amazon.com Inc',1018724),('BRKa','Berkshire Hathaway Inc',1067983),('KO','Coca-Cola Co',21344),('PEP.O','PepsiCo Inc',77476),('DIS','The Walt Disney Company',1744489),('MMM','3M Company',66740)]:
 if not any(str(r.get('cik')).lstrip('0')==str(cik) for r in rows):rows.append({'company_id':ric,'company_name':name,'cik':cik,'identity_status':'PUBLIC_ISSUER_CIK_REQUIRES_PROFILE_CROSSCHECK'})
def work(row):
 path=O/(row['company_id']+'.json')
 if path.exists():return json.loads(path.read_text())
 out={k:row.get(k) for k in ['company_id','company_name','cik','identity_status']};out.update(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),as_of=cutoff,documents=[],selector_eligible=False)
 if not row.get('cik'):out['status']='NO_VERIFIED_CIK_IN_EXISTING_MAPPING';path.write_text(json.dumps(out));return out
 try:
  url=f"https://data.sec.gov/submissions/CIK{int(row['cik']):010d}.json";data=get(url).json();f=data['filings']['recent'];out['submissions_url']=url;out['submissions']=data
  eligible=[i for i,v in enumerate(f['filingDate']) if v<=cutoff]
  picks=set()
  for forms in [{'10-K','10-K/A','20-F','20-F/A','40-F','40-F/A'},{'10-Q','10-Q/A'}]:
   inds=[i for i in eligible if f['form'][i] in forms]
   if inds:
    i=max(inds,key=lambda j:(f['reportDate'][j],f['filingDate'][j]));picks.add(i)
    # Keep original plus amendment for the selected period, not just one replacement document.
    picks.update(j for j in inds if f['reportDate'][j]==f['reportDate'][i])
  # Furnished/current reports are supplements, never automatic replacements for all annual facts.
  inds=[i for i in eligible if f['form'][i] in ['8-K','8-K/A','6-K','6-K/A']]
  picks.update(sorted(inds,key=lambda j:f['filingDate'][j],reverse=True)[:1])
  for i in sorted(picks):
   acc=f['accessionNumber'][i];doc=f['primaryDocument'][i];u=f"https://www.sec.gov/Archives/edgar/data/{int(row['cik'])}/{acc.replace('-','')}/{doc}"
   d=dict(form=f['form'][i],filing_date=f['filingDate'][i],report_date=f['reportDate'][i],accession=acc,source_url=u,primary_document=doc)
   try:
    text=cache.get(u)
    if text:d['acquisition']='EXACT_ACCESSION_CACHE_REUSED_AFTER_LIVE_AVAILABILITY_CHECK'
    else:
     response=get(u);soup=html.fromstring(response.text.encode("utf-8"))
     for tag in soup.xpath('//script|//style'):tag.drop_tree()
     text='\n'.join(t.strip() for t in soup.itertext() if t.strip());d['acquisition']='DOWNLOADED'
    d.update(text=text,text_sha256=hashlib.sha256(text.encode()).hexdigest(),status='DOWNLOADED_NOT_FACT_VERIFIED')
   except Exception as e:d.update(status='DOWNLOAD_FAILED',error_type=type(e).__name__)
   out['documents'].append(d)
  out['status']='AVAILABILITY_CHECKED_WITH_DOWNLOAD_GAPS' if any(x['status']=='DOWNLOAD_FAILED' for x in out['documents']) else 'AVAILABILITY_CHECKED'
 except Exception as e:out.update(status='AVAILABILITY_CHECK_FAILED',error_type=type(e).__name__)
 path.write_text(json.dumps(out,ensure_ascii=False));return out
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for i,r in enumerate(ex.map(work,rows),1):
  results.append(r)
  if i%40==0 or i==len(rows):print('Checked',i,'/',len(rows),'downloaded/reused',sum(sum(bool(d.get('text')) for d in x['documents']) for x in results),flush=True)
summary={'as_of':cutoff,'companies':len(results),'statuses':{s:sum(x['status']==s for x in results) for s in set(x['status'] for x in results)},'documents':sum(len(x['documents']) for x in results),'downloaded':sum(sum(d.get('acquisition')=='DOWNLOADED' for d in x['documents']) for x in results),'scope':'Existing SEC-mapped entities only; not all global public issuers; issuer identity mappings not independently reverified'}
(O/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
