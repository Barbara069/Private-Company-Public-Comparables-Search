"""Recalculate public-MCD pairs from reviewed evidence; never enrich target-side snapshots."""
from pathlib import Path
import ast,copy,gzip,hashlib,json,re,sys
import numpy as np,torch
from transformers import AutoModel,AutoTokenizer
P=Path(__file__).resolve().parent;D=P.parents[1]/'outputs/public_research_website/data';load=lambda p:json.load(gzip.open(p,'rt'));idx=load(D/'research_catalog.json.gz');key=idx['aliases']['MCD'];pp=D/(idx['groups'][key]+'.json.gz');ps=load(pp);p=ps[key];raw=json.loads((P/'downloads/latest_disclosures_20261111/MCD.json').read_text());annual=next(x for x in raw['documents'] if x['form']=='10-K')
anchors={'Restaurant format':'McDonald’s restaurants compete with international','Franchise vs company-operated economics':'The Company is primarily a franchisor','Unit format / operating footprint':'◦ Drive Thru:','Menu / cuisine / customer need':'McDonald’s menu features hamburgers','Dayparts / occasions':'McDonald’s restaurants in the U.S. and many international markets offer','Price point / value proposition':'The Company is committed to a marketing strategy','Ordering / delivery channel mix':"• D ouble Down on the 4D's:",'Geographic operating mix':'The Company franchises and owns and operates McDonald','Supply chain / menu input exposure':'The Company and its franchisees purchase food, packaging','Brand / loyalty dependence':'The Company owns or is licensed to use valuable intellectual property','Competitive positioning within QSR':'McDonald’s restaurants compete with international'}
for f in p['industry_facets']:
 f['evidence_ids']=[];f['other_evidence_ids']=[]
 if f['name'] in anchors:
  text=next((x.strip() for x in annual['text'].split('\n') if anchors[f['name']] in x and len(x.strip())<=2400),None)
  if text:
   source={'source_type':'SEC','url':annual['source_url'],'document_type':annual['form'],'document_date':annual['filing_date'],'report_period':annual['report_date'],'record_locator':annual['accession'],'retrieved_at':raw['checked_at'],'review':'RELEVANCE_REVIEWED_2026-11-12'};sid=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()[:20];eid=hashlib.sha256((sid+'\n'+text).encode()).hexdigest()[:20];p['sources'][sid]=source;p['evidence'][eid]={'text':text,'source_id':sid};f['evidence_ids']=[eid]
 f['status']='REVIEWED_RELEVANT_EXCERPT' if f['evidence_ids'] else 'UNKNOWN'
p['industry_filled']=sum(bool(f['evidence_ids']) for f in p['industry_facets'])
with gzip.open(pp,'wt') as f:json.dump(ps,f,ensure_ascii=False,separators=(',',':'))
# Read literal dictionaries without running the full historic pipeline.
def literal(path,name):
 for n in ast.parse(path.read_text()).body:
  if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in n.targets):return ast.literal_eval(n.value)
base=P.parents[1]/'outputs/global_comps_560/score_comp_draft.py';patterns=literal(base,'PATTERNS');cats=literal(base,'CATS');ns={'PATTERNS':patterns,'CATS':cats}
for n in ast.parse((P/'match_facets_v2.py').read_text()).body:
 if isinstance(n,ast.Assign) and any(isinstance(x,ast.Subscript) and isinstance(x.value,ast.Name) and x.value.id=='CATS' for x in n.targets):exec(compile(ast.Module(body=[n],type_ignores=[]),'<dictionaries>','exec'),ns)
 if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='IND_PAT' for x in n.targets):exec(compile(ast.Module(body=[n],type_ignores=[]),'<industry-dictionaries>','exec'),ns);break
ind={f:tags for f,pat,tags in ns['IND_PAT']['Restaurants']};main={f['name']:f for f in p['main_facets']};industry={f['name']:f for f in p['industry_facets']}
def candidate(row):
 f=(main if row['block']=='MAIN' else industry).get(row['facet']);quotes=[]
 for eid in (f or {}).get('evidence_ids',[]):
  q=p['evidence'][eid];s=p['sources'][q['source_id']];quotes.append({**s,'text':q['text']})
 text=' '.join(x['text'] for x in quotes);tags=(ns['CATS'].get(row['facet'],{}) if row['block']=='MAIN' else ind.get(row['facet'],{}));return {'facet':row['facet'],'block':row['block'],'module':row.get('module'),'text':text,'categories':sorted(k for k,v in tags.items() if re.search(v,text,re.I)),'evidence':quotes,'status':'REVIEWED_CANDIDATE_EVIDENCE','scope':'Global consolidated McDonald’s; dates and scope retained in each source','independently_fact_verified':False}
pairs=[];shards={}
for path in (D/'matches').glob('group_*.json.gz'):
 d=load(path);selected=[r for rs in d.values() for r in rs if r['Candidate RIC']=='MCD']
 if selected:shards[path]=d;pairs+=selected
before=hashlib.sha256(json.dumps([[r['Target ID'],[f.get('target') for f in r['Facet Details']]] for r in pairs],sort_keys=True).encode()).hexdigest()
for r in pairs:
 for f in r['Facet Details']:f['candidate']=candidate(f)
texts=sorted({v['text'] for r in pairs for f in r['Facet Details'] for v in [f.get('target'),f.get('candidate')] if v and v.get('text')});tokenizer=AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2',local_files_only=True);model=AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2',local_files_only=True);model.eval();vectors={}
with torch.no_grad():
 for text in texts:
  words=text.split();parts=[' '.join(words[j:j+180]) for j in range(0,min(len(words),600),180)];batch=tokenizer(parts,padding=True,truncation=True,max_length=256,return_tensors='pt');h=model(**batch).last_hidden_state;mask=batch['attention_mask'].unsqueeze(-1);v=(h*mask).sum(1)/mask.sum(1);v=torch.nn.functional.normalize(v,dim=1).mean(0);vectors[text]=torch.nn.functional.normalize(v,dim=0).numpy()
for r in pairs:
 ds=r['Facet Details']
 for f in ds:
  a,b=f.get('target'),f['candidate'];w=f['weight'];f['score']=f['contribution']=f['normalized_weight']=f['normalized_contribution']=None
  if not a or not a.get('text') or not b['text']:f['method']='UNKNOWN_NOT_SCORED';f['confidence']='MISSING';continue
  cosine=float(np.clip(vectors[a['text']]@vectors[b['text']],0,1));aa=set(a['categories']);bb=set(b['categories']);score=100*(.65*len(aa&bb)/len(aa|bb)+.35*cosine) if aa and bb else 100*cosine
  f['method']='65% explicit-category overlap + 35% semantic cosine' if aa and bb else 'Semantic cosine of facet-specific source passages';f['cosine']=round(cosine,5);f['score']=round(score,2);f['contribution']=round(w*score/100,4);f['rationale']='Shared categories: '+(', '.join(sorted(aa&bb)) or 'none extracted')+'. Target-only: '+(', '.join(sorted(aa-bb)) or 'none extracted')+'. Candidate-only: '+(', '.join(sorted(bb-aa)) or 'none extracted')+'. Candidate excerpt relevance reviewed; similarity remains an uncalibrated index.';f['confidence']='CANDIDATE_RELEVANCE_REVIEWED_TARGET_EXTRACTION_UNREVIEWED'
 known=[f for f in ds if f['score'] is not None and f['weight']>0];coverage=sum(f['weight'] for f in known);points=sum(f['contribution'] for f in known)
 for f in ds:
  if f['score'] is not None and coverage:f['normalized_weight']=round(100*f['weight']/coverage,4);f['normalized_contribution']=round(100*f['contribution']/coverage,4)
 r.update({'Similarity Percent':round(100*points/coverage,2) if coverage else None,'Evidence Coverage Percent':round(coverage,2),'Evidence Supported Points':round(points,2),'Missing Information Interval':[round(points,2),round(points+100-coverage,2)],'Status':'RECOMPUTED_AFTER_MCD_CANDIDATE_RELEVANCE_REVIEW; TARGET_EVIDENCE_REVIEW_PENDING','Method Version':'facet-match-v2-reviewed-MCD-2026-11-12','Candidate Evidence Review':'CORRECTED_2026-11-12','Score Meaning':'Observed-facet similarity index; same legacy target weights and target evidence retained; not calibrated or a final peer recommendation.'})
 for block,name in [('MAIN','Main Component'),('INDUSTRY','Industry Component')]:
  fs=[f for f in known if f['block']==block];den=sum(f['weight'] for f in fs);r[name]={'available_weight':round(den,4),'available_similarity':round(100*sum(f['contribution'] for f in fs)/den,2) if den else None}
 for stale in ['Prior Similarity Percent']:r.pop(stale,None)
after=hashlib.sha256(json.dumps([[r['Target ID'],[f.get('target') for f in r['Facet Details']]] for r in pairs],sort_keys=True).encode()).hexdigest();assert before==after
for path,d in shards.items():
 with gzip.open(path,'wt') as f:json.dump(d,f,ensure_ascii=False,separators=(',',':'))
# Research overlay must include reviewed legacy industry fields too.
op=D/'general_refresh_20261112/group_a.json.gz';o=load(op);o[key].update({'industry_facets':p['industry_facets'],'industry_filled':p['industry_filled'],'evidence':p['evidence'],'sources':p['sources']})
with gzip.open(op,'wt') as f:json.dump(o,f,ensure_ascii=False,separators=(',',':'))
result={'mcd_pairs_recomputed':len(pairs),'target_evidence_hash_unchanged':before==after,'model':'all-MiniLM-L6-v2; masked mean pooling; 180-word chunks; cap600words; max_length256','wendy':[{k:r[k] for k in ['Similarity Percent','Evidence Coverage Percent','Evidence Supported Points']} for r in pairs if r['Target ID']=='IQ23557'],'changed_match_shards':[str(p.relative_to(D)) for p in shards]};(P/'mcd_rescore_result_20261112.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
