"""Remove restricted-origin observations, inherited claims and dependent rankings.
Run on a publication checkout; raw local research originals are not rewritten.
"""
from pathlib import Path
import collections,csv,gzip,hashlib,json,re,shutil,sys
from source_policy import restricted,require_allowed
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'website/data'
STATS=collections.Counter()
DROP=object()
def load(p):
    return json.load(gzip.open(p,'rt')) if p.suffix=='.gz' else json.loads(p.read_text())
def save(p,v):
    text=json.dumps(v,ensure_ascii=False,separators=(',',':'))
    require_allowed(v)
    if p.suffix=='.gz':p.write_bytes(gzip.compress(text.encode(),mtime=0))
    else:p.write_text(text)
def direct_bad(v):
    if not isinstance(v,dict):return False
    for k,x in v.items():
        if not isinstance(x,(str,int,float)):continue
        if k.lower().replace(' ','_') in ['source_type','source','provider','system','source_link','source_url','url','description_source','dataset','source_file','source_name','candidate_source'] and restricted(str(x)):
            return True
    for k in ['source','Source','primary_source','business_description_source']:
        if isinstance(v.get(k),dict) and direct_bad(v[k]):return True
    return False

def clean(v):
    if isinstance(v,str):return DROP if restricted(v) else v
    if isinstance(v,list):
        out=[]
        for x in v:
            y=clean(x)
            if y is not DROP:out.append(y)
        return out
    if isinstance(v,dict):
        if direct_bad(v):STATS['atomic_records_removed']+=1;return DROP
        out={}
        for k,x in v.items():
            if restricted(k):continue
            y=clean(x)
            if y is not DROP:out[k]=y
        # Do not retain a description/value when its attribution was removed.
        if any(k in v and k not in out for k in ['source','source_id','Source Link','Source Type','business_description_source']):
            return DROP
        return out
    return v

def fields(p):
    for k in ['main_facets','industry_facets','industry_standard_facets','business_segments']:
        yield from p.get(k,[])
    yield from (p.get('main_patch') or {}).values()

def profile(p):
    # Find source/evidence lineage before removing any payload.
    sources=p.get('sources',{})
    if not isinstance(sources,dict):return clean(p)
    sources={k:v for k,v in sources.items() if not restricted(v)}
    p['sources']=sources
    evidence=p.get('evidence',{})
    original_evidence=set(evidence)
    evidence={k:v for k,v in evidence.items() if v.get('source_id') in sources and not restricted(v)}
    STATS['source_observations_removed']+=len(original_evidence)-len(evidence)
    p['evidence']=evidence
    for f in fields(p):
        if not isinstance(f,dict):continue
        old=set(f.get('evidence_ids',[])+f.get('other_evidence_ids',[]))
        # All old extracted categories may have seen the mixed-source corpus.
        for derived in ['categories','category','score','similarity']:
            f.pop(derived,None)
        for k in ['evidence_ids','other_evidence_ids','excluded_evidence_ids']:
            if k in f:f[k]=[e for e in f[k] if e in evidence]
        ids=f.get('evidence_ids',[])
        if not ids and f.get('other_evidence_ids'):
            ids=f['other_evidence_ids'][:3];f['evidence_ids']=ids;f['other_evidence_ids']=f['other_evidence_ids'][3:]
        if old-set(evidence):
            # Derived categories and old cross-source conclusions cannot be reused.
            for k in ['categories','category','text','value','source_difference_notes','score','similarity']:
                f.pop(k,None)
            STATS['dependent_facet_values_invalidated']+=1
        f['cross_validation']={'status':'SOURCE_SET_REVISED_MEANING_REVIEW_REQUIRED' if ids else 'NO_ALLOWED_EVIDENCE','source_types':sorted({sources[evidence[e]['source_id']].get('source_type','UNKNOWN') for e in ids}),'fact_verified':False}
        if not ids:
            f['status']='UNKNOWN';f['missing_reason']='No admitted evidence remains after source-policy filtering.'
        else:f['status']='SOURCE_EXCERPTS_RETRIEVED_NOT_FACT_VERIFIED'
    desc=p.get('business_description')
    if isinstance(desc,dict) and desc.get('source_id') not in sources:
        p.pop('business_description',None);STATS['business_descriptions_removed']+=1
        p['industry_modules']=[]
        p['industry_classification_basis']={'source':'Permitted-source routing review required','used_in_pseudo_private_matching':False}
        # Promote only a separately retained, attributed allowed passage.
        fs=[f for f in p.get('main_facets',[]) if f.get('name')=='Core Business Activity']
        if fs and fs[0].get('evidence_ids'):
            e=evidence[fs[0]['evidence_ids'][0]]
            p['business_description']={'text':e['text'],'source_id':e['source_id'],'status':'ALLOWED_SOURCE_PASSAGE_NOT_INDEPENDENTLY_VERIFIED'}
    for k in ['source_issues','audit_notes','source_difference_notes']:p.pop(k,None)
    p['main_filled']=sum(bool(f.get('evidence_ids')) for f in p.get('main_facets',[])) if 'main_facets' in p else p.get('main_filled',0)
    if 'industry_facets' in p:p['industry_filled']=sum(bool(f.get('evidence_ids')) for f in p['industry_facets'])
    if 'research_source_count' in p:p['research_source_count']=len(sources)
    p['source_policy_version']='2026-11-15-excluded-restricted-origin'
    p=clean(p)
    return p

def run():
    assert not (D/'comparison_rebuild_manifest.json.gz').exists(), "Rebuilt comparisons exist: use --validate, not the retired cleanup generation step"
    # Redundant role-era payloads contain stale descriptions, joins and scores.
    for pattern in ['company_group_*.json.gz','facet_extra_profiles_*.json.gz','companies.json.gz','company_registry.json.gz','catalog.json.gz']:
        for p in D.glob(pattern):p.unlink();STATS['obsolete_payloads_removed']+=1
    # All old candidate selection/ranking used the mixed-origin corpus.
    for p in (D/'matches').glob('*.gz'):
        data=load(p);STATS['rankings_withdrawn']+=sum(len(v) for v in data.values());save(p,{k:[] for k in data})
    for folder in ['research','general_refresh_20261112','quality_refresh_20261112']:
        for path in sorted((D/folder).glob('*.gz')):
            data=load(path);out={}
            for k,p in data.items():
                v=profile(p)
                if v is not DROP:out[k]=v
            save(path,out);STATS[folder+'_profiles']+=len(out)
    for path in (D/'classification').glob('*.gz'):
        data=load(path);out={}
        for key,p in data.items():
            desc_bad=restricted(p.get('business_description_source',{}))
            primary_bad=restricted(p.get('primary_sic',{}))
            v=clean(p)
            if v is DROP:v={'company_id':key,'classification_observations':[],'segments':[]}
            if primary_bad:
                v['primary_sic']=next((x for x in v.get('classification_observations',[]) if x.get('system')=='SEC SIC'),None)
                STATS['primary_classifications_invalidated']+=1
            if desc_bad:
                for k in ['selected_facet_templates','primary_industry','template_selection_basis','template_selection_method']:
                    v.pop(k,None)
                v['selected_facet_templates']=[];v['primary_industry']='UNKNOWN — allowed-source classification needed'
            v.pop('segment_source_difference_note',None)
            # Segment records without surviving attribution are not accepted.
            v['segments']=[x for x in v.get('segments',[]) if x.get('source')]
            out[key]=v
        save(path,out)
    for path in D.rglob('*.gz'):
        if path.parent.name in ['research','general_refresh_20261112','quality_refresh_20261112','classification','matches']:continue
        v=clean(load(path));save(path,{} if v is DROP else v)
    # Recompute catalog counts from allowed-source profiles, not old estimates.
    idx=load(D/'research_catalog.json.gz')
    counts={}
    for path in (D/'research').glob('*.gz'):
        for key,p in load(path).items():counts[key]=(p.get('main_filled',0),p.get('industry_filled',0),len(p.get('sources',{})))
    for c in idx['companies']:
        a,b,n=counts.get(c['key'],(0,0,0));c.update(main_filled=a,industry_filled=b,sources=n)
    save(D/'research_catalog.json.gz',idx)
    for path in D.glob('*.json'):
        v=clean(load(path));save(path,{} if v is DROP else v)
    prune_inherited_routes()
    validate()
    print(json.dumps(dict(STATS),indent=2))
    return dict(STATS)

def prune_inherited_routes():
    """A checklist inherited solely from an excluded SIC must not survive as an assignment."""
    allowed=set()
    for path in (D/'classification').glob('*.gz'):
        for key,c in load(path).items():
            primary=c.get('primary_sic')
            if primary and not restricted(primary):allowed.add(key)
    changed=0;removed=0
    for folder in ['research','general_refresh_20261112','quality_refresh_20261112']:
        for path in (D/folder).glob('*.gz'):
            data=load(path);dirty=False
            for key,p in data.items():
                if key in allowed:continue
                fields=p.get('industry_standard_facets',[])
                keep=[f for f in fields if f.get('scope_key')!='issuer']
                if len(keep)!=len(fields):
                    removed+=len(fields)-len(keep);p['industry_standard_facets']=keep
                    p['industry_route_status']='NO_INDEPENDENT_ALLOWED_SIC_ISSUER_CHECKLIST_WITHDRAWN'
                    dirty=True;changed+=1
            if dirty:save(path,data)
    STATS['inherited_issuer_field_assignments_removed']=removed
    STATS['profiles_with_inherited_routes_removed']=changed
    print(json.dumps({'inherited_issuer_field_assignments_removed':removed,'profiles_with_inherited_routes_removed':changed}),flush=True)
    return removed

def validate():
    n=0;targets=set()
    for path in D.rglob('*.gz'):
        data=load(path);require_allowed(data);n+=1
        if path.parent.name in ['research','general_refresh_20261112','quality_refresh_20261112']:
            for p in data.values():
                for e in p.get('evidence',{}).values():assert e['source_id'] in p.get('sources',{}),path
                for f in fields(p):
                    for e in f.get('evidence_ids',[])+f.get('other_evidence_ids',[]):assert e in p.get('evidence',{}),path
        if path.parent.name=='matches':
            for tid,rs in data.items():
                for row in rs:
                    assert row.get('Method Version')=='permitted-evidence-v3.2-2026-11-15' and row['Target ID']==tid
    inputs=load(D/'comparison_inputs.json.gz');assert len(inputs)==560,len(inputs)
    STATS['validated_compressed_payloads']=n;STATS['original_target_inputs_retained']=len(inputs)
    return dict(STATS)

def export_csv(destination,old_csv=None):
    """Clean snapshots; retain only independently attributed raw rows from old delivery."""
    cols=['dataset','company_id','company_name','entity_role','facet','source_url','source_date','text','record_json']
    counts=collections.Counter();csv.field_size_limit(2**31-1)
    with gzip.open(destination,'wt',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=cols);w.writeheader()
        def emit(dataset,key,name,role,record,facet='',url='',date='',text=''):
            row=dict(zip(cols,[dataset,key,name,role,facet,url,date,text,json.dumps(record,ensure_ascii=False)]));require_allowed(row);w.writerow(row);counts[dataset]+=1
        if old_csv:
            with gzip.open(old_csv,'rt',encoding='utf-8-sig',newline='') as f:
                for row in csv.DictReader(f):
                    ds=row.get('dataset','')
                    # Preserve raw provider/source observations only; mixed derived tables are rebuilt below.
                    if ds=='Official_Website_Refresh':continue
                    if not ds.startswith(('LSEG_','Provided_CapIQ_','Provided_Instructor_','SEC_','Official_Website_')):continue
                    if restricted(row):continue
                    try:record=json.loads(row.get('record_json','{}'))
                    except ValueError:continue
                    emit(ds,row.get('company_id',''),row.get('company_name',''),row.get('entity_role',''),record,row.get('facet',''),row.get('source_url',''),row.get('source_date',''),row.get('text',''))
        for path in sorted((D/'research').glob('*.gz')):
            for key,p in load(path).items():
                role='TARGET' if p.get('is_original_target') else 'PUBLIC'
                emit('Unified_Public_Research',key,p['name'],role,p)
        for folder,dataset in [('classification','Industry_Classification'),('growth','Growth_Signals'),('general_refresh_20261112','General_Evidence_Update'),('quality_refresh_20261112','Industry_Evidence_Update')]:
            for path in sorted((D/folder).glob('*.gz')):
                for key,p in load(path).items():emit(dataset,key,p.get('company_name',p.get('name','')),'',p)
        for key,p in load(D/'comparison_inputs.json.gz').items():emit('Restricted_Target_Inputs',key,p.get('target_name',''),'TARGET',p)
        if (D/'official_website_refresh_20261115.json.gz').exists():
            for p in load(D/'official_website_refresh_20261115.json.gz'):
                emit('Official_Website_Refresh',p['target_id'],'','TARGET',p,url=p.get('final_url',p.get('requested_url','')),date=p.get('retrieved_at',''),text=p.get('text',''))
        if (D/'comparison_rebuild_manifest.json.gz').exists():
            evidence={}
            for path in sorted((D/'matches').glob('*.gz')):
                for tid,rows in load(path).items():
                    for r in rows:
                        record={k:v for k,v in r.items() if k!='Facet Details'}
                        emit('Public_Comparables',tid,r['Target Name'],'TARGET',record,url=r['Candidate Source URL'])
                        for f in r['Facet Details']:
                            refs={}
                            for side,entity,role in [('target',tid,'TARGET'),('candidate',r['Canonical Company ID'],'PUBLIC')]:
                                value={**f[side],'entity_id':entity,'entity_role':role,'module_code':f.get('module_code'),'standard_id':f.get('standard_id')}
                                eid=hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:24]
                                evidence[eid]=value;refs[side+'_facet_evidence_id']=eid
                            detail={k:v for k,v in f.items() if k not in ['target','candidate']}
                            detail.update(target_id=tid,candidate_id=r['Canonical Company ID'],candidate_ric=r['Candidate RIC'],**refs)
                            emit('Comparable_Facet_Scores',tid,r['Target Name'],'TARGET',detail,facet=f['facet'])
            for eid,value in evidence.items():
                value['matching_evidence_id']=eid
                emit('Matching_Facet_Evidence',value['entity_id'],'',value['entity_role'],value,facet=value['facet'],text=value.get('text',''))
            emit('Comparable_Methodology','','','',load(D/'comparison_rebuild_manifest.json.gz'))

        if (D/'forecast_csv_additions.json.gz').exists():
            for row in load(D/'forecast_csv_additions.json.gz'):
                require_allowed(row);w.writerow(row);counts[row['dataset']]+=1

    # Full readback, including compressed content, not just filenames.
    with gzip.open(destination,'rt',encoding='utf-8',newline='') as f:
        n=0
        for row in csv.DictReader(f):require_allowed(row);json.loads(row['record_json']);n+=1
    assert n==sum(counts.values())
    return dict(counts)

if __name__=='__main__':
    if '--validate' in sys.argv:print(json.dumps(validate()))
    else:run()
