"""Evidence-first draft retrieval/scoring, without target database descriptions or labels.
Scores are uncalibrated text similarity, not a probability or analyst validation.
"""
import collections,csv,hashlib,json,pathlib,re,sys,urllib.parse,math
import numpy as np
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
P=pathlib.Path(__file__).resolve().parent;O=P/'global_run_20261028'
def load(p):return json.loads(pathlib.Path(p).read_text())
def save(name,data):
    def sanitize(v):
        if isinstance(v,float) and not math.isfinite(v):return None
        if isinstance(v,dict):return {k:sanitize(x) for k,x in v.items()}
        if isinstance(v,list):return [sanitize(x) for x in v]
        return v
    data=sanitize(data)
    (O/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str))
    if data and isinstance(data,list) and isinstance(data[0],dict):
        fields=list(dict.fromkeys(k for r in data for k in r))
        with (O/(name+'.csv')).open('w') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
def norm(s):
    words=re.findall('[a-z0-9]+',str(s).lower())
    return ''.join(w for w in words if w not in {'the','inc','incorporated','corporation','corp','limited','ltd','plc','co','company','holdings','holding','sa','ag','nv','se','group','class','a','b','c'})
def clean(s):return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','',str(s or ''))
def sentences(s):return [x.strip() for x in re.split(r'\n+|(?<=[.!?;])\s+',clean(s)) if 45<len(x.strip())<1800]
BAD=re.compile(r'investor|nasdaq|nyse|10-k|annual report|sec filing|stock price|share price|market cap|quarter.{0,15}results|cookie|privacy|copyright|all rights reserved|accept all|consent|javascript|access denied|cloudflare|terms of use|log in|sign in',re.I)
MARKETING=re.compile(r'people matter|our dna|caring is|innovation powers|join our|friendly customer care|images and other assets|sake of your content|every step of the way|unlock new potential|forward together|good thing our|our culture|our leadership|our mission|our vision',re.I)
BUS=re.compile(r'\b(manufactur\w*|provid\w*|develop\w*|design\w*|operat\w*|distribut\w*|sell\w*|market\w*|serv\w*|customer\w*|client\w*|product\w*|platform\w*|software|restaurant\w*|franchis\w*|equipment|solution\w*|subscription\w*|payroll|insurance|bank\w*|specializ\w*|health\w*|energy|retail\w*)\b',re.I)
def website_sources():
    rows=load(P/'web_evidence/collection.json')
    if (O/'website_retry_collection.json').exists():rows+=load(O/'website_retry_collection.json')
    by=collections.defaultdict(list)
    for r in rows:
        if r.get('status')!='FETCHED_TEXT_NOT_FACT_VERIFIED' or not r.get('text_file'):continue
        url=r.get('source_url') or r['requested_url']
        if re.search(r'/investor|/news|/press|/financial|/sec-|/annual-report',url,re.I):continue
        # Parse original HTML with boilerplate removed, when available.
        html=pathlib.Path(r['text_file']).with_suffix('.html')
        if html.exists():
            soup=BeautifulSoup(html.read_text(errors='replace'),'html.parser')
            for e in soup(['script','style','noscript','svg','nav','header','footer']):e.decompose()
            text=soup.get_text('\n')
        else:text=pathlib.Path(r['text_file']).read_text(errors='replace')
        for line in sentences(text):
            if not BAD.search(line) and not MARKETING.search(line) and BUS.search(line):by[r['company_id']].append((line,url,r['text_file']))
    for search_file in ['official_search_evidence.json','remaining_official_evidence.json','verified_official_paraphrases.json','two_target_official_evidence.json']:
        if not (O/search_file).exists():continue
        for r in load(O/search_file):
            for line in sentences(r['text']):
                if not BAD.search(line) and not MARKETING.search(line) and BUS.search(line):by[r['company_id']].append((line,r['source_url'],'WEB_SEARCH_OFFICIAL_PAGE'))
    return by
def prepare():
    originals=load(P.parent/'wrds_ratios_20261020/input_companies.json');by=website_sources();targets=[]
    for r in originals:
        cid=r['IQ_COMPANY_ID'];seen=set();quotes=[]
        for text,url,file in by[cid]:
            key=text.lower()
            if key in seen:continue
            seen.add(key);quotes.append({'text':text,'url':url,'file':file})
        # Retain source sentences, rather than use a public database to infer missing facts.
        quotes.sort(key=lambda x:(-len(BUS.findall(x['text'])), -min(len(x['text']),700)))
        quotes=quotes[:25]
        rev=r.get('target_revenue');ratio=r.get('target_debt_to_revenue')
        targets.append(dict(target_id=cid,target_name=r['target_company_name'],website=r['target_ciq_website'] if isinstance(r['target_ciq_website'],str) else '',revenue=rev,ebitda=r.get('target_ebitda'),debt=rev*ratio if isinstance(rev,(int,float)) and isinstance(ratio,(int,float)) else None,financial_unit='UNCONFIRMED_ORIGINAL_UNIT_AND_PERIOD; numeric size not scored',debt_basis='Instructor revenue * instructor debt/revenue',quotes=quotes,text=' '.join(q['text'] for q in quotes)[:15000],status='WEBSITE_EVIDENCE_DRAFT' if len(quotes)>=2 or sum(len(q['text']) for q in quotes)>160 else 'ABSTAIN_INSUFFICIENT_READABLE_WEBSITE'))
    save('target_allowed_profiles',targets)
    if '--targets-only' in sys.argv:
        print('Website target profiles',sum(t['status']=='WEBSITE_EVIDENCE_DRAFT' for t in targets),flush=True);return
    cat=load(P/'web_evidence/wrds_api/company_catalog_all.json');index=collections.defaultdict(dict)
    for r in cat:
        if r.get('costat')!='A' or len(r.get('busdesc') or '')<100:continue
        for k in [norm(r.get('conml')),norm(r.get('conm'))]:
            if k:index[k][r['gvkey']]=r
    profiles={}
    for p in sorted((O/'profile_batches').glob('*.json')):
        for r in load(p):profiles[r['Instrument']]=r
    if (O/'shortlist_profiles.json').exists():
        for r in load(O/'shortlist_profiles.json'):profiles[r['Instrument']]=r
    listed=load(O/'listed_universe.json');candidates=[];seen=set()
    for u in listed:
        issuer=u.get('IssuerOAPermID') or u['RIC']
        if issuer in seen:continue
        title=u['DocumentTitle'].split(', Ordinary Share')[0]
        hits=list(index.get(norm(title),{}).values());ref=hits[0] if len(hits)==1 else None
        prof=profiles.get(u['RIC'],{})
        desc=prof.get('TR.BUSINESSSUMMARY') or (ref or {}).get('busdesc') or ''
        if len(desc)<100:continue
        seen.add(issuer)
        candidates.append(dict(candidate_ric=u['RIC'],candidate_name=prof.get('TR.COMMONNAME') or title,issuer_id=issuer,isin=u.get('IssueISIN'),listing_country=u.get('RCSExchangeCountryLeaf'),exchange=u.get('ExchangeName'),listing_status='LSEG_LIS_ORDINARY_SHARE_PRIMARY_ISSUE_2026-10-28',description=clean(desc),description_source='LSEG' if prof.get('TR.BUSINESSSUMMARY') else 'WRDS_COMPUSTAT',source_link='https://www.lseg.com/en/data-analytics' if prof.get('TR.BUSINESSSUMMARY') else ref['_source_url'],source_locator=('TR.BusinessSummary; Instrument='+u['RIC']) if prof.get('TR.BUSINESSSUMMARY') else 'company.busdesc; gvkey='+ref['gvkey'],wrds_gvkey=(ref or {}).get('gvkey'),wrds_sic=(ref or {}).get('sic'),candidate_website=(ref or {}).get('weburl'),description_identity_match='LSEG_DIRECT' if prof.get('TR.BUSINESSSUMMARY') else 'UNIQUE_NORMALIZED_NAME_MATCH_REVIEW',market_cap_usd=u.get('MktCapCompanyUsd')))
    save('candidate_reference',candidates);print('Allowed website profiles',sum(t['status']=='WEBSITE_EVIDENCE_DRAFT' for t in targets),'/',len(targets),'listed issuer descriptions',len(candidates),flush=True)
def encode(texts,label):
    key=hashlib.sha256(json.dumps(texts).encode()).hexdigest()[:16];p=O/(label+'_'+key+'.npy')
    if p.exists():return np.load(p)
    model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2',local_files_only=True)
    # Three chunks prevent first-256-token truncation of long website profiles.
    out=[]
    for start in range(0,len(texts),1000):
        chunk=texts[start:start+1000];parts=[];owners=[]
        for i,text in enumerate(chunk):
            words=text.split()
            for j in range(0,min(len(words),600),200):parts.append(' '.join(words[j:j+200]));owners.append(i)
            if not words:parts.append('Unknown');owners.append(i)
        e=model.encode(parts,batch_size=128,normalize_embeddings=True,show_progress_bar=False)
        vals=np.stack([e[np.array(owners)==i].mean(axis=0) for i in range(len(chunk))]);vals/=np.linalg.norm(vals,axis=1,keepdims=True)
        out.append(vals);print(label,min(start+1000,len(texts)),'/',len(texts),flush=True)
    arr=np.concatenate(out);np.save(p,arr);return arr
def retrieve():
    ts=load(O/'target_allowed_profiles.json');cs=load(O/'candidate_reference.json')
    maps=load(P.parent/'lseg_downloads/target_mapping_560.json')
    identity={r.get('company_id',r.get('target_id')):r.get('ric') for r in maps}
    # Identifier use is restricted to self-exclusion; it is never an embedding feature.
    listed={r['RIC']:r.get('IssuerOAPermID') for r in load(O/'listed_universe.json')}
    alltext=[c['description'] for c in cs]+[t['text'] for t in ts]
    vec=TfidfVectorizer(stop_words='english',ngram_range=(1,2),max_features=120000,min_df=2,sublinear_tf=True)
    x=vec.fit_transform(alltext);lex=(x[len(cs):]@x[:len(cs)].T).toarray()
    ce=encode([c['description'] for c in cs],'candidate_embedding');te=encode([t['text'] for t in ts],'target_embedding');sem=te@ce.T
    results=[]
    for i,t in enumerate(ts):
        if t['status']!='WEBSITE_EVIDENCE_DRAFT':continue
        metric=.55*sem[i]+.45*lex[i]/max(float(lex[i].max()),.00001)
        chosen=[]
        for j in np.argsort(-metric):
            c=cs[int(j)]
            if c['candidate_ric']==identity.get(t['target_id']) or (listed.get(identity.get(t['target_id'])) and c['issuer_id']==listed[identity[t['target_id']]]):continue
            if norm(c['candidate_name'])==norm(t['target_name']):continue
            if isinstance(c.get('candidate_website'),str) and t['website'] and urllib.parse.urlparse('https://'+c['candidate_website'].replace('https://','').replace('http://','')).netloc.removeprefix('www.')==urllib.parse.urlparse('https://'+t['website'].replace('https://','').replace('http://','')).netloc.removeprefix('www.'):continue
            chosen.append(dict(target_id=t['target_id'],target_name=t['target_name'],candidate_ric=c['candidate_ric'],retrieval_rank=len(chosen)+1,retrieval_semantic_cosine=round(float(sem[i,j]),5),retrieval_lexical_cosine=round(float(lex[i,j]),5),retrieval_combined=round(float(metric[j]),5)))
            if len(chosen)==40:break
        results.extend(chosen)
    save('retrieval_top25',results)
    print('Retrieval candidates',len(results),'unique',len({r['candidate_ric'] for r in results}),flush=True)
if __name__=='__main__':{'prepare':prepare,'retrieve':retrieve}[sys.argv[1]]()
