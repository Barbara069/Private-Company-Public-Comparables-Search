"""Build provenance and cross-source review tables, without changing prior rankings."""
import collections,csv,datetime as dt,hashlib,json,pathlib,re,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from multisource_audit import P,R,O,load,store,write
from score_comp_draft import PATTERNS,CATS
def section(text,sec=False):
    text=re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','',text)
    if sec:
        starts=list(re.finditer(r'\bITEM\s*1\s*[.\-:]?\s*BUSINESS\b',text,re.I))
        options=[]
        for m in starts:
            rest=text[m.end():];end=re.search(r'\bITEM\s*1A\b',rest,re.I);s=rest[:end.start()] if end else rest[:50000]
            if len(s)>2000:options.append(s)
        if options:text=max(options,key=len)
    return text[:50000]
def sourcebody(row):
    f=row.get('text_file')
    if f and pathlib.Path(f).exists():return section(pathlib.Path(f).read_text(errors='replace'),row.get('source_type')=='SEC_ANNUAL_FILING')
    return row.get('text') or ''
def main():
    docs=[];metadata={}
    def add(role,ident,name,provider,text='',url=None,location=None,status='AVAILABLE_NOT_FACT_VERIFIED',source_date='UNKNOWN',retrieved=None,access=None,method=None,full_file=None):
        key=f'{role}:{ident}:{provider}:{len(docs)+1}'
        text=re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','',str(text or ''))
        row={'Evidence ID':key,'Entity Role':role,'Entity ID':ident,'Company Name':name,'Source Type':provider,'Access Role':access or ('PUBLIC_CANDIDATE_EVIDENCE' if role=='PUBLIC' else 'TARGET_REFERENCE_ONLY_EXCLUDED_FROM_SELECTION'),'Status':status,'Source Text':text[:1500] or None,'Source Link':url,'Source Field or Location':location,'Source Date':source_date,'Retrieved At':retrieved or '2026-10-28','Acquisition Method':method or provider,'Full Text or Snapshot Path':full_file,'Text SHA256':hashlib.sha256(text.encode()).hexdigest() if text else None}
        docs.append(row);metadata[key]='' if status.startswith('SEARCH_RESULT_ONLY') else text;return key
    originals=load(R/'target_allowed_profiles.json');masters={x['company_id']:x for x in load(P/'prepared/Targets_560.json')}
    mapping={x['company_id']:x for x in load(P.parent/'lseg_downloads/target_mapping_560.json')}
    prof={x['Instrument']:x for x in load(P.parent/'lseg_downloads/delivery/company_profiles_raw.json')}
    secold={x['company_id']:x for x in load(P/'web_evidence/sec_index.json')}
    refs={x['company_id']:x for x in load(P/'web_evidence/wrds_api/target_reference_matches.json')}
    catalog={x['gvkey']:x for x in load(P/'web_evidence/wrds_api/company_catalog_all.json')}
    for t in originals:
        tid=t['target_id'];name=t['target_name'];m=masters[tid];pr=prof.get(mapping[tid]['ric'],{})
        urls=collections.defaultdict(list)
        for q in t['quotes']:urls[q['url']].append(q)
        if not urls:add('TARGET',tid,name,'OFFICIAL_WEBSITE',url=t['website'],status='NO_USABLE_WEBSITE_FACT_EVIDENCE',access='TARGET_ALLOWED_WEBSITE_ONLY')
        for url,qs in urls.items():
            files=[q.get('file','') for q in qs];method='WEB_SEARCH_OFFICIAL_PAGE' if all(f=='WEB_SEARCH_OFFICIAL_PAGE' for f in files) else 'DIRECT_WEBSITE_EXTRACTION_OR_MIXED_CACHE'
            add('TARGET',tid,name,'OFFICIAL_WEBSITE','\n'.join(q['text'] for q in qs),url=url,location='Source sentences retained in target_allowed_profiles.json',access='TARGET_ALLOWED_WEBSITE_ONLY',method=method,full_file='; '.join(dict.fromkeys(files)))
        add('TARGET',tid,name,'LSEG',pr.get('TR.BUSINESSSUMMARY'),url=str(P.parent/'lseg_downloads/delivery/company_profiles_raw.json'),location='Instrument='+mapping[tid]['ric']+'; TR.BusinessSummary',status='REFERENCE_ONLY; '+mapping[tid].get('mapping_status',''),full_file=str(P.parent/'lseg_downloads/delivery/company_profiles_raw.json'))
        add('TARGET',tid,name,'CAPITAL_IQ',m.get('business_description'),url=m.get('source_url'),location=m.get('source_location'),method='PROVIDED_CAPITAL_IQ_WORKBOOK',source_date='SNAPSHOT_DATE_REQUIRES_VERIFICATION')
        ref=refs.get(tid,{});keys=ref.get('gvkeys',[]);wr=catalog.get(keys[0],{}) if len(keys)==1 else {}
        add('TARGET',tid,name,'WRDS_COMPUSTAT',wr.get('busdesc'),url=wr.get('_source_url'),location='gvkey='+str(wr.get('gvkey'))+'; company.busdesc',status=ref.get('status','NO_CONSERVATIVE_WRDS_REFERENCE_MATCH'),full_file=str(P/'web_evidence/wrds_api/company_catalog_all.json'))
        s=secold.get(tid,{})
        add('TARGET',tid,name,'SEC_ANNUAL_FILING',sourcebody(dict(s,source_type='SEC_ANNUAL_FILING')),url=s.get('annual_filing_url') or s.get('source_url'),status=s.get('status','NO_EXISTING_SEC_EVIDENCE'),location=f"{s.get('form','')} report period {s.get('report_date','')}; business-section extraction, not every-line fact verification",source_date=s.get('filing_date','UNKNOWN'),full_file=s.get('text_file'))
    snapshot={}
    for f in sorted((R/'shortlist_batches').glob('*.json')):
        for x in load(f):snapshot[x['Instrument']]=str(f)
    webs=collections.defaultdict(list)
    for x in load(O/'public_web_index.json'):webs[x['ric']].append(x)
    secs={x['ric']:x for x in load(O/'public_sec_index.json')}
    public=load(R/'Candidate_Data.json')
    searchrows=[]
    for f in ['official_search_evidence.json','remaining_official_evidence.json','two_target_official_evidence.json']:
        if (R/f).exists():searchrows+=load(R/f)
    for c in public:
        ric=c['candidate_ric'];name=c['candidate_name'];snap=snapshot.get(ric,str(R/'shortlist_profiles.json'))
        add('PUBLIC',ric,name,'LSEG',c['description'],url=snap,location='TR.BusinessSummary; Instrument='+ric+'; provider homepage alone is not the record citation',status='API_RECORD_AVAILABLE; NOT_FACT_VERIFIED',method='LSEG_DESKTOP_API_RESPONSE_SNAPSHOT',full_file=snap)
        add('PUBLIC',ric,name,'WRDS_COMPUSTAT',c.get('WRDS Description'),url=c.get('WRDS Description Link'),location='gvkey='+str(c.get('wrds_gvkey'))+'; company.busdesc',status='UNIQUE_NAME_REFERENCE_JOIN_REQUIRES_REVIEW' if c.get('WRDS Description') else 'NO_MATCHED_WRDS_DESCRIPTION',method='WRDS_API_CACHED_COMPANY_RECORD',full_file=str(P/'web_evidence/wrds_api/company_catalog_all.json'))
        add('PUBLIC',ric,name,'CAPITAL_IQ',c.get('Provided CapIQ Description'),url=c.get('CapIQ Source Link'),location=c.get('CapIQ Source Location'),status='PROVIDED_WORKBOOK_MATCH_NOT_INDEPENDENTLY_VERIFIED' if c.get('Provided CapIQ Description') else 'NOT_COVERED_BY_PROVIDED_560_COMPANY_FILE',source_date='SNAPSHOT_DATE_REQUIRES_VERIFICATION',method='PROVIDED_CAPITAL_IQ_WORKBOOK')
        for x in webs[ric] or [{}]:
            add('PUBLIC',ric,name,'OFFICIAL_WEBSITE',sourcebody(x),url=x.get('source_url'),status=x.get('status','NO_WEBSITE_EVIDENCE'),location=x.get('title'),source_date=x.get('source_date','UNKNOWN'),retrieved=x.get('retrieved_at'),method='DIRECT_HTTP_OR_PRIOR_OFFICIAL_PAGE_CACHE; identity not manually verified',full_file=x.get('text_file'))
        from multisource_audit import host
        for s in searchrows:
            if host(s.get('source_url'))==host(c.get('candidate_website')) and host(c.get('candidate_website')):
                add('PUBLIC',ric,name,'OFFICIAL_WEBSITE',s.get('text'),url=s['source_url'],location=s.get('source_title'),method='WEB_SEARCH_RETRIEVED_OFFICIAL_PAGE; same underlying website is not an independent source family')
        s=secs.get(ric,{})
        add('PUBLIC',ric,name,'SEC_ANNUAL_FILING',sourcebody(s),url=s.get('source_url'),status=s.get('status','NO_SEC_EVIDENCE'),location=f"{s.get('form','')} report period {s.get('report_date','')}; {s.get('identity_status','')}",source_date=s.get('filing_date','UNKNOWN'),retrieved=s.get('retrieved_at'),full_file=s.get('text_file'))
    for r in load(O/'Reviewed_Web_Evidence.json'):
        add(r['role'],r['id'],r['name'],r['provider'],r['text'],url=r['url'],status=r['status'],source_date=r.get('source_date','UNKNOWN'),method=r['method'],access='TARGET_ALLOWED_WEBSITE_ONLY' if r['role']=='TARGET' and r['provider']=='OFFICIAL_WEBSITE' else None)
    # External verification facts can be compared diagnostically, but never become target selector inputs.
    providers=['OFFICIAL_WEBSITE','LSEG','WRDS_COMPUSTAT','CAPITAL_IQ','SEC_ANNUAL_FILING','OTHER_WEB'];groups=collections.defaultdict(list)
    for r in docs:groups[(r['Entity Role'],r['Entity ID'],r['Company Name'])].append(r)
    checks=[];coverage=[]
    chunkcache={key:[s.strip() for s in re.split(r'\n+|(?<=[.!?;])\s+',text) if 35<len(s.strip())<2000] for key,text in metadata.items()}
    print('Source register ready',len(docs),'entities',len(groups),flush=True)
    core=list(PATTERNS)
    for (role,ident,name),rs in groups.items():
        sourcecount=collections.Counter(r['Source Type'] for r in rs if metadata[r['Evidence ID']])
        coverage.append({'Entity Role':role,'Entity ID':ident,'Company Name':name,**{p+' Documents':sourcecount[p] for p in providers},'Web Search Retrieved Official Pages':sum('WEB_SEARCH' in r['Acquisition Method'] for r in rs),'Distinct Source Families With Text':len(sourcecount),'Selection Boundary':'Official website only for target; other columns are external diagnostic references' if role=='TARGET' else 'Public evidence can use all listed sources','Verification':'DOCUMENT_COLLECTION_AND_AUTOMATIC_REVIEW_FLAGS; NOT_FACT_BY_FACT_VERIFIED'})
        for facet in core:
            row={'Entity Role':role,'Entity ID':ident,'Company Name':name,'Facet':facet};nonempty=[];alltags=[]
            for provider in providers:
                values=[];ids=[];tags=set()
                for r in rs:
                    if r['Source Type']!=provider:continue
                    chunks=chunkcache[r['Evidence ID']]
                    hits=[s for s in chunks if re.search(PATTERNS[facet],s,re.I)]
                    if facet=='Geography Served':hits=[s for s in hits if re.search(r'operat|serves?|customers?|across|markets?|worldwide|global|international|sales',s,re.I) and not re.search(r'headquarter|based in|based company',s,re.I)]
                    if not hits:continue
                    ids.append(r['Evidence ID'])
                    joined=' '.join(hits[:3])
                    if facet in CATS:
                        ts={k for k,p in CATS[facet].items() if re.search(p,joined,re.I)};tags|=ts
                    else:values.append(' '.join(hits[0].split()[:40]))
                val='; '.join(sorted(tags)) if facet in CATS else ' | '.join(dict.fromkeys(values))[:300]
                row[provider+' Value']=val or None;row[provider+' Evidence IDs']='; '.join(ids) or None
                if val:nonempty.append(provider)
                if tags:alltags.append(frozenset(tags))
            if len(nonempty)<2:state='SINGLE_SOURCE_OR_INSUFFICIENT_EVIDENCE'
            elif facet in CATS and len(set(alltags))>1:state='DIFFERENT_EXPLICIT_TAG_SETS_REVIEW; NOT_PROVEN_CONTRADICTION'
            elif facet in CATS:state='SAME_EXTRACTED_TAGS; NOT_INDEPENDENT_FACT_VERIFICATION'
            else:state='MULTIPLE_SOURCE_EXCERPTS_AVAILABLE; MANUAL_SEMANTIC_COMPARISON_REQUIRED'
            row.update({'Source Families With Facet Evidence':len(nonempty),'Cross Source Review Flag':state,'Interpretation':'Different wording, scope, segments or dates can cause differences. Keyword categories are not verified facts.','Target Reference Boundary':'NON_WEBSITE_COLUMNS_EXCLUDED_FROM_TARGET_SELECTION' if role=='TARGET' else 'PUBLIC_COMPARABLE_EVIDENCE'})
            checks.append(row)
        if len(coverage)%500==0:print('Facet cross checks',len(coverage),'/',len(groups),flush=True)
    write('Target_Sources',[r for r in docs if r['Entity Role']=='TARGET']);write('Public_Sources',[r for r in docs if r['Entity Role']=='PUBLIC']);write('Source_Coverage',coverage);write('Facet_Cross_Check',checks)
    summary={'target_entities':len(originals),'public_candidate_entities':len(public),'source_document_or_missing_status_rows':len(docs),'facet_cross_check_rows':len(checks),'source_text_rows_by_role_and_type':dict(collections.Counter(r['Entity Role']+' | '+r['Source Type'] for r in docs if metadata[r['Evidence ID']])),'automatic_difference_flags':sum('DIFFERENT_EXPLICIT' in x['Cross Source Review Flag'] for x in checks),'verified_factual_contradictions':0,'prior_scores_modified':False}
    store(O/'summary.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
