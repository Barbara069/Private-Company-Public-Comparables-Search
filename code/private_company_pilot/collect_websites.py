from pathlib import Path
import requests,concurrent.futures,datetime,json,gzip,re,hashlib
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
import os
R=Path(os.environ.get("PILOT_OUTPUT",str(Path(__file__).parent)));R.mkdir(parents=True,exist_ok=True)
COMPANIES=[('TailorMed','https://www.tailormed.com/'),('PlanHub','https://planhub.com/'),('PureFacts','https://purefacts.com/'),('Duetto','https://www.duettocloud.com/'),('Netchex','https://netchex.com/'),('Revecore','https://revecore.com/'),('Brightway Insurance','https://www.brightway.com/'),('Mistplay','https://www.mistplay.com/')]
now=datetime.datetime.now(datetime.timezone.utc).isoformat();session=requests.Session()
def host(u):return (urlsplit(u).hostname or '').lower().removeprefix('www.')
def fetch(tid,base,url):
 rec={'target_id':tid,'requested_url':url,'retrieved_at':now,'source_type':'OFFICIAL_WEBSITE'}
 try:
  r=session.get(url,timeout=25,headers={'User-Agent':'Mozilla/5.0 (Public company website research)'});r.raise_for_status()
  if not (host(r.url)==host(base) or host(r.url).endswith('.'+host(base))):raise ValueError('Off-domain redirect; not admitted')
  soup=BeautifulSoup(r.text,'html.parser');links=[]
  for a in soup.select('a[href]'):
   u=urljoin(r.url,a['href']).split('#')[0];label=a.get_text(' ',strip=True)
   if host(u)==host(base) and not re.search(r'privacy|cookie|terms|career|blog|news|login|sign-in|demo|contact|press|event|resource|investor|case.stud',u,re.I):
    score=sum(bool(re.search(p,u+' '+label,re.I)) for p in ['product|platform|solution','about|company|what.we.do','customer|industry|who.we','pricing|business|service'])
    if score:links.append((score,u))
  for x in soup(['script','style','nav','header','footer','noscript','svg','form']):x.decompose()
  blocks=list(dict.fromkeys(re.sub(r'\s+',' ',x.get_text(' ',strip=True)).strip() for x in soup.select('p,li,h1,h2,h3,h4')))
  quotes=[{'text':t,'url':r.url,'source_type':'OFFICIAL_WEBSITE','observed_at':now,'document_date':'UNKNOWN','record_locator':'HTML paragraph/list; document SHA256='+hashlib.sha256(r.content).hexdigest(),'verification':'EXACT_HTML_TEXT_NOT_INDEPENDENTLY_VERIFIED'} for t in blocks if 45<=len(t)<=1800 and not re.search(r'cookie|privacy policy|all rights reserved|access denied|captcha|enable javascript',t,re.I)]
  if not quotes:raise ValueError('No eligible HTML paragraphs')
  rec.update(status='DOWNLOADED',url=r.url,text='\n'.join(blocks),quotes=quotes,sha256=hashlib.sha256(r.content).hexdigest(),links=[u for _,u in sorted(set(links),reverse=True)])
 except Exception as e:rec.update(status='UNAVAILABLE',error=str(e),quotes=[],links=[])
 return rec
records=[];inputs={}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 homes=list(ex.map(lambda c:fetch('GC_'+re.sub('[^A-Z0-9]','',c[0].upper()),c[1],c[1]),COMPANIES));records+=homes
 jobs=[]
 for (name,base),home in zip(COMPANIES,homes):
  tid=home['target_id'];inputs[tid]={'target_name':name,'website':base,'website_quotes':home['quotes'],'available_financials':{'revenue':None,'ebitda':None,'debt':None},'financial_provenance':{'units':'UNKNOWN — no private financials supplied','period':'UNKNOWN'},'target_kind':'ACTUAL_PRIVATE_PORTFOLIO_COMPANY','portfolio_membership_source':'https://www.growthcurvecapital.com/portfolio','portfolio_evidence_used_for_matching':False}
  seen={base,home.get('url')}
  for u in home['links']:
   if u not in seen:jobs.append((tid,base,u));seen.add(u)
   if len(seen)>=7:break
 for rec in ex.map(lambda j:fetch(*j),jobs):
  records.append(rec);inputs[rec['target_id']]['website_quotes']+=rec['quotes']
for v in inputs.values():v['website_quotes']=list({(q['url'],q['text']):q for q in v['website_quotes']}.values())
for name,data in [('private_inputs.json.gz',inputs),('downloaded_websites.json.gz',records)]:
 (R/name).write_bytes(gzip.compress(json.dumps(data,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
print(json.dumps({'companies':len(inputs),'requests':len(records),'successful':sum(r['status']=='DOWNLOADED' for r in records),'passages_by_company':{v['target_name']:len(v['website_quotes']) for v in inputs.values()}},indent=2))
