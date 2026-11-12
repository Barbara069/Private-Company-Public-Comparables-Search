"""Conservative segment enumeration and source-scoped industry mapping."""
import re,collections
NUM={'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,'single':1}
GEO=re.compile(r'^(?:the )?(?:north america|south america|latin america|americas|europe|greater china|china|japan|international|domestic|united states|u\.?s\.?|asia(?: pacific)?|rest of asia pacific|emea|apac|australia|canada|middle east(?: and africa)?|europe,? middle east and africa|africa|india|united kingdom|rest of (?:the )?world)(?:\s*\([A-Z& ]+\))?$',re.I)
RULES=[('Insurance / reinsurance',r'insurance|reinsurance|underwriting'),('Banking / lending / payments',r'banking|bank\b|lending|credit card|payments'),('Asset / wealth management',r'asset.{0,8}management|wealth|investment management'),('Rail transportation',r'railroad|railway|\bbnsf\b|burlington northern'),('Energy / utilities',r'energy|electricity|power generation|utilities|natural gas'),('Property leasing / development',r'real estate|property (?:leasing|development)|reit'),('Restaurant operations / franchising',r'restaurant|\bqsr\b|franchis'),('Food / snacks',r'\bfoods?\b|snacks|confectionery'),('Beverages',r'beverage|bottling|soft drinks|juices'),('Semiconductors / accelerated computing',r'compute\s*&?\s*networking|graphics|semiconductor|\bgpu\b|accelerated computing'),('Cloud infrastructure / platform services',r'\baws\b|amazon web services|intelligent cloud|cloud infrastructure|cloud computing|\bazure\b'),('Software / business applications',r'productivity and business processes|\bhcm\b|human capital|payroll|software|\bsaas\b'),('Media / sports content',r'entertainment|\bespn\b|sports|broadcast|media networks'),('Theme parks / leisure experiences',r'^experiences$|theme parks|cruise|parks and'),('Industrial manufacturing',r'manufacturing|industrial|machinery'),('Aerospace / defense',r'aviation|aircraft|aerospace|defense|propulsion|commercial engines'),('Consumer / retail',r'retail|consumer|e-commerce'),('Transportation / logistics',r'transportation|logistics|freight'),('Healthcare / medical products',r'healthcare|medical|pharma|biotech'),('Technology hardware / devices',r'personal computing|hardware|devices|electronics')]
def norm(s):return re.sub(r'[^a-z0-9]','',s.lower())
def names_from_list(text):
 text=text.strip(' :;.,“”"\'')
 text=re.sub(r'^(?:which (?:include|are)|namely|as follows)\s*:?\s*','',text,flags=re.I)
 text=re.sub(r'\s*\((?:1|i|a)\)\s*','',text,count=1,flags=re.I)
 # Protect compound geography names before splitting the top-level enumeration.
 protected={}
 for i,pattern in enumerate([r'Europe,?\s*(?:the )?Middle East(?:,)?\s*and Africa',r'Asia,?\s*Middle East(?:,)?\s*and Africa']):
  def keep(m):
   token=f'GEOCOMPOUND{i}';protected[token]=m.group();return token
  text=re.sub(pattern,keep,text,flags=re.I)
 numbered=re.split(r'\s*\((?:[1-9]|1[0-9]|[ivx]{1,4}|[a-n])\)\s*',text,flags=re.I)
 if len(numbered)>1:parts=[x for x in numbered if x.strip()]
 else:
  parts=[];start=0;depth=0
  for i,ch in enumerate(text):
   if ch=='(':depth+=1
   if ch==')':depth-=1
   if ch in ',;' and depth==0:parts.append(text[start:i]);start=i+1
  parts.append(text[start:])
  if len(parts)==1:parts=re.split(r'\s+and\s+',parts[0])
  elif re.search(r'\s+and\s+',parts[-1]) and not re.match(r'^\s*and\s+',parts[-1]):
   # Only the final conjunction separates the final two list members.
   x=re.split(r'\s+and\s+',parts[-1]);parts=parts[:-1]+[' and '.join(x[:-1]),x[-1]]
 names=[]
 for part in parts:
  s=re.sub(r'^\s*(?:and|the)\s+','',part.strip(),flags=re.I).strip(' .:;,“”"\'')
  s=re.sub(r'\s+segments?$','',s,flags=re.I)
  for token,value in protected.items():s=s.replace(token,value)
  if re.match(r'^(?:its|our|their|such|all|related|including)\b',s,re.I):return []
  if not (2<=len(s)<=95) or re.search(r'\b(?:include|includes|consists|consist|provides|operates|reported|reporting|revenue|income|profit|loss|following|are|is|has|have|comprised|which|that|each)\b',s,re.I):return []
  if not re.match(r'[A-Z0-9]',s):return []
  names.append(s)
 if len(names)<2 or len(names)>18 or len({norm(n) for n in names})!=len(names):return []
 return names
PATTERNS=[r'(?P<count>\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d{1,2}))\s+(?:(?:reportable|operating|business|core|new|reporting)\s+)*segments?\s*(?::|,?\s*(?:which\s+)?(?:include|includes|are|consist of|comprise|comprised of))\s*',r'(?:(?:reportable|operating|business|reporting)\s+)*segments\s+(?:include|includes|are|consist of|comprise)\s*',r'reportable segments?\s*:\s*']
def enumerations(text,source):
 text=re.sub(r'\s+',' ',text or '');safe=text.replace('U.S.','U~S~').replace('U.K.','U~K~');out=[]
 for pat in PATTERNS:
  for m in re.finditer(pat,safe,re.I):
   tail=safe[m.end():m.end()+1000];stop=re.search(r'\.(?:\s|$)',tail)
   if not stop:continue
   raw=tail[:stop.start()];raw=raw.replace('U~S~','U.S.').replace('U~K~','U.K.')
   names=names_from_list(raw)
   if not names:continue
   count=m.groupdict().get('count');count=NUM.get(str(count).lower(),int(count) if count and count.isdigit() else None)
   if count is not None and count!=len(names):continue
   start=max(text.rfind('. ',0,m.start())+2,0);quote=text[start:m.end()+stop.end()]
   if len(quote)>1500:quote=text[m.start():m.end()+stop.end()]
   out.append({'names':names,'declared_count':count,'source':source,'source_excerpt':quote,'enumeration_complete':count==len(names) if count else bool(re.search(r'\b(?:are|consist of|comprise)\b',m.group(),re.I)),'kind':'NAMED_SEGMENT_LIST'})
 # Single reportable segment is not the same thing as one product or one industry.
 for m in re.finditer(r'(?:(?:operates?|operating|has|have|comprises?|constitutes?|determined|considered).{0,100})\b(?:single|one)\s+(?:(?:operating|reportable|business)\s*(?:and\s*)?){1,3}segment\b',text,re.I):
  a=max(0,text.rfind('. ',0,m.start())+2);b=text.find('. ',m.end());q=text[a:b+1 if b>=0 else m.end()+150]
  if re.search(r'expenses considered significant|at the time|may not be significant',q,re.I):continue
  out.append({'names':['Single disclosed operating/reportable segment'],'declared_count':1,'source':source,'source_excerpt':q,'enumeration_complete':True,'kind':'SINGLE_SEGMENT_DISCLOSURE'})
 # Partial, explicitly named segment descriptions are retained without asserting completeness.
 if not out:
  labels=[];snippets=[]
  for m in re.finditer(r'(?:The|Our|Its)\s+([A-Z][^.;:\n]{2,85}?)\s+segment\s+(?:primarily\s+)?(?:consists|includes|comprises|provides|offers|brings)',text):
   name=m.group(1).strip()
   if re.search(r'\b(?:Company|Company.s|following|reportable|operating|This|Each)\b',name,re.I):continue
   if name not in labels:labels.append(name);end=text.find('. ',m.end());snippets.append(text[m.start():end+1 if end>=0 else m.end()+160])
  if labels:out.append({'names':labels,'declared_count':None,'source':source,'source_excerpt':' […additional source passage…] '.join(snippets[:3]),'enumeration_complete':False,'kind':'PARTIAL_NAMED_SEGMENT_DESCRIPTIONS'})
 return out

def industry_for(name,context,company_industry):
 if GEO.fullmatch(name):return company_industry,'GEOGRAPHIC','Geographic reporting segment; inherits only the issuer-level industry context. It is not a separate industry assignment.'
 hits=[(label,pattern) for label,pattern in RULES if re.search(pattern,name,re.I)]
 if hits:
  labels=list(dict.fromkeys(x[0] for x in hits))
  return ' / '.join(labels),'BUSINESS_ACTIVITY','Analyst activity mapping from explicit segment-name terms: '+', '.join(re.search(p,name,re.I).group() for _,p in hits)+'. Not a vendor-assigned segment SIC.'
 if name=='Single disclosed operating/reportable segment':return company_industry,'SINGLE_REPORTED_SEGMENT','Issuer-level industry used as context for the single disclosed segment; multiple products are not promoted into separate reportable segments.'
 # Short proper-name segments may use only directly linked segment activity sentences.
 linked=[]
 for sentence in re.split(r'(?<=[.!?])\s+',context):
  if name.lower() in sentence.lower() and re.search(r'\bsegment\b.{0,30}(?:includes|consists|comprises|provides|offers)|(?:includes|consists|comprises|provides|offers).{0,40}\bsegment\b',sentence,re.I):linked.append(sentence)
 labels=[]
 for label,pattern in RULES:
  if any(re.search(pattern,t,re.I) for t in linked):labels.append(label)
 if len(labels)==1:return labels[0],'BUSINESS_ACTIVITY','Analyst mapping from the segment-specific activity sentence; not an assigned SIC.'
 return 'UNKNOWN — segment activity mapping needs review','UNMAPPED','Segment name is extracted, but its industry is not inferred from the company’s other businesses.'

def source_rank(s):
 date=s.get('document_date') or 'UNKNOWN';period=s.get('report_period') or 'UNKNOWN'
 official=s.get('source_type') in ('SEC','OFFICIAL_IR','OFFICIAL_WEBSITE')
 return (official,date if re.match(r'^20\d\d-',date) else '',period if re.match(r'^20\d\d-',period) else '')
