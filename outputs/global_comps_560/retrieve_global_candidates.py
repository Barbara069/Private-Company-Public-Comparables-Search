"""Lexical candidate discovery only. No final facet scores or test-label reads."""
import collections,csv,heapq,json,math,pathlib,re,urllib.parse
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'blinded'
STOP=set('the a an and or of to in for with on is are as by its it our your we you us company companies corporation incorporated inc corp group holdings limited plc ltd llc all more learn contact privacy cookie cookies policy terms login read menu search about home careers news investor investors relations copyright rights reserved business businesses solutions products services provides provide'.split())
def tok(text):return [x for x in re.findall(r'[a-z]{3,}',text.lower()) if x not in STOP]
def domain(u):
    if not u:return ''
    return urllib.parse.urlparse(u if '://' in u else 'https://'+u).netloc.lower().removeprefix('www.')
def norm(n):return ''.join(x for x in tok(n) if x not in ('holding','international'))
def main():
    targets=json.loads((OUT/'target_inputs.json').read_text())
    splits=json.loads((OUT/'split_manifest.json').read_text());split={r['target_id']:r['split'] for r in splits}
    websites=json.loads((ROOT/'web_evidence/collection.json').read_text())
    raw=json.loads((ROOT/'web_evidence/wrds_api/company_catalog_active_unverified.json').read_text())
    holdout_domains={domain(t['website']) for t in targets if split[t['target_id']]=='FINAL_HOLDOUT'}-{''}
    holdout_names={norm(t['company_name']) for t in targets if split[t['target_id']]=='FINAL_HOLDOUT'}
    docs=[];seen=set()
    for r in raw:
        if r.get('gvkey') in seen or not r.get('busdesc'):continue
        if domain(r.get('weburl')) in holdout_domains or norm(r.get('conml') or r.get('conm','')) in holdout_names:continue
        if not any(r.get(x) for x in ('priusa','prican','prirow')):continue
        seen.add(r['gvkey']);docs.append(r)
    counts=[collections.Counter(tok(r['busdesc'])) for r in docs];N=len(docs)
    inv=collections.defaultdict(list)
    for i,c in enumerate(counts):
        for word,freq in c.items():inv[word].append((i,freq))
    idf={w:math.log(1+(N-len(p)+.5)/(len(p)+.5)) for w,p in inv.items()}
    avg=sum(sum(c.values()) for c in counts)/N
    lengths=[sum(c.values()) for c in counts]
    results=[];coverage=[]
    for idx,t in enumerate(targets):
        sources=[r for r in websites if r['company_id']==t['target_id'] and r.get('text_file') and r['status']=='FETCHED_TEXT_NOT_FACT_VERIFIED']
        texts=[];links=[]
        for r in sources:
            text=pathlib.Path(r['text_file']).read_text()
            # Source allowlist is website only. Remove obvious public-market/IR lines.
            text='\n'.join(line for line in text.splitlines() if not re.search(r'investor|stock price|nasdaq|nyse|10-k|annual report|sec filing|share price|market cap',line,re.I))
            texts.append(text[:30000]);links.append(r.get('source_url',r['requested_url']))
        if t['target_id']=='IQ254957567':
            # Paraphrase of the verified company About page when direct HTTP yielded empty HTML.
            texts.append('HR payroll and spend management technology provider. Unified platform covers human resources, employee self-service, compliance, time and labor, scheduling, recruiting, onboarding, performance, compensation, learning and benefits administration. Finance products cover expense management, corporate cards, accounts payable automation, procurement and headcount planning. IT covers asset and access management. Serves small, midsize and enterprise organizations. Partners include accountants and brokers. Cloud software platform and workforce workflows.')
            links.append('https://www.paylocity.com/company/about-us/')
        if not texts:
            coverage.append(dict(target_id=t['target_id'],company_name=t['company_name'],split=split[t['target_id']],status='ABSTAIN_NO_READABLE_ALLOWED_WEBSITE',candidate_count=0));continue
        q=collections.Counter(tok(' '.join(texts)))
        for w in tok(t['company_name']):q.pop(w,None)
        # Select distinctive allowed website terms; BM25 is retrieval, never a % similarity.
        terms=sorted((w for w in q if w in idf),key=lambda w:min(q[w],4)*idf[w],reverse=True)[:60]
        scores=collections.defaultdict(float)
        for w in terms:
            for j,f in inv[w]:
                scores[j]+=idf[w]*f*2.2/(f+1.2*(.25+.75*lengths[j]/avg))
        chosen=[]
        for j,score in sorted(scores.items(),key=lambda v:v[1],reverse=True):
            r=docs[j]
            if domain(r.get('weburl'))==domain(t['website']) or norm(r.get('conml') or r.get('conm',''))==norm(t['company_name']):continue
            chosen.append((j,score))
            if len(chosen)==10:break
        for rank,(j,score) in enumerate(chosen,1):
            r=docs[j]
            results.append(dict(target_id=t['target_id'],target_name=t['company_name'],split=split[t['target_id']],retrieval_rank=rank,
                                candidate_gvkey=r['gvkey'],candidate_name=r.get('conml') or r['conm'],candidate_website=r.get('weburl'),candidate_country=r.get('loc'),candidate_sic=r.get('sic'),
                                bm25_retrieval_score=round(score,4),score_meaning='UNBOUNDED_LEXICAL_RETRIEVAL_NOT_FACET_SIMILARITY_PERCENT',
                                listing_status='NOT_YET_VERIFIED',candidate_description=r['busdesc'],source_url=r['_source_url'],
                                target_website_sources='; '.join(links),final_facet_score=None,final_comp_status='CANDIDATE_ONLY_REQUIRES_REVIEW'))
        coverage.append(dict(target_id=t['target_id'],company_name=t['company_name'],split=split[t['target_id']],status='RETRIEVAL_ONLY_NOT_FINAL_COMP_SELECTION',candidate_count=len(chosen)))
    for name,data in [('retrieved_candidates',results),('retrieval_coverage',coverage)]:
        (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False))
        with (OUT/(name+'.csv')).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    print('Catalog',N,'eligible reference records before listing verification; candidate rows',len(results),'targets with candidates',sum(r['candidate_count']>0 for r in coverage),'abstentions',sum(r['candidate_count']==0 for r in coverage))
if __name__=='__main__':main()
