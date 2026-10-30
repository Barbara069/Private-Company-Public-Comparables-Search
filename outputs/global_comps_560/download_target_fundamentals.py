"""Download reference fundamentals, no sampling, modeling, or scoring."""
import json,pathlib,urllib.request,urllib.parse,getpass,concurrent.futures as cf,time,collections,re
ROOT=pathlib.Path(__file__).resolve().parent;OUT=ROOT/'web_evidence/wrds_api'
def dom(u):
    if not u:return ''
    return urllib.parse.urlparse(u if '://' in u else 'https://'+u).netloc.lower().removeprefix('www.')
def norm(n):return re.sub(r'[^a-z0-9]','',re.sub(r'\b(incorporated|inc|corp|corporation|holdings|holding|limited|ltd|plc|company|co)\b','',n.lower()))
def main():
    catalog=json.loads((OUT/'company_catalog_all.json').read_text())
    targets=json.loads((ROOT/'prepared/Targets_560.json').read_text())
    bydom=collections.defaultdict(list);byname=collections.defaultdict(list)
    for r in catalog:
        if dom(r.get('weburl')):bydom[dom(r['weburl'])].append(r)
        byname[norm(r.get('conml') or r.get('conm',''))].append(r)
    matches=[];keys=set()
    for t in targets:
        found=bydom.get(dom(t['website']),[]) or byname.get(norm(t['company_name']),[])
        unique={r['gvkey']:r for r in found}
        status='UNIQUE_WEBSITE_OR_NAME_MATCH_REVIEW_REQUIRED' if len(unique)==1 else ('AMBIGUOUS_MATCH' if unique else 'NO_MATCH')
        matches.append(dict(company_id=t['company_id'],company_name=t['company_name'],status=status,gvkeys=list(unique)))
        # Download every candidate mapping; do not silently merge ambiguous entities.
        keys.update(unique)
    (OUT/'target_reference_matches.json').write_text(json.dumps(matches,indent=2))
    token=getpass.getpass('WRDS token: ')
    def fetch(url,path):
        if path.exists():return json.loads(path.read_text())
        assert url.startswith('https://wrds-api.wharton.upenn.edu/data/')
        for attempt in range(3):
            try:
                req=urllib.request.Request(url,headers={'Authorization':'Token '+token,'Accept':'application/json'})
                with urllib.request.urlopen(req,timeout=100) as r:d=json.load(r)
                path.write_text(json.dumps(d));return d
            except Exception:
                if attempt==2:raise
                time.sleep(3)
    keylist=sorted(keys);batches=[keylist[i:i+35] for i in range(0,len(keylist),35)]
    logs=[]
    for table in ['comp/funda','comp/g_funda','comp/fundq','comp/g_fundq']:
        folder=OUT/table.replace('/','_');folder.mkdir(exist_ok=True)
        if (folder/'records_2010_onward.json').exists():
            existing=json.loads((folder/'records_2010_onward.json').read_text())
            logs.append(dict(table=table,status='DOWNLOADED',rows=len(existing),source_url='https://wrds-api.wharton.upenn.edu/data/'+table+'/'));continue
        def work(pair):
            idx,ks=pair
            params={'gvkey__in':','.join(ks),'limit':5000,'fyear__gte':2010}
            if table.endswith('fundq'):
                annual_table='comp_g_funda' if table=='comp/g_fundq' else 'comp_funda'
                annual=json.loads((OUT/annual_table/'records_2010_onward.json').read_text())
                field='isin' if table=='comp/g_fundq' else 'cusip'
                ids=sorted({r[field] for r in annual if r.get('gvkey') in ks and r.get(field)})
                if not ids:return []
                params={field+'__in':','.join(ids),'limit':5000,'datadate__gte':'2010-01-01'}
            query=urllib.parse.urlencode(params)
            url='https://wrds-api.wharton.upenn.edu/data/'+table+'/?'+query
            data=fetch(url,folder/f'scoped_batch_{idx}_0.json');records=list(data.get('results',[]));page=0
            assert all(r.get('gvkey') in ks for r in records),'WRDS gvkey filter was not applied'
            while data.get('next'):
                page+=1;url=data['next'].replace('http://','https://',1)
                data=fetch(url,folder/f'scoped_batch_{idx}_{page}.json');records.extend(data['results'])
                assert all(r.get('gvkey') in ks for r in data['results']),'WRDS gvkey filter was not applied'
            # Verify ignored filters cannot cause a database-wide accidental download.
            assert all(r.get('gvkey') in ks for r in records),'WRDS gvkey filter was not applied'
            return [r for r in records if str(r.get('datadate',''))>='2010-01-01']
        records=[]
        try:
            with cf.ThreadPoolExecutor(max_workers=2) as ex:
                for i,part in enumerate(ex.map(work,enumerate(batches)),1):
                    records.extend(part);print(table,'batch',i,'/',len(batches),'retained rows',len(records),flush=True)
            (folder/'records_2010_onward.json').write_text(json.dumps(records))
            logs.append(dict(table=table,status='DOWNLOADED',rows=len(records),source_url='https://wrds-api.wharton.upenn.edu/data/'+table+'/'))
        except Exception as e:logs.append(dict(table=table,status='FAILED_OR_SUBSCRIPTION_UNAVAILABLE',error=str(e)[:200]))
        (OUT/'fundamentals_download_status.json').write_text(json.dumps(logs,indent=2))
    print('Finished',len(matches),'target mapping records;',len(keys),'reference GVKEYs',flush=True)
if __name__=='__main__':main()
