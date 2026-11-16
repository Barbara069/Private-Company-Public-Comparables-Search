"""Publish the filtered delivery and retire superseded mixed-origin downloads.
Runs inside the repository-owned cleanup workflow with its temporary token.
"""
from pathlib import Path
import hashlib,json,os,time,urllib.request,urllib.error
from exclude_restricted_sources import ROOT,STATS,export_csv
REPO=os.environ['GITHUB_REPOSITORY'];TOKEN=os.environ['GH_TOKEN']
API='https://api.github.com/repos/'+REPO
TMP=Path(os.environ.get('RUNNER_TEMP','/tmp'))/'source-clean-delivery';TMP.mkdir(exist_ok=True)
def api(path,method='GET',body=None):
    req=urllib.request.Request(API+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers={'Authorization':'Bearer '+TOKEN,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=120) as r:
        data=r.read();return json.loads(data) if data else None

def prepare():
    releases=api('/releases');old=[];originals={};old_csv=None
    for release in releases:
        if release['tag_name']=='v2026.11.15-permitted-comparables':continue
        old.append({'id':release['id'],'tag':release['tag_name']})
        for asset in release['assets']:
            name=asset['name']
            if name not in ['Company_List_for_Interns.xlsx','CapitalIQ_560.xlsx','Research_Data.csv.gz']:continue
            dest=TMP/('old_'+name)
            if not dest.exists():
                with urllib.request.urlopen(asset['browser_download_url'],timeout=180) as r,dest.open('wb') as w:
                    import shutil;shutil.copyfileobj(r,w)
            if name=='Research_Data.csv.gz':old_csv=dest
            else:originals[name]=str(dest)
    assert 'Company_List_for_Interns.xlsx' in originals and 'CapitalIQ_560.xlsx' in originals,'Permitted originals must be preserved before retiring old releases'
    output=TMP/'Research_Data.csv.gz';counts=export_csv(output,old_csv)
    payload={'old_releases':old,'originals':originals,'csv':str(output),'counts':counts}
    (TMP/'prepared.json').write_text(json.dumps(payload))
    audit={'policy_version':'2026-11-15','excluded_source_family':'WRDS-delivered content and dependent results','candidate_scores':'RECOMPUTED_PERMITTED_SOURCE_PROVISIONAL_INDICES','forecast_status':'PLAN_ONLY_NOT_EXECUTED','records_by_dataset':counts,'csv_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'compressed_bytes':output.stat().st_size,'target_input_count':560,'validation':'ALL_COMPRESSED_PUBLICATION_PAYLOADS_AND_EXPORTED_CSV_READ_BACK','history':'CLEAN_HISTORY_RETAINED; PERMITTED_SOURCE_RESULTS_ADDED'}
    (ROOT/'code/Source_Policy_Audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print('Prepared source-filtered release:',sum(counts.values()),'rows;',output.stat().st_size,'bytes')

def publish():
    p=json.loads((TMP/'prepared.json').read_text());sha=os.environ['CLEAN_COMMIT_SHA'];tag='v2026.11.15-permitted-comparables'
    existing=next((r for r in api('/releases') if r['tag_name']==tag),None)
    body='Source-filtered research delivery, 15 November 2026. Restricted academic-database observations and their old dependent scores are excluded. New permitted-source provisional comparable indices, per-facet evidence and weights are included. Preserve the two permitted original workbooks beside the notebook. Company forecasts are planned, not executed. See code/Source_Policy_Audit.json and code/04_Revenue_Growth_Methodology.md.'
    release=existing or api('/releases','POST',{'tag_name':tag,'target_commitish':sha,'name':'Permitted-source company research — 15 November 2026','body':body,'draft':False,'prerelease':False})
    upload=release['upload_url'].split('{')[0]
    assets=[('Research_Data.csv.gz',Path(p['csv']))]+[(name,Path(path)) for name,path in p['originals'].items()]
    for name,path in assets:
        old=next((a for a in api('/releases/'+str(release['id'])+'/assets') if a['name']==name),None)
        if old:
            assert old['size']==path.stat().st_size,'Existing asset differs: do not silently replace';continue
        import urllib.parse
        req=urllib.request.Request(upload+'?name='+urllib.parse.quote(name),data=path.read_bytes(),method='POST',headers={'Authorization':'Bearer '+TOKEN,'Content-Type':'application/octet-stream','Accept':'application/vnd.github+json'})
        with urllib.request.urlopen(req,timeout=600) as r:a=json.load(r)
        assert a['size']==path.stat().st_size and a['state']=='uploaded'
        print('Uploaded',name,a['size'])
    # Retire old releases only after every permitted replacement is uploaded.
    for old in p['old_releases']:
        api('/releases/'+str(old['id']),'DELETE')
        try:api('/git/refs/tags/'+old['tag'],'DELETE')
        except urllib.error.HTTPError as e:
            if e.code!=404:raise
    remaining=api('/releases');assert len(remaining)==1 and remaining[0]['tag_name']==tag
    print('Release cleanup verified: one clean release, three assets.')

if __name__=='__main__':
    import sys
    prepare() if sys.argv[1]=='prepare' else publish()
