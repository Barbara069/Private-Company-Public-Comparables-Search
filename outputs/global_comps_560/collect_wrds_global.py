"""WRDS reference catalog. Token is read from terminal, never stored."""
import json,pathlib,urllib.request,urllib.error,getpass,time,concurrent.futures as cf
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'web_evidence/wrds_api';OUT.mkdir(exist_ok=True)
BASE='https://wrds-api.wharton.upenn.edu'

def main():
    token=getpass.getpass('WRDS token: ')
    def fetch(url,path):
        if path.exists():return json.loads(path.read_text())
        assert url.startswith(BASE+'/data/')
        req=urllib.request.Request(url,headers={'Authorization':'Token '+token,'Accept':'application/json'})
        for trial in range(3):
            try:
                with urllib.request.urlopen(req,timeout=90) as r:d=json.load(r)
                path.write_text(json.dumps(d));return d
            except Exception:
                if trial==2:raise
                time.sleep(3*(trial+1))
    all_rows=[]
    for table in ['comp/company','comp/g_company']:
        page=5000
        first=fetch(f'{BASE}/data/{table}/?limit={page}',OUT/(table.replace('/','_')+'_0.json'))
        count=first['count'];actual=len(first['results'])
        if actual<page:page=actual
        pages=[(off,f'{BASE}/data/{table}/?limit={page}&offset={off}') for off in range(page,count,page)]
        records=list(first['results']);print(table,'total',count,'page size',page,flush=True)
        def work(pair):
            off,url=pair
            return fetch(url,OUT/(table.replace('/','_')+f'_{off}.json'))['results']
        with cf.ThreadPoolExecutor(max_workers=2) as ex:
            for i,data in enumerate(ex.map(work,pages),1):
                records.extend(data)
                print(table,'rows',len(records),flush=True)
        assert len(records)==count
        for r in records:
            r['_source_url']=f'{BASE}/data/{table}/'
            r['_access_role']='PUBLIC_CANDIDATE_REFERENCE_ONLY_NEVER_TARGET_PROFILE'
            r['_listing_status']='UNVERIFIED_ACTIVE_COMPANY_IS_NOT_PROOF_OF_CURRENT_LISTING'
        all_rows.extend(records)
    (OUT/'company_catalog_all.json').write_text(json.dumps(all_rows))
    active=[r for r in all_rows if r.get('costat')=='A']
    (OUT/'company_catalog_active_unverified.json').write_text(json.dumps(active))
    print('Finished',len(all_rows),'catalog records;',len(active),'active records before entity/listing verification',flush=True)
if __name__=='__main__':main()
