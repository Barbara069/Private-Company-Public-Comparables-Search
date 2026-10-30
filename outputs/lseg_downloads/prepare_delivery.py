import json,pathlib,datetime,csv,re,shutil,collections
import pandas as pd
P=pathlib.Path(__file__).resolve().parent;D=P/'delivery';D.mkdir(exist_ok=True)
BASE=P.parent/'global_comps_560'
SOURCE='https://www.lseg.com/en/data-catalogue/company-data/company-fundamentals/business-geographic-segment-and-major-customers'
mapping=json.loads((P/'target_mapping_560.json').read_text());byric={m['ric']:m for m in mapping}
original={r['company_id']:r for r in json.loads((BASE/'prepared/Targets_560.json').read_text())}
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(name):
    d=pd.read_csv(P/(name+'.csv'),keep_default_na=False)
    for c in d:
        if c.endswith(('.DATE','.CALCDATE')) or c=='TR.COMPANYINCORPDATE':
            d[c]=d[c].apply(lambda x:str(x)[:10] if x not in ('',None) else '')
    return d.drop_duplicates()
def clean(v):
    if v is None:return None
    if isinstance(v,float) and pd.isna(v):return None
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','',v) if isinstance(v,str) else v
def records(d):return [{k:clean(v) for k,v in r.items()} for r in d.to_dict('records')]
def export(name,rows):
    rows=[{k:clean(v) for k,v in r.items()} for r in rows]
    (D/(name+'.json')).write_text(json.dumps(rows,ensure_ascii=False))
    if rows:
        with (D/(name+'.csv')).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def meaningful(x):return x not in ('',None) and not (isinstance(x,float) and pd.isna(x))
datasets={}
for key in ['company_profiles_raw','annual_five_years','latest_quarter','ltm','market','business_segments','geographic_segments']:
    d=read(key);d=d[d.Instrument.isin(byric)]
    if key=='annual_five_years':
        cols=['Instrument','TR.TOTALREVENUE.DATE','TR.TOTALREVENUE.FPERIOD']
        # Coalesce equivalent repeated requests; retain raw responses in the package.
        d=d.groupby(cols,dropna=False,sort=False).agg(lambda s:next((x for x in s if meaningful(x)),'')).reset_index()
        d=d.sort_values('TR.TOTALREVENUE.DATE',ascending=False).groupby('Instrument',sort=False).head(5)
    if key in ['company_profiles_raw','ltm','market']:
        d=d.groupby('Instrument',sort=False).agg(lambda s:next((x for x in s if meaningful(x)),'')).reset_index()
    d.insert(0,'Company ID',d.Instrument.map(lambda r:byric[r]['company_id']))
    d.insert(1,'Original Company Name',d.Instrument.map(lambda r:byric[r]['target_name']))
    d['Source']='LSEG Workspace Data Library';d['Source Link']=SOURCE;d['Retrieved At UTC']=stamp
    if key.endswith('segments'):
        nc=next(c for c in d if c.endswith('.SEGMENTNAME'))
        d['Total or Elimination Row']=d[nc].astype(str).str.contains('segment total|consolidated|elimination|unallocated',case=False,regex=True)
    rows=records(d);datasets[key]=rows;export(key,rows)
profiles={r['Instrument']:r for r in datasets['company_profiles_raw']}
companies=[];coverage=[];evidence=[]
for m in mapping:
    r=profiles.get(m['ric'],{});o=original[m['company_id']]
    company={'Company ID':m['company_id'],'Original Company Name':m['target_name'],'Original Ticker':m['input_ticker'],'LSEG Instrument':m['ric'],
             'LSEG Company Name':r.get('TR.COMMONNAME'),'Identity Status':m['mapping_status'],
             'Original Website':o['website'],'LSEG Headquarters Country':r.get('TR.HEADQUARTERSCOUNTRY'),
             'LSEG Business Sector':r.get('TR.TRBCBUSINESSSECTOR'),'LSEG Industry Group':r.get('TR.TRBCINDUSTRYGROUP'),'LSEG Industry':r.get('TR.TRBCINDUSTRY'),
             'LSEG Employees':r.get('TR.NUMBEROFEMPLOYEES'),'LSEG Employees Date':r.get('TR.NUMBEROFEMPLOYEES.DATE'),
             'Original CapIQ Employees':o.get('employees'),'Original CapIQ Employees Date':'Not specified in supplied field',
             'LSEG Incorporation Date':r.get('TR.COMPANYINCORPDATE'),'Original CapIQ Founded Year':o.get('founded'),
             'Original SIC4':o.get('sic4'),'Original FF49':o.get('ff49'),
             'LSEG ISIN':r.get('TR.ISIN'),'LSEG CUSIP':r.get('TR.CUSIP'),
             'LSEG Business Summary':r.get('TR.BUSINESSSUMMARY'),'LSEG Source Link':SOURCE,'Original Source Link':o['source_url']}
    companies.append(company)
    stat={'Company ID':m['company_id'],'Company Name':m['target_name'],'Instrument':m['ric'],'Identity Status':m['mapping_status']}
    for key in ['annual_five_years','latest_quarter','ltm','market','business_segments','geographic_segments']:
        rs=[x for x in datasets[key] if x['Company ID']==m['company_id']]
        valuecol='TR.COMPANYMARKETCAP' if key=='market' else ('TR.BGS.BUSTOTALREVENUE' if key=='business_segments' else ('TR.BGS.GEOTOTALREVENUE' if key=='geographic_segments' else 'TR.TOTALREVENUE'))
        stat[key+' nonmissing observations']=sum(meaningful(x.get(valuecol)) for x in rs)
        if key in ('annual_five_years','latest_quarter','ltm'):
            stat[key+' latest period end']=max((str(x.get('TR.TOTALREVENUE.DATE','')) for x in rs if meaningful(x.get(valuecol))),default='')
    stat['Business Summary Present']=meaningful(r.get('TR.BUSINESSSUMMARY'));stat['Employees Present']=meaningful(r.get('TR.NUMBEROFEMPLOYEES'))
    coverage.append(stat)
    evidence.append({'Company ID':m['company_id'],'Company Name':m['target_name'],'Source Type':'LSEG_API','Section':'Business summary','Source Text':r.get('TR.BUSINESSSUMMARY',''),'Source Link':SOURCE,'Source Location':m['ric']+' / TR.BusinessSummary','Source Date':stamp,'Raw Text File':''})
    evidence.append({'Company ID':m['company_id'],'Company Name':m['target_name'],'Source Type':'SUPPLIED_CAPIQ','Section':'Original company profile','Source Text':str(o.get('business_description',o.get('description',''))),'Source Link':o['source_url'],'Source Location':o['source_location'],'Source Date':'Source as-of date unspecified','Raw Text File':''})
for r in json.loads((BASE/'web_evidence/collection.json').read_text()):
    if r['company_id'] not in original:continue
    text=pathlib.Path(r['text_file']).read_text() if r.get('text_file') else r.get('error',r['status'])
    evidence.append({'Company ID':r['company_id'],'Company Name':r['company_name'],'Source Type':'COMPANY_WEBSITE','Section':r['status'],'Source Text':text[:1500]+(' [Full text in accompanying file]' if len(text)>1500 else ''),'Source Link':r.get('source_url',r['requested_url']),'Source Location':'Extracted webpage text, not independently fact-checked','Source Date':r.get('retrieved_at',''),'Raw Text File':'texts/web/'+pathlib.Path(r['text_file']).name if r.get('text_file') else ''})
for r in json.loads((BASE/'web_evidence/sec_index.json').read_text()):
    if r['company_id'] not in original:continue
    text=pathlib.Path(r['text_file']).read_text() if r.get('text_file') else r['status']
    evidence.append({'Company ID':r['company_id'],'Company Name':r['company_name'],'Source Type':'SEC_ANNUAL_REPORT','Section':r.get('form',r['status']),'Source Text':text[:1500]+(' [Full text in accompanying file]' if len(text)>1500 else ''),'Source Link':r.get('annual_filing_url',r.get('source_url','')),'Source Location':'Ticker/CIK filing lookup; entity identity still requires review','Source Date':r.get('filing_date',''),'Raw Text File':'texts/sec/'+pathlib.Path(r['text_file']).name if r.get('text_file') else ''})
export('Companies_560',companies);export('Coverage_560',coverage);export('Evidence',evidence)
labels={'TR.TOTALREVENUE':'Total revenue','TR.EBITDA':'EBITDA','TR.EBIT':'EBIT','TR.GROSSPROFIT':'Gross profit','TR.OPERATINGINCOME':'Operating income','TR.NETINCOME':'Net income','TR.TOTALASSETS':'Total assets','TR.TOTALASSETSREPORTED':'Total assets reported','TR.TOTALLIABILITIES':'Total liabilities','TR.TOTALEQUITY':'Total equity','TR.TOTALDEBT':'Total debt','TR.NETDEBT':'Net debt','TR.CASHANDSTINVESTMENTS':'Cash and short-term investments','TR.CASHFROMOPERATINGACTIVITIES':'Operating cash flow','TR.CAPITALEXPENDITURES':'Capital expenditures, provider field','TR.CAPEXCFSTMT':'Cash-flow statement capex, provider field','TR.RESEARCHANDDEVELOPMENT':'Research and development','TR.DEPRECIATION':'Depreciation','TR.INTERESTEXPENSE':'Interest expense','TR.EFFECTIVETAXRATE':'Effective tax rate','TR.NUMBEROFEMPLOYEES':'Employee count','TR.TOTALCURRENTASSETS':'Current assets','TR.TOTALCURRENTLIABILITIES':'Current liabilities','TR.FREECASHFLOW':'Provider free cash flow','TR.COMPANYMARKETCAP':'Company market capitalization','TR.EV':'Enterprise value','TR.EVTOEBITDA':'Provider EV/EBITDA','TR.PRICECLOSE':'Closing share price','TR.SHARESOUTSTANDING':'Shares outstanding'}
guide=[]
allkeys=sorted({k for rs in datasets.values() for r in rs for k in r if k.startswith('TR.')})
for field in allkeys:
    unit='Text / identifier';note='Provider value retained. Missing remains missing.'
    if field in labels:
        unit='Count' if field in ('TR.NUMBEROFEMPLOYEES','TR.SHARESOUTSTANDING') else ('Percentage points' if field=='TR.EFFECTIVETAXRATE' else ('Multiple (x)' if field=='TR.EVTOEBITDA' else 'USD, base units (requested Curn=USD, Scale=0)'))
    if field.endswith(('.DATE','.CALCDATE')):unit='Date'
    if field.endswith('CALCDATE'):note='LSEG calculation date. Not a filing/publication date.'
    if field in ('TR.CAPITALEXPENDITURES','TR.CAPEXCFSTMT'):note='Different native fields may have different signs/scope. Do not substitute or reconcile without checking definitions.'
    if field=='TR.FREECASHFLOW':note='LSEG supplied field. Not recomputed as operating cash flow minus either capex field.'
    guide.append({'Variable Name':field,'Description':labels.get(field,field.removeprefix('TR.')),'Unit / Data Type':unit,'Notes':note,'Source Link':SOURCE})
export('Field_Guide',guide)
summary={'targets':560,'profile_rows':len(companies),'business_summaries':sum(x['Business Summary Present'] for x in coverage),'employees_available':sum(x['Employees Present'] for x in coverage),
         'annual_companies_with_revenue':sum(x['annual_five_years nonmissing observations']>0 for x in coverage),'annual_companies_with_five_revenue_years':sum(x['annual_five_years nonmissing observations']>=5 for x in coverage),
         'latest_quarter_companies_with_revenue':sum(x['latest_quarter nonmissing observations']>0 for x in coverage),'ltm_companies_with_revenue':sum(x['ltm nonmissing observations']>0 for x in coverage),
         'market_caps_available':sum(x['market nonmissing observations']>0 for x in coverage),'business_segment_companies':sum(x['business_segments nonmissing observations']>0 for x in coverage),
         'geographic_segment_companies':sum(x['geographic_segments nonmissing observations']>0 for x in coverage),'identity_review_companies':sum('REQUIRED' in x['Identity Status'] for x in coverage),
         'annual_rows':len(datasets['annual_five_years']),'source_evidence_records':len(evidence),'retrieved_at_utc':stamp}
(D/'download_summary.json').write_text(json.dumps(summary,indent=2))
readme='''# Original 560 company data collection

Scope: data collection only, restricted to the original 560 targets. No external comp selection, similarity scores, sample split or out-of-sample evaluation.

Financials: latest five available fiscal annual observations, latest published fiscal quarter, and LTM. Quarter queries explicitly use FQ0; when its revenue is missing, the most recent nonmissing observation among FQ-1 through FQ-4 is retained and labeled in Quarter Selection. Annual observations are per-company fiscal years, not calendar-year-aligned. Companies with limited history keep their available periods. USD/base units were requested for monetary financial and market data. Ratios, percentage points, employee counts and share counts keep their own units. Native signs are retained. No calculated figures were substituted for absent source values.

Company profiles and quantity data: business summary, country, TRBC classification, incorporation date, employee count and its date, ISIN/CUSIP, current share count, business segment and geographic segment revenue. Latest available segments only. Total/elimination rows are retained and flagged; do not sum them with underlying segments. Incorporation date is not founding date.

Source attribution: LSEG field names and instruments are retained in every table. Evidence contains company website and SEC excerpts with the source URL immediately to the right, plus full-text relative paths. Full website/SEC extracted text is included in the ZIP. These texts have not all been independently fact-checked. The supplied CapIQ, WRDS and FF49 records remain separate source data.

Identity: the 560-row coverage and company tables preserve all original IDs, including name/class/primary-instrument corrections. Rows marked NAME_OR_LEGAL_ENTITY_CHANGE_REVIEW_REQUIRED need manual confirmation before valuation. Do not treat active status, a primary quote or a successful download as proof of current public listing. Delisted identifiers retain their historical data and dates.

Timing: Retrieved At UTC is extraction time. TR.TotalRevenue.DATE is the financial period end. CALCDATE is the provider calculation date, not a publication date. This is a current research snapshot, not a point-in-time backtest dataset. Reports and current website text may have different dates.

Quality: missing values remain blank, not zero. Latest-quarter absence is common for firms that do not report quarterly. Different EBITDA/capex/free-cash-flow fields can have different definitions. The field guide gives labels and units, not complete provider accounting definitions. No final ratio harmonization or valuation model has been performed.

For later pseudo-private matching, allow only the target's company-owned business website and the original permitted Revenue, EBITDA and Debt. Hide its database/SEC-only information, true multiple and public identifiers from selection. The complete collection remains available on the public-comp side.
'''
(D/'README.md').write_text(readme)
for name in ['Targets_560','WRDS_Matched_Latest','FF49_Benchmarks_560']:
    shutil.copy2(BASE/'prepared'/(name+'.csv'),D/('Provided_'+name+'.csv'))
print(json.dumps(summary,indent=2))
