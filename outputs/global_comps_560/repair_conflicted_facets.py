"""Apply evidence corrections, retain raw observations, and quarantine unresolved claims.

No source preference or NLI score is treated as proof of factual truth.
"""
import ast,collections,csv,hashlib,json,pathlib,re,unicodedata
P=pathlib.Path(__file__).resolve().parent;I=P/'semantic_validation_20261028';A=P/'multisource_audit_20261028';R=P/'global_run_20261028';O=P/'repaired_facets_20261028';O.mkdir(exist_ok=True)
def load(p):return json.loads(pathlib.Path(p).read_text())
def save(n,rs):
 (O/(n+'.json')).write_text(json.dumps(rs,ensure_ascii=False,indent=2,default=str))
 if isinstance(rs,list) and rs:
  cols=list(dict.fromkeys(k for r in rs for k in r))
  with (O/(n+'.csv')).open('w') as f:w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rs)
def canon(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(s or ''))).strip().lower()
defs={}
for n in ast.parse((P/'score_comp_draft.py').read_text()).body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('PATTERNS','CATS') for t in n.targets):defs[n.targets[0].id]=ast.literal_eval(n.value)
PAT=defs['PATTERNS'];CATS=defs['CATS']
PAT['Revenue Model']=r'\bsubscriptions?\b|\bfees?\b|\bcommissions?\b|royalt|\blicen[cs](?:e|es|ing)\b|\btransactions?\b|\bfranchis\w*|\brental\b|\bleasing\b|\bsells?\b|\bsales of\b|\bpremiums\b'
CATS['Revenue Model']['fees']=r'\bfees?\b';CATS['Revenue Model']['product sales']=r'\bsells?\b|\bsales of\b|\bproduct sales\b'
NOISE=re.compile(r'\b(?:us-gaap|ifrs-full|xbrli|dei|srt):\w+|\b[a-z]+:[A-Z]\w+Member\b|access denied|enable javascript|cookie settings|privacy policy|subscribe to (?:our )?(?:newsletter|email)|receive notifications via email|all rights reserved',re.I)
FINANCE_NOISE=re.compile(r'preferred stock|common stock|shares outstanding|securities act|exchange act|new or revised financial accounting|financial accounting standards|convertible|consolidated statements|stock options|earnings per share',re.I)
VERB=re.compile(r'\b(?:is|are|was|were|has|have|offers?|provides?|manufactur\w*|develop\w*|design\w*|operat\w*|distribut\w*|sell\w*|suppl\w*|serv\w*|markets?|focus\w*|specializ\w*|generat\w*|earn\w*|charg\w*|receiv\w*|engag\w*|include\w*|own\w*|establish\w*|found\w*|incorporat\w*)\b',re.I)
MANUAL={}
def manual(name,facet,value,url,reason,scope='COMPANY',date='UNKNOWN',allowed=True):
 MANUAL[(name,facet)]={'value':value,'url':url,'reason':reason,'scope':scope,'date':date,'allowed':allowed}
# Source-grounded corrections. A manual paraphrase is explicitly labelled as such, never as a verbatim quote.
manual('Paylocity Holding Corporation','Revenue Model','For its small-business payroll offering, Paylocity charges per employee per month. Cost depends on selected modules/services and employee count. Do not infer a universal enterprise rate or base fee from this page.','https://www.paylocity.com/who-we-serve/company-size/small/payroll/','Official pricing FAQ supplies the charging unit. Regulatory and feedback text was not revenue evidence.','SMALL_BUSINESS_PAYROLL')
manual('Paylocity Holding Corporation','Pricing Structure',MANUAL[('Paylocity Holding Corporation','Revenue Model')]['value'],MANUAL[('Paylocity Holding Corporation','Revenue Model')]['url'],'Scope is small-business payroll, not every Paylocity contract.','SMALL_BUSINESS_PAYROLL')
manual('Paylocity Holding Corporation','Business Model','Paylocity provides cloud-based HR and payroll software to employers. The official small-business payroll page describes software sold with a per-employee-per-month charging unit.','https://www.paylocity.com/who-we-serve/company-size/small/payroll/','Replace customer-industry and referral-network descriptions with the provider/product model.','SMALL_BUSINESS_PAYROLL')
manual('Ascom Holding AG','Product Specialization','Ascom provides communication and collaboration solutions for acute care, long-term care and enterprise organizations. It supplies solutions to healthcare providers; the Sheffield hospital description is a customer example.','https://www.ascom.com/about-us/','Official company overview resolves the hospital-customer subject error.')
manual('The Brink\'s Company','Company Maturity','Brink’s predecessor operating business dates to 1859. The 1991 date in the DSW case study describes the customer, not Brink’s.','https://www.brinks.fr/nous-connaitre/','Official Brink’s history names Perry Brink and the 1859 origin.','PREDECESSOR_BUSINESS_ORIGIN')
manual('Allient Inc.','Company Maturity','Hathaway predecessor business originated in 1939; Colorado public-company incorporation occurred in 1962. These are separate events.','https://allient.com/company/','Official corporate history distinguishes business origin from legal/public incorporation.','SEPARATE_ORIGIN_AND_INCORPORATION')
manual('Energy Recovery, Inc.','Company Maturity','Original incorporation in Virginia: April 1992. Reincorporation in Delaware: March 2001.','https://ir.energyrecovery.com/sec-filings/all-sec-filings/content/0000950134-08-020309/f50518e10vq.htm','Historical filing distinguishes original incorporation from reincorporation.','JURISDICTION_SPECIFIC_EVENTS',allowed=False)
manual('Singapore Paincare Holdings Ltd','Company Maturity','First specialist clinic established in 2007. Holding company incorporated on 31 December 2018.','https://links.sgx.com/1.0.0/corporate-information/2903','SGX identifies the clinic and holding company as separate event subjects.','CLINIC_VS_HOLDING_COMPANY',allowed=False)
manual('TRON Inc','Core Business Activity','TRON Inc. has a toy/merchandise business and a TRX digital-asset treasury strategy. The listed company is distinct from the TRON blockchain network and TRON DAO.','https://www.sec.gov/Archives/edgar/data/1956744/000149315226012723/form10-k.htm','The annual filing explicitly separates the corporate entity from the blockchain and reports two operating segments.','TWO_OPERATING_SEGMENTS','2025-12-31',False)
manual('TRON Inc','Primary Services',MANUAL[('TRON Inc','Core Business Activity')]['value'],MANUAL[('TRON Inc','Core Business Activity')]['url'],'The blockchain-network capabilities cannot be assigned as services operated by the listed issuer.','TWO_OPERATING_SEGMENTS','2025-12-31',False)
manual('Mankind Pharma Ltd','Geography Served','The cited vendor describes pharmaceutical and consumer-healthcare sales in India and internationally. The official PetStar page describes UK sourcing/manufacturing for a pet-food brand; that sourcing location is not a customer-market definition.','https://www.mankindpharma.com/pet-care/','Manufacturing/sourcing geography and geography of customers are different facets.','GEOGRAPHY_OF_SALES_VS_SOURCING',allowed=False)
manual('Welltower Inc.','Primary Products','Welltower describes a portfolio of 3,000+ seniors and wellness housing communities on the official website, with non-market-capitalization metrics dated 30 September 2026. The 2025 annual report describes 2,500+; retain that as the earlier period, not a same-date contradiction.','https://welltower.com/','Official website states the 2026-09-30 metric date; annual report is for 2025-12-31.','TIME_SPECIFIC_PORTFOLIO','2026-09-30')
manual('Welltower Inc.','End Markets','Seniors and wellness housing for mature renters and older adults. Portfolio counts of 2,500+ in the 2025 annual report and 3,000+ on the September 2026 website belong to different observation periods.','https://welltower.com/','The target market is unchanged in the two excerpts; portfolio count has a separate dated metric.','TIME_SPECIFIC_PORTFOLIO','2026-09-30')
def namekey(name):
 return ' '.join(w for w in re.findall(r'[a-z0-9]+',name.lower()) if w not in {'the','inc','incorporated','corporation','corp','company','co','ltd','limited','holdings','holding','ag','plc'})
def lookupmanual(name,facet):
 return next((v for (n,f),v in MANUAL.items() if f==facet and namekey(n)==namekey(name)),None)
def quality(text,facet,name,url=''):
 t=str(text or '').strip();reasons=[]
 if len(t)<45 or not VERB.search(t):reasons.append('FRAGMENT_OR_NAVIGATION_NOT_A_FACT')
 if NOISE.search(t):reasons.append('MARKUP_OR_BOILERPLATE')
 if facet in ['Primary Products','Primary Services','Core Business Activity','Business Model','Value Chain Position','Delivery Model','Distribution Channels'] and FINANCE_NOISE.search(t):reasons.append('FINANCING_DISCLOSURE_NOT_OPERATING_FACET')
 if not re.search(PAT[facet],t,re.I):reasons.append('NO_PRECISE_FACET_PREDICATE')
 if facet in ['Business Model','Revenue Model','Value Chain Position'] and re.search(r'industries.{0,30}(?:including|include)|serves? (?:various|for.profit)|end.markets?|our clients.{0,30}(?:manufactur|bank|insurance)',t,re.I) and not re.search(r'we (?:manufactur|sell|charge)|company (?:manufactur|sell|charges)|generat\w*.{0,35}revenue',t,re.I):reasons.append('CUSTOMER_INDUSTRY_NOT_PROVIDER_MODEL')
 if facet=='Revenue Model':
  if re.search(r'feedback|license.{0,25}(?:regulat|obtain)|required licenses|licensing requirements|must (?:register|obtain)|money transmitter|franchise agreement.{0,25}(?:not|terminate)',t,re.I) and not re.search(r'\brevenue\b|\bcharge\w*\b|\broyalt\w*|\bearn\w*\b|per.employee.per.month',t,re.I):reasons.append('REGULATION_OR_FEEDBACK_NOT_REVENUE')
  if re.search(r'royalt|\bfees?\b|\blicens\w*|transaction',t,re.I) and not re.search(r'revenue|charg\w*|\bsales\b|\bsells?\b|\bearning\b|\bearn\w*\b|\bfees? (?:for|from|based|charged)|franchis|subscription|per.employee|rental|leasing|commission|premium',t,re.I):reasons.append('PAYMENT_WORD_WITHOUT_CHARGING_CONTEXT')
 if facet=='Distribution Channels' and re.search(r'wellness credits|employee|spouses|neurosurgeon|geotech|engineering and resource management partner',t,re.I) and not re.search(r'market and sell|sell.{0,35}(?:through|via)|sales force|independent distributors|retail channels',t,re.I):reasons.append('NON_SALES_PARTNERSHIP_OR_EMPLOYEE_BENEFIT')
 if facet=='Company Maturity':
  named=any(len(w)>3 and re.search(r'\b'+re.escape(w)+r'\b',t[:180],re.I) for w in namekey(name).split())
  if not named and not re.search(r'^(?:we|our company|the company|it)\b.{0,60}(?:founded|established|incorporated)',t,re.I):reasons.append('MATURITY_ENTITY_NOT_BOUND')
 if facet in ['Geography Served','Geographic Concentration']:
  if re.search(r'Brotherhood of|labor union|labour union|employees.{0,20}collective|registered office|headquartered|sourced from|UK.made|manufactured in|incorporated in',t,re.I) and not re.search(r'sales|revenue|customers|serves|markets its|markets and sells',t,re.I):reasons.append('NON_CUSTOMER_MARKET_GEOGRAPHY')
 if facet in ['Business Model','Product Specialization','Core Business Activity'] and re.search(r'\b(?:chief|CFO|CEO|officer|chairman|chartered accountant|biography|career|she (?:has|is)|he (?:has|is))\b',t,re.I) and not re.search(r'company is|we (?:are|provide|manufactur)|company (?:operat|provid|manufactur)',t,re.I):reasons.append('PERSON_BIOGRAPHY_NOT_COMPANY_MODEL')
 if re.search(r'/case.stud|customer.stor|success.stor',url,re.I) and facet not in ['Customer Segment','End Markets']:
  if not re.search(r'\bwe (?:provide|offer|manufactur|develop|charge|operate)',t,re.I):reasons.append('CUSTOMER_STORY_NOT_COMPANY_LEVEL_EVIDENCE')
 return sorted(set(reasons))
def main():
 oldfacets=load(I/'Company_Facet_Validation.json');statements=load(I/'Source_Statements.json');sby={r['Statement ID']:r for r in statements};sp=load(I/'Source_Pairs.json');pby={x['Pair ID']:x for x in sp};pr=load(I/'Pair_Semantic_Results.json');resultsbygroup=collections.defaultdict(list);sg=collections.defaultdict(list)
 for x in statements:sg[x['Entity Role'],x['Entity ID'],x['Facet']].append(x)
 for x in pr:resultsbygroup[x['Entity Role'],x['Entity ID'],x['Facet']].append(x)
 bad={r['Statement ID']:r['Reason'] for r in load(I/'Statement_Adjudications.json')};qualityrows=[]
 for s in statements:
  reasons=quality(s['Statement Text'],s['Facet'],s['Company Name'],s['Source Link'] or '')
  if s['Statement ID'] in bad:reasons.append('PREVIOUS_REVIEW: '+bad[s['Statement ID']])
  if reasons:qualityrows.append({**s,'Exclusion Reasons':'; '.join(reasons)});bad[s['Statement ID']]='; '.join(reasons)
 baseline={}
 for role,n in [('TARGET','Target_Facets'),('PUBLIC','Public_Facets')]:
  for x in load(R/(n+'.json')):baseline[role,x.get('Target ID') or x.get('Candidate RIC'),x['Facet']]=x
 # Read exact source bodies for re-extraction; process per entity to avoid duplicating large filing text.
 docs=load(A/'Target_Sources.json')+load(A/'Public_Sources.json');dg=collections.defaultdict(list)
 for d in docs:dg[d['Entity Role'],d['Entity ID']].append(d)
 source_cache={};snap_cache={}
 def body(d):
  text=d.get('Source Text') or '';fp=d.get('Full Text or Snapshot Path') or ''
  if fp.endswith('.txt') and pathlib.Path(fp).is_file():
   if fp not in source_cache:source_cache[fp]=pathlib.Path(fp).read_text(errors='replace')
   text=source_cache[fp]
  elif d['Source Type']=='LSEG' and fp.endswith('.json') and pathlib.Path(fp).is_file():
   if fp not in snap_cache:snap_cache[fp]=load(fp)
   ric=(d.get('Source Field or Location') or '').split('Instrument=')[-1].split(';')[0]
   text=next((x.get('TR.BUSINESSSUMMARY') for x in snap_cache[fp] if x.get('Instrument')==ric and x.get('TR.BUSINESSSUMMARY')),text)
  if d['Source Type']=='SEC_ANNUAL_FILING':
   # Choose the real Item 1 narrative, never the short contents-table entry.
   options=[]
   for m in re.finditer(r'\bitem\s+1\s*[.\-:]?\s*business\b',text,re.I):
    tail=text[m.end():];end=re.search(r'(?:\n|\s{2,})item\s+1a\s*[.\-:]?',tail,re.I);part=tail[:end.start()] if end else tail[:120000]
    if len(part)>1500:options.append(part)
   if options:text=min(options,key=lambda s:abs(len(s)-35000))
   text=re.sub(r'\b(?:[a-z][\w.-]*):[A-Za-z0-9_]+',' ',text)
  return text[:160000]
 flagged={(r['Entity Role'],r['Entity ID'],r['Facet']) for r in oldfacets if r['Validation Status']=='POSSIBLE_CONFLICT_NEEDS_SOURCE_REVIEW'}
 decisions=[];patched=[];changes=[];newclaims=[];pairactions=[];manualexisting={r['Pair ID']:r for r in load(I/'Manual_Adjudications.json')};entity=None;chunks={}
 for old in oldfacets:
  role,ident,facet=key=(old['Entity Role'],old['Entity ID'],old['Facet']);name=old['Company Name'];orig=baseline[key];before=orig.get('Source Text') or '';baseurl=orig.get('Source Link') or '';manualfix=lookupmanual(name,facet);basebad=quality(before,facet,name,baseurl) if before else []
  excluded=[s for s in sg[key] if s['Statement ID'] in bad];needs=key in flagged or bool(excluded) or bool(basebad) or bool(manualfix)
  unresolved=[];dismissed=0;known=0
  for p in resultsbygroup[key]:
   if 'CONTRADICTION' not in p['Verdict'] and 'DISAGREEMENT' not in p['Verdict']:continue
   q=pby[p['Pair ID']];bs=[k for k in [q['Statement A ID'],q['Statement B ID']] if k in bad]
   if bs:act='INVALID_EXTRACTION_REMOVED';why=' | '.join(bad[k] for k in bs);dismissed+=1
   elif p['Pair ID'] in manualexisting:act='PRIOR_HUMAN_SCOPE_REVIEW';why=manualexisting[p['Pair ID']]['Reason'];known+=1
   elif manualfix:act='SOURCE_GROUNDED_MANUAL_CORRECTION';why=manualfix['reason'];known+=1
   else:act='UNRESOLVED_WITHHELD_FROM_SCORING';why='A model flag does not establish which source is correct. No unqualified canonical value is admitted until source/entity/time reconciliation.';unresolved.append(p['Pair ID'])
   pairactions.append({**p,'Repair Disposition':act,'Repair Reason':why})
  action='RETAINED_BASELINE_NOT_REVERIFIED';value=before or None;safe=bool(value);provider='OFFICIAL_WEBSITE' if role=='TARGET' else 'LSEG';url=baseurl;ids='';why='Unchanged baseline retained, not promoted to verified truth.';scope='UNVERIFIED_ORIGINAL_SCOPE';date='UNKNOWN';typ='SOURCE_EXCERPT'
  if needs:
   if entity!=(role,ident):
    entity=(role,ident);chunks={};source_cache.clear()
    for d in dg[entity]:
     text=body(d);ls=[]
     for m in re.finditer(r'[^\n]+',text):
      line=m.group().strip()
      if 45<=len(line)<=1800:ls.append((line,m.start()))
      elif len(line)>1800:
       for s in re.split(r'(?<=[.!?])\s+(?=[A-Z“])',line):
        if 45<=len(s)<=1400:ls.append((s,m.start()+line.find(s)))
     chunks[d['Evidence ID']]=(d,ls)
   candidates=[]
   for eid,(d,ls) in chunks.items():
    if role=='TARGET' and d['Source Type']!='OFFICIAL_WEBSITE':continue
    if 'SEARCH_RESULT_ONLY' in d['Status'] or 'NOT_COVERED' in d['Status']:continue
    for t,offset in ls:
     if quality(t,facet,name,d['Source Link'] or ''):continue
     tokens=namekey(name).split();intro=bool(re.search(r'^(?:we (?:are|provide|manufactur|offer)|our company|the company)',t,re.I) or any(len(w)>3 and re.search(r'^.{0,35}\b'+re.escape(w)+r'\b',t,re.I) for w in tokens))
     specificity=1 if re.search(r'per.employee|per.user|recurring revenue|royalt|franchis',t,re.I) and facet in ['Revenue Model','Pricing Structure','Recurring Revenue Profile','Business Model'] else 0
     priority={'OFFICIAL_WEBSITE':4,'SEC_ANNUAL_FILING':3,'LSEG':2,'WRDS_COMPUSTAT':1,'CAPITAL_IQ':1}.get(d['Source Type'],0)
     score=5*intro+2*specificity+priority+min(len(re.findall(PAT[facet],t,re.I)),3)-3*bool(re.search(r'\b(?:may|might|could|if|risk|historically)\b',t,re.I))
     candidates.append((score,t,d,offset))
   candidates.sort(key=lambda x:(-x[0],len(x[1])>650,-min(len(x[1]),450)))
   if candidates:
    _,v,d,offset=candidates[0];value=v;url=d['Source Link'];provider=d['Source Type'];ids=d['Evidence ID'];date=d['Source Date'];action='REEXTRACTED_FROM_PRECISE_SOURCE';why='Replaced weak/incorrect sentence with a direct facet-relevant source excerpt. This is a data extraction repair, not independent truth verification.'
    newclaims.append({'Entity Role':role,'Entity ID':ident,'Company Name':name,'Facet':facet,'Repaired Source Text':v,'Source Type':provider,'Source Link':url,'Evidence ID':ids,'Source Date':date,'Character Offset In Extraction Context':offset,'Full Source Path':d.get('Full Text or Snapshot Path'),'Evidence Meaning':'Direct source excerpt; corporate/segment scope may still require review.'})
   else:value=None;url=None;provider=None;safe=False;action='REMOVED_UNSUPPORTED_VALUE';why='No admissible facet-relevant replacement was found; unsupported value removed rather than guessed.'
   if manualfix:
    # External primary references stay diagnostic for pseudo-private targets.
    if role=='PUBLIC' or manualfix['allowed']:
     value=manualfix['value'];url=manualfix['url'];provider='OFFICIAL_WEBSITE' if manualfix['allowed'] else 'PRIMARY_FILING_OR_EXCHANGE';ids='MANUAL_PRIMARY_SOURCE_REVIEW';scope=manualfix['scope'];date=manualfix['date'];action='APPLIED_SOURCE_VERIFIED_CORRECTION';why=manualfix['reason'];typ='REVIEWER_PARAPHRASE';unresolved=[];safe=True
    else:why+=' External manual correction retained in diagnostic field only; target selector is still website-only.'
   if unresolved:
    action='UNRESOLVED_VALUE_QUARANTINED';safe=False;why='Re-extraction does not settle the remaining source disagreement. Corrected research/scoring value is withheld; source-attributed observations remain available.'
   else:safe=bool(value)
  row={'Entity Role':role,'Entity ID':ident,'Company Name':name,'Facet':facet,'Before Value':before or None,'Corrected Value':value if safe else None,'Source Observation Not Admitted':value if not safe else None,'Eligible For Scoring':safe,'Repair Action':action,'Repair Reason':why,'Source Type':provider,'Source Link':url,'Evidence IDs':ids or None,'Source Date':date,'Scope':scope,'Text Type':typ,'Original Conflict Flag':key in flagged,'Unresolved Conflict Pair IDs':'; '.join(unresolved) or None,'Excluded Source Statements':len(excluded),'Diagnostic External Correction':manualfix['value'] if manualfix and role=='TARGET' and not manualfix['allowed'] else None,'Target Input Boundary':'OFFICIAL_WEBSITE_ONLY' if role=='TARGET' else 'MULTI_SOURCE_PUBLIC','Human Reviewed Fact':action=='APPLIED_SOURCE_VERIFIED_CORRECTION'}
  patched.append(row)
  if needs:changes.append(row)
  if key in flagged:decisions.append(row)
 save('Corrected_Facets',patched);save('Repair_Log',changes);save('Conflict_Dispositions',decisions);save('Rejected_Source_Statements',qualityrows);save('Reextracted_Source_Evidence',newclaims);save('Conflict_Pair_Dispositions',pairactions)
 summary={'all_facet_rows':len(patched),'original_flagged_facets':len(flagged),'flagged_facets_processed':len(decisions),'flagged_dispositions':dict(collections.Counter(x['Repair Action'] for x in decisions)),'all_repair_actions':dict(collections.Counter(x['Repair Action'] for x in changes)),'rejected_selected_statements':len(qualityrows),'reextracted_source_claims':len(newclaims),'actual_corrected_values_different_from_original':sum(canon(x['Corrected Value'])!=canon(x['Before Value']) for x in patched),'remaining_flagged_facets_quarantined':sum(x['Repair Action']=='UNRESOLVED_VALUE_QUARANTINED' for x in decisions),'source_date_unknown_not_replaced_with_retrieval_date':True,'target_external_data_used_for_scoring':False,'original_files_overwritten':False,'all_conflicts_factually_resolved':False}
 save('repair_summary',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
