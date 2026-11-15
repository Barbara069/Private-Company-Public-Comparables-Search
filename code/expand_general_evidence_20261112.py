"""Full retained-source search and multi-sentence context. Never alters blinded inputs or scores."""
from pathlib import Path
import ast,bisect,collections,csv,gzip,hashlib,json,re,sys,time
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'outputs/public_research_website/data';OUT=R/'outputs/clean_research_delivery';sys.path.insert(0,str(P));from public_facet_rules import acceptable,specificity
load=lambda p:json.load(gzip.open(p,'rt'));idx=load(D/'research_catalog.json.gz');meta=json.loads((P/'general_facet_dictionary.json').read_text());patterns={}
for n in ast.parse((R/'outputs/global_comps_560/score_comp_draft.py').read_text()).body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PATTERNS' for t in n.targets):patterns=ast.literal_eval(n.value)
patterns.update({'Customer Type':r'\bB2B\b|\bB2C\b|\bB2G\b|business.to.business|business.to.consumer|(?:customers|clients) (?:include|are|consist of)|serves? (?:businesses|consumers|government)','Customer Size':r'(?:small|medium|mid.market|large|enterprise).{0,35}(?:businesses|companies|employers|customers|clients)|(?:customers|clients).{0,35}(?:small|medium|mid.market|enterprise)'})
pat={n:re.compile(v,re.I) for n,v in patterns.items()};latest={}
for path in (P/'downloads/latest_disclosures_20261111').glob('*.json'):
 if path.name=='summary.json':continue
 q=json.loads(path.read_text());key=idx['aliases'].get(q.get('company_id'))
 if key:latest[key]=path

def good(t,name):
 if name in ['Customer Type','Customer Size']:return 40<=len(t)<=2200 and pat[name].search(t) and not re.search('cookie|privacy|may adversely|could adversely',t,re.I)
 return acceptable(t,name)
def add(p,source,text):
 sid=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()[:20];eid=hashlib.sha256((sid+'\n'+text).encode()).hexdigest()[:20];p['sources'].setdefault(sid,source);p['evidence'].setdefault(eid,{'source_id':sid,'text':text});return eid

def chunks(text):
 # Character offsets preserve exact original wording/whitespace, rather than joining fabricated sentences.
 spans=[]
 for m in re.finditer(r'[^\n]+',text):
  a,b=m.span()
  if b-a<=2200:
   if b-a>=40:spans.append((a,b))
  else:
   for x in re.finditer(r'.+?(?:[.!?](?=\s+[A-Z])|$)',m.group(),re.S):
    c,d=a+x.start(),a+x.end()
    if 40<=d-c<=2200:spans.append((c,d))
 return spans

def passage(text,spans,starts,pos):
 i=max(0,bisect.bisect_right(starts,pos)-1)
 if not spans or not spans[i][0]<=pos<spans[i][1]:return None
 a,b=spans[i]
 # Include adjacent sentences only within the same paragraph; preserve source scope and avoid headings.
 for j in range(i+1,min(i+3,len(spans))):
  c,d=spans[j]
  if '\n' in text[b:c] or d-a>2200:break
  b=d
 return text[a:b].strip()

def source_check(p,ids):
 obs=[(p['evidence'][i]['text'],p['sources'][p['evidence'][i]['source_id']]) for i in ids];types=sorted({s.get('source_type','UNKNOWN') for t,s in obs});norm={re.sub(r'\s+',' ',t).lower() for t,s in obs}
 return {'status':'NO_EVIDENCE' if not ids else 'SHARED_WORDING_NOT_INDEPENDENT' if len(ids)>1 and len(norm)==1 else 'MULTISOURCE_MEANING_REVIEW_REQUIRED' if len(ids)>1 else 'SINGLE_SOURCE_NOT_INDEPENDENTLY_CONFIRMED','source_types':types,'fact_verified':False,'scope_and_period_review_required':True}

stats=collections.Counter();coverage=[];groups=sorted(set(idx['groups'].values()));started=time.time()
for gi,name in enumerate(groups):
 path=D/(name+'.json.gz');ps=load(path)
 for key,p in ps.items():
  raw=[];overview=p.get('business_description')
  if overview and overview.get('text') and overview.get('source_id') in p['sources']:raw.append((overview['text'],p['sources'][overview['source_id']]))
  if key in latest:
   q=json.loads(latest[key].read_text())
   for doc in q.get('documents',[]):
    if doc.get('text'):raw.append((doc['text'],{'source_type':'SEC','url':doc['source_url'],'document_type':doc['form'],'document_date':doc['filing_date'],'report_period':doc['report_date'],'retrieved_at':q['checked_at'],'record_locator':'SEC accession '+doc['accession'],'identity_basis':'RETAINED_CANONICAL_CIK_LINKAGE; NOT_NEWLY_VERIFIED','text_type':'EXACT_SOURCE_SUBSTRING'}))
  raw=[(t,s,chunks(t)) for t,s in raw];raw=[(t,s,sp,[a for a,b in sp]) for t,s,sp in raw]
  for f in p['main_facets']:
   old=list(f.get('evidence_ids',[]));choices=[]
   for eid in old:
    q=p['evidence'][eid];s=p['sources'][q['source_id']];original=q['text'];expanded=original
    if not good(original,f['name']):continue
    for full,source,sp,starts in raw:
     if source.get('url')!=s.get('url'):continue
     pos=full.find(original)
     if pos<0:continue
     candidate=passage(full,sp,starts,pos)
     if candidate and original in candidate and len(candidate)>len(original) and good(candidate,f['name']):expanded=candidate;break
    if expanded!=original:stats['passages_expanded']+=1
    if good(expanded,f['name']):choices.append((3,expanded,s))
   # Fill unsupported facets and supplement fields with fewer than 2 distinct source documents.
   if not old or len({p['sources'][p['evidence'][e]['source_id']].get('url') for e in old})<2:
    for full,s,sp,starts in raw:
     n=0
     for m in pat.get(f['name'],re.compile(re.escape(f['name']),re.I)).finditer(full):
      t=passage(full,sp,starts,m.start())
      if not t or not good(t,f['name']):continue
      choices.append((specificity(t,f['name']),t,s));n+=1
      if n>=8:break
   chosen=[];seen=set();urls=set()
   choices.sort(key=lambda x:(x[2].get('document_date','') not in ['', 'UNKNOWN'],x[2].get('document_date',''),x[0]),reverse=True)
   for value,t,s in choices:
    tok=(s.get('url'),t)
    if tok in seen or s.get('url') in urls:continue
    eid=add(p,s,t);chosen.append(eid);seen.add(tok);urls.add(s.get('url'))
    if len(chosen)==3:break
   if chosen:
    if not old:stats['general_fields_newly_supported']+=1
    if chosen!=old:stats['general_fields_updated']+=1
    f['evidence_ids']=chosen;f['other_evidence_ids']=[i for i in dict.fromkeys(old+f.get('other_evidence_ids',[])) if i not in chosen];f['status']='SOURCE_EXCERPTS_RETRIEVED_NOT_FACT_VERIFIED'
   ids=f.get('evidence_ids',[]);f['cross_validation']=source_check(p,ids);f['missing_reason']=None if ids else ('No relevant passage admitted after full retained-filing search; further source collection or review is needed.' if key in latest else 'Detailed sources are limited; no relevant passage admitted from the retained company description.');stats['general_with_evidence' if ids else 'general_unknown']+=1
  p['main_filled']=sum(bool(f.get('evidence_ids')) for f in p['main_facets']);p['general_evidence_updated_at']='2026-11-12';p['verified_all_facts']=False
  coverage.append({'company_id':key,'company_name':p['name'],'is_original_target':p['is_original_target'],'main_filled':p['main_filled'],'main_total':32,'main_coverage_percent':round(p['main_filled']/32*100,2),'unknown_general_facets':'; '.join(f['name'] for f in p['main_facets'] if not f.get('evidence_ids')),'all_facts_verified':False});stats['companies']+=1
 tmp=path.with_suffix('.20261112.pending')
 with gzip.open(tmp,'wt',encoding='utf-8',compresslevel=6) as f:json.dump(ps,f,ensure_ascii=False,separators=(',',':'))
 tmp.replace(path)
 if gi%20==0:print('Companies',stats['companies'],'new fields',stats['general_fields_newly_supported'],'longer passages',stats['passages_expanded'],'seconds',round(time.time()-started),flush=True)
with (OUT/'Extraction_Completeness.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(coverage[0]));w.writeheader();w.writerows(coverage)
summary={**stats,'source_refresh':'Retained full SEC text and vendor descriptions; no new source download claimed','cross_source_semantic_review_complete':False,'restricted_target_inputs_unchanged':True,'score_recomputed':False};(P/'expansion_summary_20261112.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
