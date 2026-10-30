"""Collect source text, not inferred company facts or final comp scores."""
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import pathlib
import time
import urllib.request
import urllib.error
import urllib.parse
import re
import sys
from html.parser import HTMLParser

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.hidden=0; self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','noscript','svg'): self.hidden+=1
        if tag in ('p','div','li','h1','h2','h3','tr','br'): self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style','noscript','svg') and self.hidden: self.hidden-=1
        if tag in ('p','div','li','tr'): self.parts.append('\n')
    def handle_data(self,data):
        if not self.hidden:self.parts.append(data+' ')

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 'web_evidence'
OUT.mkdir(exist_ok=True)
RAW = OUT / 'raw'
RAW.mkdir(exist_ok=True)
TARGETS = json.loads((ROOT/'prepared/Targets_560.json').read_text())
UA = 'Company comparison research; contact hb2885@columbia.edu'

def collect(task):
    ident, name, role, url = task
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    meta_path = RAW / (key+'.json')
    if meta_path.exists():
        old = json.loads(meta_path.read_text())
        return dict(old, company_id=ident, company_name=name, role=role)
    row = dict(company_id=ident, company_name=name, role=role,
               requested_url=url, source_type='COMPANY_WEBSITE',
               retrieved_at=dt.datetime.now(dt.timezone.utc).isoformat(),
               status='NOT_FETCHED', source_date='UNKNOWN')
    try:
        r = urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=18)
        row.update(http_status=r.status, source_url=r.url)
        if 'html' not in r.headers.get('content-type','').lower():
            row['status']='NON_HTML_NOT_EXTRACTED'
        else:
            html=r.read(15000000).decode('utf-8',errors='replace')
            (RAW/(key+'.html')).write_text(html)
            parser=TextParser();parser.feed(html)
            row['source_title']=name+' company website'
            text='\n'.join(' '.join(x.split()) for x in ''.join(parser.parts).splitlines() if x.strip())
            (RAW/(key+'.txt')).write_text(text)
            row.update(text_file=str(RAW/(key+'.txt')),text_characters=len(text),
                       content_hash=hashlib.sha256(text.encode()).hexdigest(),
                       status='FETCHED_TEXT_NOT_FACT_VERIFIED' if len(text)>300 else 'THIN_TEXT_REVIEW')
            if any(s in text[:1500].lower() for s in ['verify you are human','just a moment','access denied','enable javascript and cookies']):
                row['status']='BOT_CHALLENGE_NOT_EVIDENCE'
    except Exception as e:
        row.update(status='FETCH_FAILED',error=str(e)[:200])
    meta_path.write_text(json.dumps(row,ensure_ascii=False,indent=2))
    return row

def main():
    if '--expand' in sys.argv:
        existing=json.loads((OUT/'collection.json').read_text())
        class Links(HTMLParser):
            def __init__(self):super().__init__();self.links=[]
            def handle_starttag(self,tag,attrs):
                if tag=='a':
                    href=dict(attrs).get('href','')
                    if href:self.links.append(href)
        tasks=[];known={r['requested_url'] for r in existing}
        for row in existing:
            if row['status']!='FETCHED_TEXT_NOT_FACT_VERIFIED':continue
            key=hashlib.sha256(row['requested_url'].encode()).hexdigest()[:16]
            hp=RAW/(key+'.html')
            if not hp.exists():continue
            parser=Links();parser.feed(hp.read_text())
            base=row.get('source_url',row['requested_url']);host=urllib.parse.urlparse(base).netloc
            selected=[]
            for kind in ['about|our-company|who-we-are','product|solution','service|business|segment']:
                for link in parser.links:
                    u=urllib.parse.urljoin(base,link).split('#')[0]
                    path=urllib.parse.urlparse(u).path.lower()
                    if urllib.parse.urlparse(u).netloc!=host or u in known or u in selected:continue
                    if not re.search(kind,path) or re.search('blog|news|career|investor|privacy|login|\.pdf|contact',path):continue
                    selected.append(u);break
            for u in selected:
                known.add(u);tasks.append((row['company_id'],row['company_name'],row['role'],u))
        with cf.ThreadPoolExecutor(max_workers=6) as ex:
            for i,r in enumerate(ex.map(collect,tasks),1):
                existing.append(r)
                if i%100==0:print('Business subpages',i,'/',len(tasks),flush=True)
        (OUT/'collection.json').write_text(json.dumps(existing,ensure_ascii=False,indent=2))
        print('Added',len(tasks),'business subpages',flush=True)
        return
    tasks=[]
    for t in TARGETS:
        u=t.get('website') or ''
        if u: tasks.append((t['company_id'],t['company_name'],'TARGET','https://'+u.removeprefix('https://').removeprefix('http://')))
    seeds=[('MCD','McDonald\'s','https://corporate.mcdonalds.com/'),('QSR','Restaurant Brands International','https://www.rbi.com/about-us/overview/default.aspx'),('YUM','Yum! Brands','https://www.yum.com/'),('DPZ','Domino\'s Pizza','https://biz.dominos.com/about-us/franchising/'),('PZZA','Papa Johns','https://ir.papajohns.com/'),('ARCO','Arcos Dorados','https://ir.arcosdorados.com/company-overview/'),('PAYX','Paychex','https://www.paychex.com/business-solutions/midsize-business-solutions'),('WDAY','Workday','https://www.workday.com/en-us/products/human-capital-management.html'),('TNET','TriNet','https://www.trinet.com/hr-plus'),('NSP','Insperity','https://www.insperity.com/our-products/hr360/'),('INTU','Intuit','https://quickbooks.intuit.com/payroll/'),('SAP','SAP','https://www.sap.com/products/hcm.html'),('ORCL','Oracle','https://www.oracle.com/human-capital-management/')]
    tasks += [(i,n,'GLOBAL_CANDIDATE_SEED',u) for i,n,u in seeds]
    result=[]
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for i,r in enumerate(ex.map(collect,tasks),1):
            result.append(r)
            if i%40==0: print('Collected',i,'of',len(tasks),flush=True)
    (OUT/'collection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print('Finished',len(result),'sources;',sum(r['status']=='FETCHED_TEXT_NOT_FACT_VERIFIED' for r in result),'readable pages',flush=True)

if __name__=='__main__': main()
