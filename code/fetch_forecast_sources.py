from pathlib import Path
import concurrent.futures,datetime,gzip,json,hashlib,io
import requests
from bs4 import BeautifulSoup
import os
R=Path(os.environ.get("FORECAST_WORKDIR",str(Path.cwd()/"outputs/forecast_source_downloads")));R.mkdir(parents=True,exist_ok=True)
SOURCES={
'PAYC_Q32026':('PAYC','2026-11-04','https://investors.paycom.com/news/news-details/2026/Paycom-Software-Inc--Reports-Third-Quarter-2026-Results/default.aspx'),
'PCTY_Q12027':('PCTY','2026-11-05','https://investors.paylocity.com/news-releases/news-release-details/paylocity-announces-first-quarter-fiscal-2027-financial-results'),
'ADP_Q12027':('ADP','2026-10-28','https://s205.q4cdn.com/887941133/files/content_files/ADP-1Q27-Earnings-Release.pdf'),
'PAYX_Q12027':('PAYX','2026-09-23','https://investor.paychex.com/sec-filings/all-sec-filings/content/0000723531-26-000004/payx-ex99_1.htm'),
'ASUR_Q32026':('ASUR','2026-10-29','https://investor.asuresoftware.com/news-releases/news-release-details/asure-announces-third-quarter-2026-results'),
'NETCHEX_MESH_LAUNCH':('GC_NETCHEX','2026-07-20','https://netchex.com/blog/netchex-mesh-ai/'),
'NETCHEX_MESH_EARLY':('GC_NETCHEX','UNKNOWN','https://netchex.com/mesh/'),
'NETCHEX_QUOTE':('GC_NETCHEX','UNKNOWN','https://netchex.com/request-quote/')}
def fetch(item):
 key,(issuer,date,url)=item;rec={'source_id':key,'issuer_id':issuer,'url':url,'publication_date':date,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_type':'OFFICIAL_WEBSITE' if issuer.startswith('GC_') else 'PEER_OFFICIAL_IR','target_input_allowed':issuer.startswith('GC_')}
 try:
  r=requests.get(url,timeout=35,headers={'User-Agent':'Mozilla/5.0 (Company research)'});r.raise_for_status()
  if r.content.startswith(b'%PDF'):
   import tempfile,subprocess
   with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'release.pdf';p.write_bytes(r.content)
    text=subprocess.check_output(['pdftotext','-layout',str(p),'-']).decode('utf-8')
  else:
   soup=BeautifulSoup(r.text,'html.parser')
   for x in soup(['script','style','nav','header','footer']):x.decompose()
   text=soup.get_text(' ',strip=True)
  rec.update(status='DOWNLOADED',final_url=r.url,body_sha256=hashlib.sha256(r.content).hexdigest(),text=text)
 except Exception as e:rec.update(status='UNAVAILABLE',error=str(e),text='')
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:rs=list(ex.map(fetch,SOURCES.items()))
(R/'raw_source_payloads.json.gz').write_bytes(gzip.compress(json.dumps(rs,separators=(',',':')).encode(),mtime=0))
for r in rs:print(r['source_id'],r['status'],len(r['text']))
