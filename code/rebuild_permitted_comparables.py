"""Fresh global retrieval and evidence-linked provisional scoring from permitted data only.
No retired candidates, categories, vectors, SIC joins or outcome labels are read.
"""
from pathlib import Path
import argparse,collections,csv,gzip,hashlib,json,os,re,sys,time
import numpy as np
from source_policy import restricted,require_allowed
from public_facet_rules import acceptable,specificity
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'website/data';P=ROOT/'code'
VERSION='permitted-evidence-v3.2-2026-11-15'
CONFIG=json.loads((P/'matching_rules.json').read_text());POLICY=json.loads((P/'scoring_policy_v3.json').read_text())
GENERAL=POLICY['general_weights'];INDUSTRY={m['code']:m for m in POLICY['industry_modules']}
BAN=re.compile(r'cookie (?:policy|settings|consent)|we use cookies|privacy policy|copyright|all rights reserved|forward.looking statements|accounting (?:standard|guidance|policies)|FASB|\bASU\s+(?:No\.?\s*)?20\d{2}|software development stages|capitalization of software costs|internal.use software|fair value|deferred tax|repurchase|stock.based compensation|share.based compensation|pension|subsequent events|unaudited condensed|rights agreement|securities exchange act|indicate by check mark|vote your proxy|terms of use|access denied|captcha|enable javascript',re.I)
CONDITIONAL=re.compile(r'\bmay\b|\bcould\b|risk factor|would adversely|if we fail|cannot assure',re.I)
COMPETITOR=re.compile(r'\b(?:ADP|Paycom|Dayforce|Deel|UKG|Workday|McDonald.s|Burger King|Wendy.s|Paylocity)\b',re.I)
GENERIC=set('company companies business businesses model type category operating operations profile structure system services service product products provision information other customer customers general including primary activity activities example examples year years monthly million billion total revenue revenues percentage percent number unit units growth margin rate ratio yield change volume frequency intensity amount exposure capacity value revenue sales'.split())
def load(p):return json.load(gzip.open(p,'rt')) if p.suffix=='.gz' else json.loads(p.read_text())
def save(p,d):
 require_allowed(d);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode(),compresslevel=6,mtime=0))
def hash_obj(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def tokens(t):return set(re.findall(r'[a-z][a-z0-9-]{2,}',t.lower()))
def clean_quote(q,target=False,target_name='',target_website=''):
 text=re.sub(r'\s+',' ',q.get('text','')).strip();url=q.get('url') or q.get('source_url') or ''
 if not text or not url.startswith(('https://','http://')) or restricted(q):return None
 if target:
  from urllib.parse import urlsplit
  h=(urlsplit(url).hostname or '').lower()
  normalized=h.removeprefix('www.')
  base=(urlsplit(target_website if target_website.startswith('http') else 'https://'+target_website).hostname or '').lower().removeprefix('www.')
  if base and not (normalized==base or normalized.endswith('.'+base)):return None
  if any(normalized==x or normalized.endswith('.'+x) for x in ['sec.gov','lseg.com','capitaliq.com','marketscreener.com','finance.yahoo.com']):return None
  if q.get('source_type')!='OFFICIAL_WEBSITE' or h.startswith(('ir.','investor.','investors.')):return None
  if re.search(r'/investor|/annual.report|/quarterly|/sec.filing|/earnings|/financial.results|/10-[kq]',url,re.I):return None
  if q.get('document_type') in ['10-K','10-Q','20-F','8-K','ANNUAL_REPORT','EARNINGS_RELEASE','EARNINGS_CALL']:return None
  # A comparison table about competitors is not the target's operating evidence.
  if re.search(r'View all.{0,300}View all|Request a Demo.{0,100}Request a Demo',text,re.I):return None
  if text.count('|')>=2 or (len(set(COMPETITOR.findall(text)))>=2 and re.search(r'compare|custom|versus|alternative|pricing|\$|employee/month',text,re.I)):return None
  if re.search(r'\bas a franchisee\b',text,re.I) and re.search(r'global restaurant brand|quick.service restaurant industry',text,re.I):
   return {**q,'text':text,'url':url,'scope_restriction':'INDUSTRY_FORMAT_ONLY'}
  if re.search(r'\b(?:your|you will|you.ll|you can|as a franchisee|job applicant|job requirements|we.re hiring)\b',text,re.I):return None
 return {**q,'text':text,'url':url}
def passages(quotes):
 seen=set()
 for q in quotes:
  for s in re.split(r'\n+|(?<=[.!?;])\s+(?=[A-Z“])',q['text']):
   s=s.strip()
   if not 40<=len(s)<=1800 or s in seen or BAN.search(s) or CONDITIONAL.search(s):continue
   seen.add(s);yield {**q,'text':s}
def categories(name,text):
 return sorted(k for k,p in CONFIG['CATS'].get(name,{}).items() if re.search(p,text,re.I))
def extract(name,qs,block='MAIN',pattern=None,tags=None):
 pattern=pattern or CONFIG['PATTERNS'].get(name,r'(?!)');matches=[]
 for q in qs:
  t=q['text']
  if q.get('scope_restriction')=='INDUSTRY_FORMAT_ONLY' and not re.search(r'restaurant.*format',name,re.I):continue
  if name!='Company Maturity' and re.search(r'formerly|historically|opened (?:its|the) first|was founded|was incorporated|in 19[0-9]{2}',t,re.I) and not re.search(r'currently|today|continues? to',t,re.I):continue
  structured=name in ['Customer Size','Customer Type'] and q.get('data_kind')=='STRUCTURED_CUSTOMER_SIZE_GRID'
  own_claim=name=='Core Business Activity' and re.search(r'\bwe[’\']re\b.{0,100}(?:provider|manufacturer|operator)',t,re.I)
  if not (re.search(pattern,t,re.I) or structured) or not (acceptable(t,name,block) or structured or own_claim):continue
  rank=specificity(t,name)+min(5,len(re.findall(pattern,t,re.I)))
  if q.get('source_type')=='SEC':rank+=1
  matches.append((rank,q))
 matches.sort(key=lambda x:(-x[0],-int(re.sub(r'\D','',x[1].get('document_date',''))[:8] or '0'),len(x[1]['text'])))
 chosen=[];families=set();seen=set()
 for diversity in [True,False]:
  for _,q in matches:
   if q['text'] in seen:continue
   family=q.get('source_type','UNKNOWN')
   if diversity and family in families:continue
   seen.add(q['text']);families.add(family);chosen.append(q)
   if len(chosen)==3:break
  if len(chosen)==3:break
 text=' '.join(q['text'] for q in chosen)
 cats=categories(name,text) if tags is None else sorted(k for k,p in tags.items() if re.search(p,text,re.I))
 if any(q.get('data_kind')=='STRUCTURED_CUSTOMER_SIZE_GRID' for q in chosen):
  if name=='Customer Type':cats=['B2B']
  elif name=='Customer Size':cats=['SMB','mid-market','enterprise']
 return {'facet':name,'text':text,'categories':cats,'evidence':chosen,'status':'AUTOMATED_PERMITTED_SOURCE_EXTRACTION_REQUIRES_REVIEW' if chosen else 'UNKNOWN_NO_RELEVANT_EVIDENCE','fact_verified':False}
def main_fields(qs):return {f['name']:extract(f['name'],qs) for f in GENERAL}
# SIC-like checklist routing is an analyst inference from website operations, never a hidden target code.
ROUTES=[
 ('58',r'quick.service|fast.casual|restaurant|hamburger|dining',r'operat|franchis|restaurant|menu'),
 ('73',r'software|payroll|human capital|cybersecurity|advertising|staffing|outsourcing|data processing',r'provid|offer|develop|platform|solutions|software|services'),
 ('80',r'hospital|patient care|healthcare services|health care services|home.health|medical care|clinical services',r'operat|provid|patient|clinic|care'),
 ('28',r'pharmaceutical|therapeutic|biotech|drug development|specialty chemicals|chemical manufactur',r'develop|manufactur|produc|commercial|drugs|chemicals'),
 ('38',r'medical devices|diagnostic equipment|surgical instruments|laboratory instruments|measurement instruments',r'design|manufactur|develop|products|devices'),
 ('63',r'insurance|reinsurance|annuities',r'underwrit|insur|premiums|reinsur'),('60',r'commercial bank|banking|bank services|deposits and loans',r'bank|lend|loans|deposit'),
 ('62',r'asset management|investment management|wealth management|brokerage|securities brokerage',r'manag|advis|broker|investment'),
 ('65',r'property management|real estate brokerage|owns.{0,50}(?:properties|real estate)|shopping centers|real estate',r'own|operat|manag|develop|broker|lease'),
 ('67',r'REIT|real estate investment trust|investment holding|closed.end fund',r'owns|invest|hold|fund'),
 ('35',r'industrial equipment|machinery|HVAC|air.conditioning|engines|pumps|compressors|machine tools',r'manufactur|design|engineer|produc|equipment'),
 ('36',r'semiconductor|electronic components|electrical equipment|electronic products|batteries|electronic manufacturing',r'manufactur|design|develop|produc'),
 ('37',r'aircraft|aerospace|motor vehicles|boats|automotive components|automobiles',r'manufactur|design|produc|supplier'),
 ('34',r'fabricated metal|metal products|steel fabrication|metal containers',r'manufactur|fabricat|produc'),
 ('33',r'steel|aluminum|aluminium|primary metals|copper',r'manufactur|produc|smelt|refin'),
 ('20',r'food products|beverages|brewing|brewery|snacks|dairy|meat processing|bottling',r'manufactur|produc|process|brewer|bottl'),
 ('23',r'apparel|garments|clothing|footwear',r'manufactur|design|produc'),
 ('26',r'paper products|pulp|packaging paper',r'manufactur|produc|process'),
 ('30',r'rubber|plastic products|plastic packaging',r'manufactur|produc'),
 ('32',r'cement|glass|concrete products|aggregates|ceramics',r'manufactur|produc|quarr'),
 ('49',r'electric utility|electricity|natural.gas utility|water utility|regulated utilities|waste management',r'generat|distribut|utility|utilities|water|waste'),
 ('13',r'oil and gas|crude oil|natural gas',r'explor|drill|produc|upstream'),('29',r'petroleum refining|refinery|refineries|refined petroleum',r'refin|produc'),
 ('10',r'copper mining|gold mining|metal mining|iron ore|silver mining',r'min(?:e|es|ing)|explor|extract'),
 ('12',r'coal mining|coal producer',r'min(?:e|es|ing)|produc'),
 ('15',r'homebuilding|homebuilder|residential construction|commercial building construction',r'construct|build|develop'),
 ('16',r'road construction|highway construction|infrastructure construction|heavy construction|civil construction',r'construct|build|contract'),
 ('17',r'electrical contracting|mechanical contracting|specialty contractor|plumbing|installation services',r'contract|install|provid'),
 ('40',r'railroad|rail transportation',r'operat|transport|rail'),('42',r'trucking|truckload|less.than.truckload|warehousing',r'provid|transport|operat'),
 ('44',r'marine shipping|ocean shipping|shipping vessels|maritime transportation',r'operat|ship|transport'),
 ('45',r'airline|air transportation|air cargo',r'operat|transport|airline'),('47',r'freight forwarding|logistics services|transportation logistics',r'provid|logistics|forward'),
 ('48',r'telecommunications|broadband|wireless communications|television broadcasting|radio broadcasting',r'provid|operat|network|broadcast'),
 ('27',r'publishing|newspapers|book publishing|magazines',r'publish|produc|distribut'),('78',r'film production|motion pictures|movie studios',r'produc|distribut|studio'),
 ('79',r'casino|gaming|theme parks|sports entertainment|motor racing|recreational facilities',r'operat|own|entertain|gaming'),
 ('70',r'hotels|lodging|resort|hospitality',r'operat|manag|franchis|own'),('82',r'education|college|university|online learning|training programs',r'provid|operat|education|training'),
 ('87',r'engineering services|environmental consulting|scientific consulting|testing services',r'provid|consult|engineering'),
 ('50',r'industrial distribution|equipment distributor|wholesale distribution|distributes.{0,40}(?:industrial|electronic|equipment)',r'distribut|wholesale'),
 ('51',r'foodservice distributor|wholesale food|chemical distributor|fuel distribution',r'distribut|wholesale'),
 ('53',r'department stores|general merchandise|discount stores|warehouse clubs',r'retail|operat|store'),
 ('54',r'grocery|supermarkets|convenience stores',r'retail|operat|store'),('56',r'apparel|footwear|clothing',r'retail|operat|stores|sells'),
 ('57',r'home furnishings|furniture retail|electronics retail',r'retail|operat|stores'),('59',r'retail|e.commerce|online marketplace|specialty stores',r'retail|operat|store|sells|marketplace')]

def route(fs):
 text=' '.join(fs[n]['text'] for n in ['Primary Products','Primary Services','Core Business Activity','Business Model'] if fs.get(n))
 scored=[]
 for code,pat,op in ROUTES:
  a=len(re.findall(pat,text,re.I));b=bool(re.search(op,text,re.I))
  if a and b:scored.append((a,code))
 # Explicit own-business software/HCM claims override merely served customer verticals.
 if re.search(r'(?:payroll|human capital|HR|cybersecurity).{0,60}(?:software|platform|solutions)|(?:provides?|offers?).{0,60}(?:software|cloud.based)',text,re.I):scored=[(a+100 if c=='73' else a,c) for a,c in scored]
 if re.search(r'quick.service restaurant|restaurant (?:chain|company)|operating.{0,50}franchising|menu.{0,60}(?:hamburger|sandwich|pizza)',text,re.I):scored=[(a+100 if c=='58' else a,c) for a,c in scored]
 scored.sort(reverse=True);codes=[c for a,c in scored if c in INDUSTRY and not INDUSTRY[c].get('reference_only')]
 return {'primary_code':codes[0] if codes else None,'additional_activity_hypotheses':codes[1:3],'basis':'Rule-based analyst checklist inference from permitted own-business passages; not a vendor-assigned SIC. Additional activities do not imply known segment revenue weights.'}

FIELD_MAP={'01':'Software Category','02':'Deployment Model','03':'Pricing Metric','04':'Contract Duration','05':'Revenue Composition','06':'Implementation Complexity','07':'Customer Retention Model','08':'Deployment Model','09':'Software Category'}
def industry_specs(code):
 if not code:return []
 out=[]
 for field in INDUSTRY[code]['fields']:
  if not field.get('importance_points') or field.get('diagnostic_only'):continue
  name=field['name'];pat=None;tags={}
  if code=='58':
   mapping={'01':'Restaurant format','02':'Franchise vs company-operated economics','07':'Menu / cuisine / customer need','08':'Ordering / delivery channel mix'}
   old=next((x for x in CONFIG['IND_PAT']['Restaurants'] if x[0]==mapping.get(field['id'].split('-')[-1])),None)
   if old:_,pat,tags=old
   if field['id']=='I58-02':pat+='|master franchisee|sub.licenses?|pays royalties|franchisor|receives royalties'
  elif code=='73':
   if field['id'].endswith('-04'):
    pat=CONFIG['PATTERNS']['Contract Duration'];tags={}
   old=next((x for x in CONFIG['IND_PAT']['Technology / SaaS'] if x[0]==FIELD_MAP.get(field['id'].split('-')[-1])),None)
   if old and not field['id'].endswith('-04'):_,pat,tags=old
  if code=='73' and field.get('conditional_extension'):
   activation={'09':r'payroll|human capital|human resources|software|SaaS','10':r'net (?:revenue|dollar) retention','11':r'annual recurring revenue|\bARR\b','12':r'transaction processing|payment processing|data processing','13':r'(?:provid|offer|staffing|placement).{0,70}(?:staffing|recruitment|placement services)|staffing services','14':r'temporary staffing|temporary workers|staffing hours','15':r'permanent placement|placement fees','16':r'bill.rate|pay.rate|bill.pay spread','17':r'advertising (?:agency|services)|media buying|advertising retainer','18':r'janitorial|building maintenance|security guard|protective services','19':r'equipment rental|rental fleet'}
   pat=activation.get(field['id'].split('-')[-1],r'(?!)');tags={}
  if not pat:
   terms=sorted((tokens(name+' '+' '.join(field.get('examples',[])))-GENERIC))
   terms=[t for t in terms if not any(x.isdigit() for x in t) and len(t)>3]
   pat='|'.join(re.escape(t) for t in terms[:35]) or r'(?!)'
  out.append({**field,'pattern':pat,'tags':tags})
 return out

def standard_fields(code,qs,target=False):
 fields=[]
 for f in industry_specs(code):
  # Conditional fields require a concrete operational subtype cue on the target.
  v=extract(f['name'],qs,'INDUSTRY',f['pattern'],f['tags'])
  if target and f.get('conditional_extension') and not v['text']:continue
  fields.append({**v,'standard_id':f['id'],'module_code':code,'importance_points':f['importance_points'],'conditional_extension':f.get('conditional_extension',False)})
 if target:
  seen={}
  for f in fields:
   if f['text'] and f['text'] in seen:
    f['importance_points']=0;f['duplicate_of_standard_id']=seen[f['text']]
   elif f['text']:seen[f['text']]=f['standard_id']
 return fields

def public_quotes(p):
 qs=[];b=p.get('business_description')
 if b and b.get('source_id') in p['sources']:qs.append({**p['sources'][b['source_id']],'text':b['text']})
 for e in p.get('evidence',{}).values():
  if e.get('source_id') not in p['sources']:continue
  s=p['sources'][e['source_id']]
  if s.get('text_type')=='STRUCTURED_API_FIELD':continue
  qs.append({**s,'text':e.get('text','')})
 clean=[x for q in qs if (x:=clean_quote(q))]
 return list(passages(clean))
def overview(p):
 b=p.get('business_description')
 if b and b.get('source_id') in p.get('sources',{}) and not BAN.search(b['text']) and len(b['text'])>=80:
  s=p['sources'][b['source_id']];return b['text'][:4500],s
 qs=public_quotes(p);a=extract('Core Business Activity',qs)
 if a['evidence']:return a['text'][:4500],a['evidence'][0]
 return None,None

def embed(texts,cache_dir,label):
 from sentence_transformers import SentenceTransformer
 import torch
 torch.set_num_threads(4)
 key=hash_obj({'model':'all-MiniLM-L6-v2','max_tokens':192,'texts':texts});path=cache_dir/(label+'_'+key[:16]+'.npy')
 if path.exists():
  path.with_suffix('.texts.json').write_text(json.dumps(texts,ensure_ascii=False))
  return np.load(path)
 # Reuse only exact-text embeddings produced by this permitted-source rebuild,
 # with the same model and token settings; never load retired mixed-source vectors.
 needed=set(texts);reused={}
 for meta in sorted(cache_dir.glob(label+'_*.texts.json')):
  source=meta.with_name(meta.name.replace('.texts.json','.npy'))
  if not source.exists():continue
  previous=json.loads(meta.read_text());array=np.load(source,mmap_mode='r')
  for i,t in enumerate(previous):
   if t in needed and t not in reused:reused[t]=np.array(array[i],copy=True)
 missing=[t for t in texts if t not in reused]
 print(label,'exact permitted-text cache reuse',len(reused),'new passages',len(missing),flush=True)
 if missing:
  model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2',device='cpu',local_files_only=True);model.max_seq_length=192
  for a in range(0,len(missing),1500):
   vectors=model.encode(missing[a:a+1500],batch_size=96,normalize_embeddings=True,show_progress_bar=False)
   reused.update(zip(missing[a:a+1500],vectors));print(label,'embedded',min(a+1500,len(missing)),'/',len(missing),flush=True)
 v=np.stack([reused[t] for t in texts]);np.save(path,v);path.with_suffix('.texts.json').write_text(json.dumps(texts,ensure_ascii=False));return v

def compare(a,b,weight,vecs):
 row={'facet':a['facet'],'target':a,'candidate':b,'weight':round(weight,6),'score':None,'contribution':None,'method':'UNKNOWN_NOT_SCORED','rationale':'No eligible passage on one or both sides; missing evidence is not zero similarity.','confidence':'MISSING'}
 if not a['text'] or not b['text']:return row
 cosine=float(np.clip(vecs[a['text']]@vecs[b['text']],0,1));aa=set(a.get('categories',[]));bb=set(b.get('categories',[]));shared=sorted(aa&bb)
 if len(aa)>1:aa.discard('software')
 if len(bb)>1:bb.discard('software')
 s=100*(.65*len(aa&bb)/min(len(aa),len(bb))+.35*cosine) if aa and bb else 100*cosine
 reason='Shared explicit categories: '+(', '.join(shared) if shared else 'none extracted on both sides')+'. Text differences are not independently verified business differences.'
 # Regional master franchisees have a different role from a brand's franchisor.
 ta=a['text'];tb=b['text']
 if re.search(r'franchise|operating model|ownership|Business Model',a['facet'],re.I):
  master=lambda t:bool(re.search(r'master franchisee|master licensee|exclusive.{0,35}franchisee|pays royalties|sub.licenses|sub.licens',t,re.I))
  franchisor=lambda t:bool(re.search(r'franchisor|franchises? (?:its |the )?restaurants|franchising|franchise owners|global restaurant brand|our franchisees',t,re.I))
  if master(tb) and franchisor(ta) and not master(ta):s=min(s,35);reason+=' Master-franchisee versus brand-franchisor operating roles differ; score capped at 35.'
 if a['facet'].lower().startswith('restaurant format') and 'QSR' in aa and bb and 'QSR' not in bb:s=min(s,25);reason+=' Quick-service versus explicitly different restaurant format; cap 25.'
 row.update(score=round(s,2),contribution=round(weight*s/100,6),cosine=round(cosine,6),method='65% explicit-category overlap coefficient + 35% passage cosine' if aa and bb else 'Facet-specific passage cosine; category mapping unavailable',rationale=reason,confidence='AUTOMATED_NOT_FACT_VERIFIED')
 return row

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--cache',default=str(ROOT.parent/'cache'));parser.add_argument('--pilot',action='store_true');args=parser.parse_args();cache=Path(args.cache);cache.mkdir(parents=True,exist_ok=True)
 idx=load(D/'research_catalog.json.gz');inputs=load(D/'comparison_inputs.json.gz');require_allowed(inputs);input_hash=hash_obj(inputs)
 targets={};stats=collections.Counter();catalog={c['key']:c for c in idx['companies']}
 for tid,p in inputs.items():
  if args.pilot and tid not in ['IQ23557','IQ254957567']:continue
  qs=[x for q in p['website_quotes'] if (x:=clean_quote(q,True,p['target_name'],p['website']))];qs=list(passages(qs));fs=main_fields(qs);routing=route(fs);code=routing['primary_code'];ind=standard_fields(code,qs,True)
  targets[tid]={'input':p,'quotes':qs,'main':fs,'routing':routing,'industry':ind,'own_key':idx['aliases'].get(tid)}
 stats['targets']=len(targets);print('Target-only bundles extracted',len(targets),flush=True)
 # Load only independently retained public descriptions for the global retrieval stage.
 refs=[]
 for group in sorted(set(idx['groups'].values())):
  for key,p in load(D/(group+'.json.gz')).items():
   c=catalog[key]
   if any(x.endswith('.PK') for x in c.get('rics',[])):continue
   if not c.get('rics') or not (c.get('is_listed_registry') or c.get('is_original_target')):continue
   text,source=overview(p)
   if text:
    refs.append({'key':key,'name':p['name'],'rics':p['rics'],'issuer_ids':p.get('legal_issuer_ids',[]),'text':text,'source':source,'group':group,'listing_status':p.get('listing_status','UNKNOWN')})
 print('Permitted-description global candidate profiles',len(refs),flush=True);stats['retrieval_universe']=len(refs)
 texts=[r['text'][:2400] for r in refs];tids=list(targets)
 ttexts=[' '.join(q['text'] for q in targets[tid]['quotes'])[:6500] or 'Unknown business' for tid in tids]
 cv=embed(texts,cache,'candidate_descriptions');tv=embed(ttexts,cache,'target_websites')
 from sklearn.feature_extraction.text import TfidfVectorizer
 tf=TfidfVectorizer(stop_words='english',ngram_range=(1,2),max_features=130000,min_df=2,sublinear_tf=True)
 # The original target companies' unrestricted profiles must not fit the lexical model.
 fit_texts=[r['text'][:2400] for r in refs if not catalog[r['key']].get('is_original_target')]
 tf.fit(fit_texts);cm=tf.transform(texts);tm=tf.transform(ttexts);lex=(tm@cm.T).toarray();sem=tv@cv.T
 pools={};wanted=collections.defaultdict(set)
 for i,tid in enumerate(tids):
  t=targets[tid]
  own_ids=set(next((r['issuer_ids'] for r in refs if r['key']==t['own_key']),[]))
  allowed=[j for j,r in enumerate(refs) if r['key']!=t['own_key'] and not (own_ids & set(r['issuer_ids']))]
  denom=max(float(lex[i,allowed].max()),1e-8) if allowed else 1
  metric=.70*sem[i]+.30*lex[i]/denom;selected=[];selected_issuers=set()
  if len(t['quotes'])<1:pools[tid]=[];continue
  for j in np.argsort(-metric):
   r=refs[int(j)]
   if r['key']==t['own_key'] or (own_ids & set(r['issuer_ids'])):continue
   if set(r['issuer_ids']) & selected_issuers:continue
   # Exclusion-only identity metadata is not fed into embeddings or facet weights.
   if t['own_key'] and set(r['rics'])&set(catalog[t['own_key']].get('rics',[])):continue
   if t['routing']['primary_code']=='58' and not (re.search(r'restaurant|dining',r['text'],re.I) and re.search(r'operat|franchis|restaurant chain',r['text'],re.I)):continue
   if t['routing']['primary_code']=='73' and re.search(r'payroll|human capital|workforce|human resources',ttexts[i],re.I):
    if not re.search(r'(?:payroll|human capital|human resources|workforce management).{0,100}(?:software|platform|solutions|services)|(?:software|platform|solutions).{0,100}(?:payroll|human capital|human resources|workforce management)',r['text'],re.I):continue
   selected.append((int(j),float(metric[j])));selected_issuers.update(r['issuer_ids']);wanted[r['group']].add(r['key'])
   if len(selected)==60:break
  pools[tid]=selected
 stats['retrieved_pairs']=sum(map(len,pools.values()));print('Retrieved pairs',stats['retrieved_pairs'],flush=True)
 pub={};needed_codes=collections.defaultdict(set)
 for tid,rs in pools.items():
  for j,_ in rs:needed_codes[refs[j]['key']].add(targets[tid]['routing']['primary_code'])
 for group,keys in wanted.items():
  for key,p in load(D/(group+'.json.gz')).items():
   if key not in keys:continue
   qs=public_quotes(p);pub[key]={'main':main_fields(qs),'industry':{code:{x['standard_id']:x for x in standard_fields(code,qs)} for code in needed_codes[key] if code},'quotes':qs}
 print('Selected public profiles re-extracted',len(pub),flush=True)
 unique=set()
 for t in targets.values():
  unique.update(x['text'] for x in list(t['main'].values())+t['industry'] if x['text'])
 for p in pub.values():
  unique.update(x['text'] for x in p['main'].values() if x['text'])
  for fs in p['industry'].values():unique.update(x['text'] for x in fs.values() if x['text'])
 strings=sorted(unique);vectors=embed(strings,cache,'paired_facets');vecs={s:v for s,v in zip(strings,vectors)};output={};summaries=[];pool_audit={}
 for tid,t in targets.items():
  rs=[];code=t['routing']['primary_code'];ind=t['industry'];base={f['name']:f['weight_percent'] for f in GENERAL};base['Company Size Category']=0
  # Freeze duplicate-fact exclusions from the TARGET, never from candidate missingness.
  duplicate_general={}
  for f in ind:
   if not f['text']:continue
   for name,g in t['main'].items():
    if g['text'] and f['text']==g['text'] and re.search(r'product|menu|operating model|business model|revenue model|pricing|deployment',f['facet'],re.I):
     duplicate_general[name]=f['standard_id'];base[name]=0
  den=sum(base.values());base={k:60*w/den for k,w in base.items()};inden=sum(x['importance_points'] for x in ind) or 1
  for j,retrieval in pools[tid]:
   r=refs[j];p=pub[r['key']];rows=[]
   for name,w in base.items():
    rows.append({'block':'MAIN','duplicate_of_industry':duplicate_general.get(name),**compare(t['main'][name],p['main'][name],w,vecs)})
   for f in ind:
    b=p['industry'][code].get(f['standard_id'],{'facet':f['facet'],'text':'','categories':[],'evidence':[]})
    rows.append({'block':'INDUSTRY','standard_id':f['standard_id'],'module_code':code,**compare(f,b,40*f['importance_points']/inden,vecs)})
   observed=[x for x in rows if x['score'] is not None and x['weight']>0];coverage=sum(x['weight'] for x in observed);support=sum(x['contribution'] for x in observed);similarity=100*support/coverage if coverage else None
   # Minimum explicit offering evidence prevents generic industry boilerplate from ranking alone.
   offering=[x for x in rows if x['score'] is not None and (x['facet'] in ['Primary Products','Primary Services'] or x.get('standard_id') in ['I58-01','I58-07','I73-01','I73-09'])]
   if not offering or max(x['score'] for x in offering)<25:continue
   if coverage<15:continue
   for x in rows:x['normalized_contribution']=round((x['contribution'] or 0)*100/coverage,4) if coverage and x['score'] is not None else None
   rs.append({'Target ID':tid,'Target Name':t['input']['target_name'],'Candidate RIC':r['rics'][0],'Candidate RIC Aliases':r['rics'],'Candidate Name':r['name'],'Canonical Company ID':r['key'],'Candidate Issuer ID':','.join(r['issuer_ids']),'Candidate Description':r['text'],'Candidate Source':r['source'].get('source_type','UNKNOWN'),'Candidate Source URL':r['source']['url'],'Candidate Record Locator':r['source'].get('record_locator',''),'Candidate Source Date':r['source'].get('document_date','UNKNOWN'),'Ranking Score':round(similarity*(.5+.5*min(1,coverage/60)),2),'Similarity Percent':round(similarity,2),'Evidence Coverage Percent':round(coverage,2),'Evidence Supported Points':round(support,2),'Missing Information Interval':[round(support,2),round(support+100-coverage,2)],'Main Component':{'available_weight':round(sum(x['weight'] for x in observed if x['block']=='MAIN'),2)},'Industry Component':{'available_weight':round(sum(x['weight'] for x in observed if x['block']=='INDUSTRY'),2)},'Target Industry Module':INDUSTRY[code]['title'] if code else 'UNKNOWN','Target Industry Code Hypothesis':code,'Industry Inference':t['routing']['basis'],'Additional Activity Hypotheses':t['routing']['additional_activity_hypotheses'],'Facet Details':rows,'Retrieval Index':round(retrieval,6),'Status':'PERMITTED_SOURCE_PROVISIONAL_AUTOMATED_REVIEW_REQUIRED','Method Version':VERSION,'Final Ranking Eligible':False,'Segment Mix Status':'Website-only activity routing; no hidden segment shares and no invented equal segment weights. Primary activity comparison; full multi-segment aggregate is not claimed.','Listing Status':r['listing_status'],'Universe Listing Snapshot':'2026-10-28 retained reference; not independently refreshed','Target Input Hash':hash_obj(t['input']),'Source Policy':'PERMITTED_SOURCES_ONLY','Main Weight Percent':60,'Industry Weight Percent':40,'Financial Inputs Used For Retrieval':False})
  rs.sort(key=lambda x:(-x['Ranking Score'],-x['Similarity Percent'],-x['Evidence Coverage Percent'],-x['Evidence Supported Points'],x['Candidate Name']))
  pool_audit[tid]=[{k:r[k] for k in ['Candidate RIC','Candidate Name','Ranking Score','Similarity Percent','Evidence Coverage Percent']} for r in rs]
  rs=rs[:10]
  for rank,r in enumerate(rs,1):r['Candidate Order']=rank;r['Rank']=rank
  output[tid]=rs;summaries.append({'target_id':tid,'target_name':t['input']['target_name'],'candidate_count':len(rs),'status':'PROVISIONAL_SCORED_CANDIDATES' if rs else 'ABSTAIN_INSUFFICIENT_ALLOWED_EVIDENCE','website_passages_admitted':len(t['quotes']),'industry_code_hypothesis':code,'general_fields_with_evidence':sum(bool(f['text']) for f in t['main'].values()),'industry_fields_with_evidence':sum(bool(f['text']) for f in ind)})
 prefix='pilot_' if args.pilot else '';save(cache/(prefix+'matches.json.gz'),output);save(cache/(prefix+'target_matching_facets.json.gz'),{k:{'general':v['main'],'industry':v['industry'],'routing':v['routing']} for k,v in targets.items()})
 save(cache/(prefix+'pool_diagnostics.json.gz'),pool_audit)
 stats['targets_with_scores']=sum(bool(v) for v in output.values());stats['scored_candidates']=sum(map(len,output.values()));stats['targets_abstaining']=len(targets)-stats['targets_with_scores'];stats['public_profiles_reextracted']=len(pub);stats['unique_permitted_facet_texts_embedded']=len(strings)
 manifest={'version':VERSION,'as_of':'2026-11-15','target_input_hash':input_hash,'input_files':['website/data/comparison_inputs.json.gz','website/data/research_catalog.json.gz','website/data/research/profiles_*.json.gz'],'stats':dict(stats),'targets':summaries,'method':'New pretrained passage embeddings + independently authored explicit categories; no old scores, vectors, SIC joins or candidates reused.','calibration':'UNVALIDATED_RESEARCH_INDEX_NOT_PROBABILITY','ranking_score':'S × (0.5 + 0.5 × min(1, C/60)); provisional evidence-reliability adjustment, not a business difference or calibrated probability','general_share':60,'industry_share':40,'multi_segment_status':'PRIMARY_ACTIVITY_ONLY; ADDITIONAL_ACTIVITIES_AND_UNKNOWN_MIX_DISCLOSED','target_sic_policy':'WEBSITE_INFERRED_HYPOTHESIS_NOT_HIDDEN_VENDOR_SIC'}
 (cache/(prefix+'rebuild_manifest.json')).write_text(json.dumps(manifest,indent=2));print(json.dumps(dict(stats)),flush=True)
 for tid in ['IQ23557','IQ254957567']:
  if tid in output:print(tid,[(r['Candidate RIC'],r['Candidate Name'],r['Similarity Percent'],r['Evidence Coverage Percent']) for r in output[tid]],flush=True)
 assert hash_obj(load(D/'comparison_inputs.json.gz'))==input_hash

if __name__=='__main__':main()
