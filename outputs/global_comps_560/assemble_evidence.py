import csv,json,pathlib,collections,datetime
ROOT=pathlib.Path(__file__).resolve().parent
E=ROOT/'web_evidence';B=ROOT/'blinded'
read=lambda p:json.loads(p.read_text())
targets=read(B/'target_inputs.json');names={r['target_id']:r['company_name'] for r in targets}
split={r['target_id']:r['split'] for r in read(B/'split_manifest.json')}
rows=[]
def add(cid,name,typ,role,section,text,url,status='SOURCE_VALUE_NOT_INDEPENDENTLY_VERIFIED',source_date='UNKNOWN',location='',raw_file=''):
    text=str(text)
    for i in range(0,max(1,len(text)),3000):
        rows.append(dict(company_id=cid,company_name=name,split=split.get(cid,'EXTERNAL_PUBLIC_CANDIDATE'),source_type=typ,
                         access_role=role,section_or_field=section,chunk=i//3000+1,
                         source_text=text[i:i+3000],source_link=url,
                         source_date=source_date,status=status,source_location=location,
                         raw_text_file=raw_file,retrieved_date='2026-10-27 America/New_York'))
for t in targets:
    add(t['target_id'],t['company_name'],'ORIGINAL_INTERNS_EXCEL','TARGET_ALLOWED',
        'Revenue, EBITDA, derived Debt',json.dumps({k:t[k] for k in ('revenue','ebitda','debt','debt_basis','amount_unit','period')}),
        'https://docs.google.com/spreadsheets/d/1hhacI53Ya8af_PFjpP7Nqf77SgGDy6Lyu9WqMT8HH-s/edit',location='Cached original exact company records. Debt = target_revenue * target_debt_to_revenue.')
for r in read(E/'collection.json'):
    txt=pathlib.Path(r['text_file']).read_text() if r.get('text_file') else r.get('error',r['status'])
    add(r['company_id'],r['company_name'],'COMPANY_WEBSITE','TARGET_WEBSITE_REQUIRES_BUSINESS_ONLY_FILTER' if r['role']=='TARGET' else 'PUBLIC_CANDIDATE',
        'Fetched page text including possible navigation; not a verified facet extraction',txt,r.get('source_url',r['requested_url']),r['status'],raw_file=r.get('text_file',''))
add('IQ254957567',names['IQ254957567'],'COMPANY_WEBSITE_WEB_READER','TARGET_ALLOWED',
    'About page business summary, paraphrased',
    'Paylocity supplies HR, payroll and spend-management technology. Its platform covers recruiting, onboarding, benefits, time tracking and workforce workflows, with additional finance and IT offerings. It serves small, midsize and enterprise organizations and works with partners including accountants and brokers.',
    'https://www.paylocity.com/company/about-us/','READ_VIA_WEB_TOOL_PARAPHRASE_NOT_DIRECT_SCRAPE',location='Company About page and product navigation')
for r in read(E/'sec_index.json'):
    text=json.dumps({k:v for k,v in r.items() if k not in ('text_file',)},ensure_ascii=False)
    add(r['company_id'],r['company_name'],'SEC_EDGAR','PUBLIC_CANDIDATE_OR_EVALUATION_ONLY_NEVER_TARGET_INPUT',
        'Annual filing index and identity mapping',text,r.get('annual_filing_url',r.get('source_url','')),r['status'],r.get('filing_date','UNKNOWN'))
    if r.get('text_file'):
        add(r['company_id'],r['company_name'],'SEC_ANNUAL_REPORT','PUBLIC_CANDIDATE_OR_EVALUATION_ONLY_NEVER_TARGET_INPUT',
            'Full extracted annual-report text. Numbers retained; inspect source context and units.',pathlib.Path(r['text_file']).read_text(),r['annual_filing_url'],
            'FETCHED_TEXT_NOT_FACT_VERIFIED',r['filing_date'],raw_file=r['text_file'])
for file,typ in [('Targets_560','SUPPLIED_CAPIQ_EXCEL'),('WRDS_Matched_Latest','SUPPLIED_WRDS_FIRM_RATIOS'),('FF49_Benchmarks_560','SUPPLIED_WRDS_FF49_MEDIANS')]:
    for r in read(ROOT/'prepared'/f'{file}.json'):
        cid=r['company_id'];url=r.get('source_url','https://drive.google.com/file/d/14NvyjcLDPbrm4fGh03xJpMrAJ9Q-VeqB/view')
        add(cid,names.get(cid,''),typ,'PUBLIC_CANDIDATE_OR_EVALUATION_ONLY_NEVER_TARGET_INPUT',
            'Full source record; hidden for this target role',json.dumps(r,ensure_ascii=False),url,source_date=r.get('benchmark_date',r.get('Date','UNKNOWN')),
            location=r.get('source_location',r.get('source_sheet','Latest ratios matched conservatively')))
candidates=read(B/'retrieved_candidates.json');seen=set()
for r in candidates:
    gv=r['candidate_gvkey']
    if gv in seen:continue
    seen.add(gv)
    add('GVKEY'+gv,r['candidate_name'],'WRDS_API_COMPUSTAT','PUBLIC_CANDIDATE_ONLY_NEVER_TARGET_PROFILE',
        'Business description',r['candidate_description'],r['source_url'],'API_RECORD_RETRIEVED_CURRENT_LISTING_UNVERIFIED',location='gvkey='+gv)
with (E/'Evidence.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(E/'Evidence.json').write_text(json.dumps(rows,ensure_ascii=False))
status=[{'Item':'Target universe','Value':560,'Detail':'Website plus three permitted figures only for target inputs.'},
        {'Item':'Development / validation','Value':420,'Detail':'WEN and PCTY previously explored; retained in development. Tune only within this split.'},
        {'Item':'Final holdout','Value':140,'Detail':'Labels kept in separate file. Final out-of-sample valuation test NOT RUN.'},
        {'Item':'Company catalog records','Value':142911,'Detail':'North America and Global, including inactive and duplicate records. Not 142911 confirmed listed firms.'},
        {'Item':'Active catalog records','Value':73410,'Detail':'Active company status is not proof of current listing.'},
        {'Item':'Target retrieval coverage','Value':455,'Detail':'Initial lexical candidate discovery, no final similarity percentages or comp approval.'},
        {'Item':'Abstentions','Value':105,'Detail':'No readable permitted website text. No public-only target data fallback.'},
        {'Item':'Candidate rows','Value':len(candidates),'Detail':'Top 10 lexical matches where available; require listing, identity, business and facet review.'},
        {'Item':'Evidence rows','Value':len(rows),'Detail':'Long text split into 3000-character chunks, adjacent source URLs.'},
        {'Item':'Final scored targets','Value':0,'Detail':'Facet scoring, weights calibration, financial harmonization and final test remain unfinished.'},
        {'Item':'WRDS API','Value':'Authenticated successfully','Detail':'Token not persisted in code, evidence or workbook.'},
        {'Item':'Amounts and dates','Value':'Preserved from source','Detail':'Original interns-list units and LTM date not documented. Do not silently substitute CapIQ net debt.'}]
(E/'Status.json').write_text(json.dumps(status))
print('Evidence rows',len(rows),'unique WRDS retrieved candidate profiles',len(seen))
