"""Recalculate existing candidate rows from applied corrections; no new candidate discovery."""
import collections,hashlib,json,pathlib,math
import numpy as np
from repair_conflicted_facets import P,I,R,O,A,load,save,CATS,canon,namekey,quality
from strict_facet_checks import strict_reasons
def main():
 rows=load(O/'Corrected_Facets.json')
 oldfacets={}
 for role,file in [('TARGET','Target_Facets'),('PUBLIC','Public_Facets')]:
  for x in load(R/(file+'.json')):oldfacets[role,x.get('Target ID') or x.get('Candidate RIC'),x['Facet']]=x
 docs=load(A/'Target_Sources.json')+load(A/'Public_Sources.json');dg=collections.defaultdict(list)
 for d in docs:dg[d['Entity Role'],d['Entity ID']].append(d)
 reviewed_software={
  'Paylocity Holding Corporation':('https://www.paylocity.com/products/ ; https://www.paylocity.com/products/hr/human-resources-software/',{
   'Core Business Activity':'Paylocity provides cloud-based HR software and unifies HR, payroll, finance and IT workflows on its platform.',
   'Primary Products':'Paylocity offers HR and payroll software, finance tools for expenses, AP automation and corporate cards, and IT tools for asset and access management.',
   'Primary Services':'Paylocity offers payroll tax services and client support alongside its HR and payroll software platform.'}),
  'Paycom Software, Inc.':('https://www.paycom.com/',{
   'Core Business Activity':'Paycom provides HR and payroll software built on a single database.',
   'Primary Products':'Paycom offers payroll, talent acquisition, talent management, HR management, and time and labor management software.',
   'Primary Services':'Paycom offers client implementation assistance, payroll-processing guidance and ongoing support alongside its HR and payroll software.'}),
  'Paychex, Inc.':('https://www.paychex.com/corporate',{
   'Core Business Activity':'Paychex provides integrated human capital management solutions for HR, payroll, retirement plans, employee benefits and business insurance.',
   'Primary Services':'Paychex offers payroll, HR, retirement-plan, employee-benefit and business-insurance services to business clients.'}),
  'Automatic Data Processing Inc':('https://www.adp.com/what-we-offer.aspx',{
   'Core Business Activity':'ADP provides payroll and HR services and technology for businesses, including HR outsourcing and professional employer organization services.',
   'Primary Products':'ADP offers payroll and HR platforms, time and attendance tools, talent-management tools and benefits-administration technology.'})
 }
 # Sourcing location is not a company-wide customer-market fact.
 for r in rows:
  soft=next(((u,fs) for n,(u,fs) in reviewed_software.items() if namekey(n)==namekey(r['Company Name']) and r['Facet'] in fs),None)
  if soft:
   u,fs=soft;r.update({'Corrected Value':fs[r['Facet']],'Source Observation Not Admitted':None,'Eligible For Scoring':True,'Repair Action':'APPLIED_SOURCE_VERIFIED_CORRECTION','Repair Reason':'Read the company’s official offering page. Replace internal workforce/security/biography excerpts with actual customer-facing products or services.','Source Type':'OFFICIAL_WEBSITE','Source Link':u,'Source Date':'UNKNOWN','Fact As Of Date':'UNKNOWN','Scope':'COMPANY_OFFERING','Text Type':'REVIEWER_PARAPHRASE','Unresolved Conflict Pair IDs':None,'Human Reviewed Fact':True,'Evidence IDs':'MANUAL_PRIMARY_SOURCE_REVIEW','Reviewed At':'2026-10-28'})
  r.setdefault('Fact As Of Date','UNKNOWN');r.setdefault('Reviewed At','2026-10-28' if r['Human Reviewed Fact'] else 'UNKNOWN')
  if r['Human Reviewed Fact'] and r['Fact As Of Date']=='UNKNOWN' and r['Source Date']!='UNKNOWN':
   r['Fact As Of Date']=r['Source Date'];r['Source Date']='2026-03-25' if r['Company Name']=='TRON Inc' else 'UNKNOWN'
  if r['Company Name']=='Qben Infra AB' and r['Facet'] in ['Primary Products','Core Business Activity','Business Model','Value Chain Position']:
   r.update({'Corrected Value':'The current Qben website lists Construction, Power, and Testing/Inspection/Certification as its three business areas. Qben completed the Rail divestment announced on 28 January 2026; retain older four-area descriptions as historical, not current group operations.','Source Observation Not Admitted':None,'Eligible For Scoring':True,'Repair Action':'APPLIED_SOURCE_VERIFIED_CORRECTION','Repair Reason':'Current company business-area list and the dated completed-divestment announcement supersede the undated four-area company description.','Source Type':'OFFICIAL_WEBSITE','Source Link':'https://qben.se/ ; https://www.qben.se/en/wp-content/uploads/sites/2/2021/10/press-release-qben-infra-completion-of-the-divestment-of-qben-rail-260128.pdf','Source Date':'UNKNOWN','Fact As Of Date':'Homepage observed 2026-10-28; Rail divestment announced complete 2026-01-28','Scope':'POST_RAIL_DIVESTITURE_BUSINESS_AREAS','Text Type':'REVIEWER_PARAPHRASE','Unresolved Conflict Pair IDs':None,'Human Reviewed Fact':True,'Evidence IDs':'MANUAL_PRIMARY_SOURCE_REVIEW','Reviewed At':'2026-10-28'})
  if r['Repair Action']=='RETAINED_BASELINE_NOT_REVERIFIED' and r['Corrected Value']:
   ds=dg[r['Entity Role'],r['Entity ID']]
   matches=[d for d in ds if d['Source Type']=='LSEG'] if r['Entity Role']=='PUBLIC' else [d for d in ds if d['Source Type']=='OFFICIAL_WEBSITE' and d['Source Link'] and d['Source Link'] in str(r['Source Link'] or '')]
   if matches:r['Source Link']='; '.join(dict.fromkeys(d['Source Link'] for d in matches if d['Source Link']));r['Evidence IDs']='; '.join(d['Evidence ID'] for d in matches)
  if namekey(r['Company Name'])==namekey('Paylocity Holding Corporation'):
   if r['Facet'] in ['Revenue Model','Pricing Structure'] and r['Repair Action']=='APPLIED_SOURCE_VERIFIED_CORRECTION':
    r['Corrected Value']='For small-business payroll, Paylocity charges a monthly per-employee fee. Cost depends on the modules/services selected and employee count. This page does not establish a universal enterprise rate or a separate base fee.'
   if r['Facet']=='Business Model' and r['Repair Action']=='APPLIED_SOURCE_VERIFIED_CORRECTION':
    r['Corrected Value']='Paylocity supplies cloud-based software for HR and payroll to organizations. The small-business payroll offering is charged through monthly per-employee fees. Customer industries are distinct from this software-provider business model.'
    r['Source Link']='https://www.paylocity.com/company/about-us/newsroom/press-releases/paylocity-debuts-ai-assistant-to-simplify-and-accelerate-hr-processes/ ; https://www.paylocity.com/who-we-serve/company-size/small/payroll/'
  if r['Company Name']=='Mankind Pharma Ltd' and r['Facet']=='Geography Served':
   r.update({'Corrected Value':None,'Source Observation Not Admitted':'The official PetStar page describes recipes for the Indian climate and ingredients sourced in the UK. This is a pet-care subsegment and sourcing description, not company-wide customer-market coverage.','Eligible For Scoring':False,'Source Type':'OFFICIAL_WEBSITE','Repair Action':'APPLIED_SCOPE_SEPARATION_NO_GLOBAL_VALUE','Repair Reason':'Remove the sourcing-versus-sales false comparison. Company-wide geography remains unknown from this page.','Scope':'PETCARE_SOURCING_NOT_GROUP_SALES'})
 # Recover valid original claims that an earlier overly narrow finite-verb list rejected.
 for r in rows:
  if r['Repair Action']=='REMOVED_UNSUPPORTED_VALUE' and not r['Unresolved Conflict Pair IDs']:
   base=oldfacets[r['Entity Role'],r['Entity ID'],r['Facet']];b=base.get('Source Text') or ''
   if b and not strict_reasons(b,r['Facet']) and not quality(b,r['Facet'],r['Company Name'],base.get('Source Link') or ''):
    r['Corrected Value']=b;r['Eligible For Scoring']=True;r['Repair Action']='RESTORED_VALID_ORIGINAL_EXCERPT';r['Repair Reason']='Original excerpt passes the corrected finite-verb and facet checks. Restored as a source claim, not independently verified truth.'
    matches=[d for d in dg[r['Entity Role'],r['Entity ID']] if d['Source Type']=='LSEG'] if r['Entity Role']=='PUBLIC' else [d for d in dg[r['Entity Role'],r['Entity ID']] if d['Source Type']=='OFFICIAL_WEBSITE' and d['Source Link'] and d['Source Link'] in str(base.get('Source Link') or '')]
    r['Source Type']='LSEG' if r['Entity Role']=='PUBLIC' else 'OFFICIAL_WEBSITE';r['Source Link']='; '.join(dict.fromkeys(d['Source Link'] for d in matches if d['Source Link'])) or base.get('Source Link');r['Evidence IDs']='; '.join(d['Evidence ID'] for d in matches)
 strict_exclusions=[]
 for r in rows:
  if r['Eligible For Scoring'] and not r['Human Reviewed Fact']:
   reasons=strict_reasons(r['Corrected Value'],r['Facet'])
   if reasons:
    strict_exclusions.append({'Entity Role':r['Entity Role'],'Entity ID':r['Entity ID'],'Company Name':r['Company Name'],'Facet':r['Facet'],'Rejected Value':r['Corrected Value'],'Source Link':r['Source Link'],'Reason':'; '.join(reasons)})
    r['Source Observation Not Admitted']=r['Corrected Value'];r['Corrected Value']=None;r['Eligible For Scoring']=False;r['Repair Action']='REMOVED_UNSUPPORTED_VALUE';r['Repair Reason']='Strict final quality check: '+'; '.join(reasons)
    base=oldfacets[r['Entity Role'],r['Entity ID'],r['Facet']];b=base.get('Source Text') or ''
    if b and not r['Unresolved Conflict Pair IDs'] and not strict_reasons(b,r['Facet']) and not quality(b,r['Facet'],r['Company Name'],base.get('Source Link') or ''):
     r['Corrected Value']=b;r['Eligible For Scoring']=True;r['Repair Action']='RESTORED_VALID_ORIGINAL_EXCERPT';r['Repair Reason']='Rejected the weak replacement. Original source excerpt passes the stricter predicate/quality checks; retained as an unverified source claim.'
     matches=[d for d in dg[r['Entity Role'],r['Entity ID']] if d['Source Type']=='LSEG'] if r['Entity Role']=='PUBLIC' else [d for d in dg[r['Entity Role'],r['Entity ID']] if d['Source Type']=='OFFICIAL_WEBSITE' and d['Source Link'] and d['Source Link'] in str(base.get('Source Link') or '')]
     r['Source Type']='LSEG' if r['Entity Role']=='PUBLIC' else 'OFFICIAL_WEBSITE';r['Source Link']='; '.join(dict.fromkeys(d['Source Link'] for d in matches if d['Source Link'])) or base.get('Source Link');r['Evidence IDs']='; '.join(d['Evidence ID'] for d in matches)
 save('Final_Quality_Exclusions',strict_exclusions);save('Corrected_Facets',rows)
 for n in ['Repair_Log','Conflict_Dispositions']:
  orig=load(O/(n+'.json'));keys={(x['Entity Role'],x['Entity ID'],x['Facet']) for x in orig}
  if n=='Repair_Log':keys|={(x['Entity Role'],x['Entity ID'],x['Facet']) for x in rows if x['Human Reviewed Fact'] or x['Repair Action']!='RETAINED_BASELINE_NOT_REVERIFIED'}
  save(n,[x for x in rows if (x['Entity Role'],x['Entity ID'],x['Facet']) in keys])
 by={(x['Entity Role'],x['Entity ID'],x['Facet']):x for x in rows};old=load(R/'Facet_Scores.json');oldresults=load(R/'Comp_Results.json');resultsby={(r['Target ID'],r['Candidate RIC']):r for r in oldresults};texts=set();changed=[]
 for d in old:
  if d['Facet']=='FF49 Industry':continue
  a=by['TARGET',d['Target ID'],d['Facet']];b=by['PUBLIC',d['Candidate RIC'],d['Facet']]
  ischange=(canon(a['Before Value'])!=canon(a['Corrected Value']) or canon(b['Before Value'])!=canon(b['Corrected Value']) or not a['Eligible For Scoring'] or not b['Eligible For Scoring'])
  if ischange:
   changed.append((d,a,b))
   if a['Eligible For Scoring'] and b['Eligible For Scoring'] and d['Facet'] not in CATS:texts.update([a['Corrected Value'],b['Corrected Value']])
 texts=sorted(texts);vectors={};cachetexts=O/'repair_embedding_texts.json';cachevectors=O/'repair_embeddings.npy'
 if cachetexts.exists() and cachevectors.exists():vectors=dict(zip(load(cachetexts),np.load(cachevectors)))
 todo=[t for t in texts if t not in vectors];print('Changed score rows',len(changed),'unique embedding texts',len(texts),'uncached',len(todo),flush=True)
 if todo:
  import torch
  from sentence_transformers import SentenceTransformer
  torch.set_num_threads(6);model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2',device='cpu',local_files_only=True)
  # Same mean-of-200-word-chunks convention as the original draft.
  for i in range(0,len(todo),400):
   ts=todo[i:i+400];parts=[];owners=[]
   for j,t in enumerate(ts):
    ws=t.split()
    for k in range(0,min(len(ws),600),200):parts.append(' '.join(ws[k:k+200]));owners.append(j)
   es=model.encode(parts,batch_size=64,normalize_embeddings=True,show_progress_bar=False)
   for j,t in enumerate(ts):
    v=es[np.array(owners)==j].mean(axis=0);vectors[t]=v/max(np.linalg.norm(v),1e-12)
   print('Embedding texts',min(i+400,len(todo)),'/',len(todo),flush=True)
  cachetexts.write_text(json.dumps(texts));np.save(cachevectors,np.stack([vectors[t] for t in texts]))
 ds=[];groups=collections.defaultdict(list)
 for d in old:
  x=dict(d);x['Prior Facet Similarity Percent']=d['Facet Similarity Percent'];x['Prior Contribution Percent Points']=d['Contribution Percent Points'];x['Prior Target Source Text']=d['Target Source Text'];x['Prior Public Source Text']=d['Public Source Text'];x['Repair Applied']=False
  if d['Facet']!='FF49 Industry':
   a=by['TARGET',d['Target ID'],d['Facet']];b=by['PUBLIC',d['Candidate RIC'],d['Facet']];ischange=(canon(a['Before Value'])!=canon(a['Corrected Value']) or canon(b['Before Value'])!=canon(b['Corrected Value']) or not a['Eligible For Scoring'] or not b['Eligible For Scoring'])
   x['Target Repair Action']=a['Repair Action'];x['Public Repair Action']=b['Repair Action'];x['Target Evidence Role']=a['Target Input Boundary'];x['Public Evidence Role']=b['Target Input Boundary']
   x['Target Source Link']=a['Source Link'];x['Public Source Link']=b['Source Link'];x['Public Source Field']=b['Evidence IDs'];x['Target Evidence IDs']=a['Evidence IDs'];x['Public Evidence IDs']=b['Evidence IDs']
   if ischange:
    x['Repair Applied']=True;x['Target Source Text']=a['Corrected Value'];x['Target Source Link']=a['Source Link'];x['Public Source Text']=b['Corrected Value'];x['Public Source Link']=b['Source Link'];x['Public Source Field']=b['Evidence IDs'];sc=None
    if a['Eligible For Scoring'] and b['Eligible For Scoring']:
     if d['Facet'] in CATS:
      aa={k for k,p in CATS[d['Facet']].items() if __import__('re').search(p,a['Corrected Value'],__import__('re').I)};bb={k for k,p in CATS[d['Facet']].items() if __import__('re').search(p,b['Corrected Value'],__import__('re').I)};x['Target Categories']='; '.join(sorted(aa));x['Public Categories']='; '.join(sorted(bb))
      if aa and bb:sc=100*len(aa&bb)/len(aa|bb)
      x['Scoring Method']='REPAIRED_EXPLICIT_CATEGORY_JACCARD'
     else:sc=100*max(0.,min(1.,float(np.dot(vectors[a['Corrected Value']],vectors[b['Corrected Value']]))));x['Scoring Method']='REPAIRED_SOURCE_EMBEDDING_COSINE_UNCALIBRATED';x['Semantic Cosine']=round(sc/100,4)
    else:x['Scoring Method']='WITHHELD_UNRESOLVED_OR_UNSUPPORTED_FACET';x['Semantic Cosine']=None
    x['Facet Similarity Percent']=round(sc,2) if sc is not None else None;x['Observed Weight']=d['Proposed Weight'] if sc is not None else None;x['Lexical Cosine']=None
  x['Contribution Percent Points']=None;x['Verification']='REPAIRS_APPLIED; NO_CLAIM_ALL_FACTS_OR_COMPS_VALIDATED';ds.append(x);groups[d['Target ID'],d['Candidate RIC']].append(x)
 results=[];rt=collections.defaultdict(list)
 for key,rs in groups.items():
  prev=resultsby[key];observed=sum(r['Proposed Weight'] for r in rs if r['Facet Similarity Percent'] is not None);weighted=sum(r['Proposed Weight']*r['Facet Similarity Percent'] for r in rs if r['Facet Similarity Percent'] is not None);partial=weighted/observed if observed else None
  tid,ric=key
  core=all(by[role,ident,'Core Business Activity']['Eligible For Scoring'] and any(by[role,ident,f]['Eligible For Scoring'] for f in ['Primary Products','Primary Services']) for role,ident in [('TARGET',tid),('PUBLIC',ric)])
  score=partial if core else None
  for d in rs:
   if d['Facet Similarity Percent'] is not None:d['Contribution Percent Points']=round(d['Proposed Weight']*d['Facet Similarity Percent']/observed,4)
  r={**prev,'Prior Rank':prev['Rank'],'Prior Similarity Percent':prev['Similarity Percent'],'Prior Weighted Evidence Coverage':prev['Weighted Evidence Coverage'],'Rank':None,'Similarity Percent':round(score,2) if score is not None else None,'Partial Observed-Facet Similarity':round(partial,2) if partial is not None else None,'Weighted Evidence Coverage':round(observed,4),'Scored Facets':sum(x['Facet Similarity Percent'] is not None for x in rs),'Repaired Facet Score Rows':sum(x['Repair Applied'] for x in rs),'Status':'WITHHELD_MISSING_OR_CONFLICTED_CORE_EVIDENCE' if not core else 'REPAIRED_DRAFT_REQUIRES_COMP_AND_SEGMENT_REVIEW','Evidence Adjusted Ranking Index':round(score*observed**.5,4) if score is not None else None,'Ranking Scope':'RERANKED_WITHIN_PREVIOUS_10_CANDIDATES_ONLY; NO_NEW_GLOBAL_DISCOVERY','Candidate Source':by['PUBLIC',ric,'Core Business Activity']['Source Type'],'Source Text':by['PUBLIC',ric,'Core Business Activity']['Corrected Value'],'Source Link':by['PUBLIC',ric,'Core Business Activity']['Source Link'],'Source Field':by['PUBLIC',ric,'Core Business Activity']['Evidence IDs'],'Score Meaning':'Uncalibrated observed-facet similarity, not probability of being a valid comparable. Unknown and quarantined values are not used.'}
  rt[tid].append(r)
 for tid,rs in rt.items():
  rs.sort(key=lambda x:(x['Evidence Adjusted Ranking Index'] is not None,x['Evidence Adjusted Ranking Index'] or 0),reverse=True);rank=0
  for r in rs:
   if r['Similarity Percent'] is not None:rank+=1;r['Rank']=rank
   results.append(r)
 save('Corrected_Facet_Scores',ds);save('Corrected_Comp_Results',results)
 summary=load(O/'repair_summary.json');decisions=load(O/'Conflict_Dispositions.json');changes=load(O/'Repair_Log.json');summary.update({'flagged_dispositions':dict(collections.Counter(x['Repair Action'] for x in decisions)),'all_repair_actions':dict(collections.Counter(x['Repair Action'] for x in changes)),'actual_corrected_values_different_from_original':sum(canon(x['Before Value'])!=canon(x['Corrected Value']) for x in rows),'remaining_flagged_facets_quarantined':sum(x['Repair Action']=='UNRESOLVED_VALUE_QUARANTINED' for x in decisions),'rescored_existing_pairs':len(results),'recomputed_or_withheld_facet_score_rows':sum(x['Repair Applied'] for x in ds),'pairs_with_changed_scores':sum(x['Similarity Percent']!=x['Prior Similarity Percent'] for x in results),'pairs_withheld_due_to_core_evidence':sum(x['Similarity Percent'] is None for x in results),'pairs_with_scored_facets':sum(x['Similarity Percent'] is not None for x in results),'ranking_scope':'Previous ten candidates per target only; no new discovery','forecasting_started':False});save('repair_summary',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
