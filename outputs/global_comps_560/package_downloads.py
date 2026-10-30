"""Data collection deliverable only: no split, comp selection, or scoring."""
import csv,json,pathlib,datetime,collections,zipfile
ROOT=pathlib.Path(__file__).resolve().parent;E=ROOT/'web_evidence';O=ROOT/'download_delivery';O.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text())
targets=read(ROOT/'prepared/Targets_560.json');names={t['company_id']:t['company_name'] for t in targets}
inventory=[]
cols=['company_id','company_name','source_type','section','source_text','source_link','source_date','status','source_location','raw_text_file']
f=(O/'Evidence_FULL.csv').open('w');writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader();total=0
def add(cid,name,typ,section,text,url,date='UNKNOWN',status='DOWNLOADED_NOT_FACT_VERIFIED',location='',raw=''):
    global total
    text=str(text)
    base=dict(company_id=cid,company_name=name,source_type=typ,section=section,source_text='',source_link=url,source_date=date,status=status,source_location=location,raw_text_file=raw)
    for start in range(0,max(1,len(text)),10000):
        row=dict(base,source_text=text[start:start+10000],source_location=location+f'; text characters {start+1}–{min(start+10000,len(text))}')
        writer.writerow(row);total+=1
    if typ!='WRDS_API_GLOBAL_CATALOG':
        inventory.append(dict(base,source_text=text[:1200]+(' [Full text continues in Evidence_FULL.csv / raw file]' if len(text)>1200 else '')))

web=read(E/'collection.json');sec=read(E/'sec_index.json')
for r in web:
    txt=pathlib.Path(r['text_file']).read_text() if r.get('text_file') else r.get('error',r['status'])
    rel='texts/web/'+pathlib.Path(r['text_file']).name if r.get('text_file') else ''
    add(r['company_id'],r['company_name'],'COMPANY_WEBSITE','Full extracted page text',txt,r.get('source_url',r['requested_url']),status=r['status'],raw=rel)
for r in sec:
    add(r['company_id'],r['company_name'],'SEC_FILING_INDEX','Annual filing identity/index',json.dumps(r,ensure_ascii=False),r.get('annual_filing_url',r.get('source_url','')),r.get('filing_date','UNKNOWN'),r['status'])
    if r.get('text_file'):
        p=pathlib.Path(r['text_file'])
        add(r['company_id'],r['company_name'],'SEC_ANNUAL_REPORT',r['form']+' full extracted text',p.read_text(),r['annual_filing_url'],r['filing_date'],raw='texts/sec/'+p.name)
catalog=read(E/'wrds_api/company_catalog_all.json')
for r in catalog:
    add('GVKEY'+r['gvkey'],r.get('conml') or r.get('conm',''),'WRDS_API_GLOBAL_CATALOG','Business description and company record',json.dumps(r,ensure_ascii=False),r['_source_url'],status='API_RECORD_CURRENT_LISTING_NOT_VERIFIED',location='gvkey='+r['gvkey'])
for file,typ in [('Targets_560','SUPPLIED_CAPIQ_EXCEL'),('WRDS_Matched_Latest','SUPPLIED_WRDS_FIRM_RATIOS'),('FF49_Benchmarks_560','SUPPLIED_WRDS_FF49_MEDIANS')]:
    for r in read(ROOT/'prepared'/f'{file}.json'):
        add(r['company_id'],names.get(r['company_id'],''),typ,'Complete prepared source record',json.dumps(r,ensure_ascii=False),r.get('source_url','https://drive.google.com/file/d/14NvyjcLDPbrm4fGh03xJpMrAJ9Q-VeqB/view'),r.get('benchmark_date',r.get('Date','UNKNOWN')),location=r.get('source_location',r.get('source_sheet','Prepared source record')))
fund_status=[];variables=[]
for table in ['comp_funda','comp_fundq','comp_g_funda','comp_g_fundq']:
    path=E/'wrds_api'/table/'records_2010_onward.json'
    if not path.exists():continue
    records=read(path);keys=sorted(set().union(*(r.keys() for r in records))) if records else []
    url='https://wrds-api.wharton.upenn.edu/data/'+table.replace('_','/',1)+'/'
    with (O/(table+'_2010_onward.csv')).open('w') as out:
        w=csv.DictWriter(out,fieldnames=keys+['source_link']);w.writeheader()
        for r in records:w.writerow(dict(r,source_link=url))
    fund_status.append(dict(table=table,rows=len(records),fields=len(keys),source_url=url))
    for key in keys:variables.append(dict(table=table,variable=key,description='Native database field; definition not yet downloaded',data_type='Observed '+','.join(sorted({type(r.get(key)).__name__ for r in records[:100] if r.get(key) is not None})),source_link=url))
    for r in records:
        # All original variables remain in separate wide CSV and raw API responses.
        keep={k:r.get(k) for k in ('gvkey','conm','tic','datadate','fyear','fyearq','fqtr','curcd','curcdq','sale','saleq','revt','revtq','ebitda','oibdp','oibdpq','ebit','at','atq','lt','ltq','dltt','dlttq','dlc','dlcq','che','cheq','csho','cshoq','ni','niq','oancf','oancfy','capx','capxy','indfmt','datafmt','consol','popsrc') if k in r}
        add('GVKEY'+str(r.get('gvkey')),r.get('conm',''),'WRDS_API_FUNDAMENTALS',table+' selected figures (all fields in wide CSV)',json.dumps(keep),url,str(r.get('datadate','UNKNOWN')),location='Native Compustat values; currency field retained; units dictionary pending')
f.close()
stats=[dict(Item='Scope',Value='DOWNLOADS ONLY',Detail='No sample split, comp selection, similarity scoring or model evaluation in this delivery.'),
dict(Item='Target companies',Value=560,Detail='Original target IDs preserved.'),
dict(Item='Website page attempts',Value=len(web),Detail='Homepages plus company-owned business/product/service subpages.'),
dict(Item='Readable website pages',Value=sum(r['status']=='FETCHED_TEXT_NOT_FACT_VERIFIED' for r in web),Detail='Extracted text, not independently fact-checked. Failures retained.'),
dict(Item='Annual-report texts',Value=sum(bool(r.get('text_file')) for r in sec),Detail='May contain duplicate entities. Filing index and date retained.'),
dict(Item='WRDS company records',Value=len(catalog),Detail='North America + Global; includes inactive and overlapping entities, not a verified listed-company count.'),
dict(Item='Unified full evidence rows',Value=total,Detail='Evidence_FULL.csv includes full 10000-character chunks. Workbook contains source excerpts and paths.'),
dict(Item='WRDS fundamentals',Value=sum(x['rows'] for x in fund_status),Detail='All available downloaded annual/quarterly fields retained in wide CSV; periods from 2010 onward.'),
dict(Item='Use in later modeling',Value='Target information restriction remains',Detail='Collection includes full public information. Later selection inputs must be restricted to target website and original three permitted figures.'),
dict(Item='Source dates and units',Value='Preserved, not harmonized',Detail='Latest is not a common date. Current websites are not historical snapshots. Undocumented units remain unverified.')]
(O/'Status.json').write_text(json.dumps(stats));(O/'Evidence_Index.json').write_text(json.dumps(inventory));(O/'Variables.json').write_text(json.dumps(variables))
meta=ROOT.parent/'wrds_ratios_20261020/variable_metadata.tsv'
if meta.exists():
    for line in meta.read_text().splitlines():
        parts=line.split('\t')
        if len(parts)>=3:variables.append(dict(table='SUPPLIED_WRDS_RATIOS',variable=parts[0],data_type=parts[1],description=parts[2],source_link='https://wrds-www.wharton.upenn.edu/pages/get-data/financial-ratios-suite-wrds/financial-ratios/financial-ratios-firm-level-by-wrds-beta/'))
    (O/'Variables.json').write_text(json.dumps(variables))
(O/'fundamentals_status.json').write_text(json.dumps(fund_status,indent=2))
readme='''# Public-company data downloads

This is a data collection package. No sample split, comp selection, similarity scores or out-of-sample results are included.

Evidence_FULL.csv combines original workbook records, website text, SEC annual-report text, WRDS company descriptions and selected fundamental figures. Each source-text column is immediately followed by its source URL. Long text is split into numbered character ranges. Raw extracted website and SEC text files are included under texts/. Full native fundamental variables are in separate wide CSV files, each with source_link. The original three source files remain unchanged in the workspace and are not duplicated in this package.

The Excel index shows the first 1200 characters per source record plus its full-text path. It is an index, not the complete raw corpus. Open Evidence_FULL.csv or the text files for longer passages and all numerical context.

WRDS includes active and inactive companies and overlapping Global/North America records. Company active status is not proof of a current listing. Target-reference matching ambiguity is retained. API figures have not been standardized to an as-of date, currency, unit scale or accounting basis. Variable names are retained; descriptions not obtained from a dictionary are explicitly marked pending.

For later pseudo-private modeling, hide target public-only financials, SEC descriptions and database classifications. Use only company-owned business website information and the original permitted Revenue, EBITDA and Debt. This collection does not itself enforce a future model's information boundary.

Previously generated sample splits and lexical candidate rankings were moved out of this delivery to deferred_model_work/ after the scope correction. They are not outputs of this download package.
'''
(O/'README.md').write_text(readme)
print('Prepared full evidence CSV',total,'rows; Excel source index',len(inventory),'records; fundamental tables',fund_status,flush=True)
