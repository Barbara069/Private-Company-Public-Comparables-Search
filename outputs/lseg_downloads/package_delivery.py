import json,pathlib,zipfile,csv
P=pathlib.Path(__file__).resolve().parent;D=P/'delivery';BASE=P.parent/'global_comps_560/web_evidence'
manifest=[]
with zipfile.ZipFile(P/'560_Company_Data_Package.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in sorted(D.iterdir()):
        if p.is_file() and (p.suffix in ('.csv','.json','.md','.xlsx')):
            z.write(p,'data/'+p.name);manifest.append(dict(path='data/'+p.name,bytes=p.stat().st_size))
    for f in ['target_mapping_560.json','primary_identifier_corrections.json','identity_exception_searches.json']:
        p=P/f;z.write(p,'audit/'+p.name)
    for f in ['request_log.json','completion_request_log.json']:
        p=P/'raw_560'/f
        if p.exists():z.write(p,'audit/'+f)
    rows=json.loads((D/'Evidence.json').read_text());paths={r['Raw Text File'] for r in rows if r.get('Raw Text File')}
    for relative in sorted(paths):
        kind=relative.split('/')[1];name=relative.split('/')[-1]
        source=BASE/('raw' if kind=='web' else 'sec')/name
        assert source.exists(),source
        z.write(source,relative);manifest.append(dict(path=relative,bytes=source.stat().st_size))
    z.writestr('file_manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(P/'560_Company_Data_Package.zip') as z:
    assert z.testzip() is None
    assert 'data/560_Company_Data.xlsx' in z.namelist()
    print('Verified package:',len(z.namelist()),'files;',round((P/'560_Company_Data_Package.zip').stat().st_size/1e6,1),'MB')
