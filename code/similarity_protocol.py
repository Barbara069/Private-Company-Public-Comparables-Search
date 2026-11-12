"""Auditable similarity calculation. Requires cited, explicit per-facet judgments.
No embedding score is substituted for reviewed economic similarity.
"""
VERSION='2026-10-30-v1'
MAIN_WEIGHTS=dict(zip(['Primary Products','Primary Services','Core Business Activity','Customer Segment','End Markets','Business Model','Revenue Model','Value Chain Position','Geography Served','Company Size Category','Product Specialization','Customer Concentration','Distribution Channels','Delivery Model','Pricing Structure','Recurring Revenue Profile','Capital Intensity','Labor Intensity','Regulatory Exposure','Competitive Positioning','Product Differentiation','Customer Switching Costs','Revenue Cyclicality','Company Maturity','Technology Dependence','Geographic Concentration','Supply Chain Complexity','Contract Duration','IP Dependence','Brand Dependence'],[11,6,0,8,9,8,10,7,5,3,3,2,4,3,2,3,3,1,2,1,2,2,2,0,0,0,1,1,0,1]))
INDUSTRY_WEIGHTS={
'Technology / SaaS':dict(zip(['Software Category','Deployment Model','Customer Size','Pricing Metric','Revenue Composition','Product Architecture','Implementation Complexity','Integration Dependence','Customer Retention Model','AI Exposure'],[18,5,14,5,8,10,10,12,16,2])),
'Manufacturing / Industrials':dict(zip(['Manufacturing Type','Material Type','Production Model','Product Complexity','Production Role','Automation Level','End-Market Exposure','Capacity Sensitivity','Supply Chain Position','Raw Material Exposure'],[12,6,12,14,12,5,16,10,7,6])),
'Financial Services':dict(zip(['Financial Business Type','Revenue Driver','Customer Type','Balance Sheet Dependence','Credit Exposure','Asset Class Focus','Regulatory Regime','Distribution Model','Risk Underwriting Model','Funding Model'],[18,14,8,14,10,6,10,4,10,6])),
'Healthcare / Life Sciences':dict(zip(['Healthcare Segment','Product Stage','Therapeutic Area','Revenue Source','Customer / Payer','Regulatory Approval','IP / Patent Dependence','Manufacturing Model','Reimbursement Exposure','R&D Intensity'],[16,16,12,10,10,12,8,4,8,4])),
'Consumer / Retail':dict(zip(['Product Category','Market Position','Distribution Model','Store Footprint','Brand Strength','Purchase Frequency','Customer Demographics','Inventory Model','Geographic Footprint','Pricing Power'],[18,12,18,8,8,10,6,8,6,6])),
'Energy / Utilities / Materials':dict(zip(['Industry Position','Commodity Exposure','Revenue Structure','Asset Ownership','Geographic Resource Exposure','Capital Intensity','Regulatory Structure','Reserve / Resource Profile','Energy Transition Exposure','Commodity Price Sensitivity'],[14,16,14,10,10,8,10,6,4,8])),
'Business / Professional Services':dict(zip(['Service Category','Engagement Model','Billing Structure','Labor Specialization','Client Segment','Contract Duration','Geographic Delivery','Technology Enablement','Revenue Recurrence','Scalability'],[18,14,10,10,12,10,6,6,8,6])),
'Restaurants':dict(zip(['Restaurant format','Franchise vs company-operated economics','Unit format / operating footprint','Menu / cuisine / customer need','Dayparts / occasions','Price point / value proposition','Ordering / delivery channel mix','Geographic operating mix','Purchase frequency','Supply chain / menu input exposure','Brand / loyalty dependence','Competitive positioning within QSR'],[12,22,8,12,8,8,8,5,5,4,4,4]))}

def validate_weights(weights):
 if any(v<0 for v in weights.values()) or abs(sum(weights.values())-100)>1e-9:raise ValueError('Weights must be nonnegative and total 100')

def effective_weights(weights,excluded=()):
 """Freeze exclusions at TARGET level: N/A or duplicate economic fact, not candidate missingness."""
 validate_weights(weights)
 unknown=set(excluded)-set(weights)
 if unknown:raise ValueError('Unrecognized facet exclusion')
 d={k:(0 if k in excluded else v) for k,v in weights.items()};den=sum(d.values())
 if not den:raise ValueError('No applicable weighted facets')
 return {k:100*v/den for k,v in d.items()}

def evidence_ok(e,target=False):
 if not e or not e.get('text') or not e.get('source_url','').startswith(('https://','http://')):return False
 if e.get('unresolved_contradiction') or e.get('identity_status')=='MISMATCH':return False
 if target and e.get('source_type')!='OFFICIAL_WEBSITE':return False
 if target:
  from urllib.parse import urlsplit
  host=(urlsplit(e['source_url']).hostname or '').lower()
  if any(host==d or host.endswith('.'+d) for d in ['sec.gov','wharton.upenn.edu','lseg.com','capitaliq.com']):return False
  if (host.startswith(('investor.','investors.','ir.')) or '/investor-relations/' in e['source_url'].lower()) and e.get('content_scope')!='BUSINESS_DESCRIPTION_ONLY':return False
 # Issuer IR/filing text hosted on its website still cannot bypass website-only business-source boundary.
 if target and e.get('document_type') in ['10-K','10-Q','20-F','40-F','8-K','6-K','ANNUAL_REPORT','EARNINGS_RELEASE','EARNINGS_CALL']:return False
 return e.get('scope_aligned') is True and e.get('relevance_reviewed') is True

def component(weights,judgments):
 validate_weights(weights);supported=coverage=0;details=[]
 for facet,weight in weights.items():
  j=judgments.get(facet,{});s=j.get('score');reason=j.get('reason','')
  valid=(s in (0,25,50,75,100) and bool(reason) and evidence_ok(j.get('target_evidence'),True) and evidence_ok(j.get('candidate_evidence')) and j.get('duplicate_economic_fact') is not True)
  c=weight*s/100 if valid else 0
  if valid:coverage+=weight;supported+=c
  details.append({'facet':facet,'weight_percent':weight,'observed':valid,'score':s if valid else None,'contribution_points':c,'reason':reason,'target_evidence':j.get('target_evidence'),'candidate_evidence':j.get('candidate_evidence')})
 return dict(supported_points=supported,coverage_percent=coverage,observed_similarity_percent=supported*100/coverage if coverage else None,uncertainty_interval=[supported,supported+100-coverage],details=details)

def combine(main,industry,main_share=.6,critical_reviewed=False):
 if not 0<=main_share<=1:raise ValueError('Invalid component weight')
 support=main_share*main['supported_points']+(1-main_share)*industry['supported_points']
 coverage=main_share*main['coverage_percent']+(1-main_share)*industry['coverage_percent']
 eligible=coverage>=80 and main['coverage_percent']>=70 and industry['coverage_percent']>=70 and critical_reviewed
 return {'method_version':VERSION,'main_share':main_share,'industry_share':1-main_share,'evidence_supported_points':support,'coverage_percent':coverage,'observed_similarity_percent':support*100/coverage if coverage else None,'uncertainty_interval':[support,support+100-coverage],'ranking_eligible':eligible,'status':'ELIGIBLE_FOR_RANKING' if eligible else 'ABSTAIN_INSUFFICIENT_REVIEWED_EVIDENCE'}

def segment_similarity(matrix,target_mix,candidate_mix):
 """Weights must be known visible mix or explicitly labelled scenario weights by caller."""
 if not matrix or len(matrix)!=len(target_mix) or any(len(r)!=len(candidate_mix) for r in matrix):raise ValueError('Segment matrix dimensions')
 for mix in (target_mix,candidate_mix):
  if any(x<0 for x in mix) or abs(sum(mix)-1)>1e-8:raise ValueError('Mix must include all business segments and total one')
 if any(x is None or not 0<=x<=1 for r in matrix for x in r):raise ValueError('Unresolved segment scores require scenarios, not silent exclusion')
 a=sum(w*max(row) for w,row in zip(target_mix,matrix));b=sum(w*max(row[j] for row in matrix) for j,w in enumerate(candidate_mix))
 return 100*(a+b)/2

for _weights in [MAIN_WEIGHTS,*INDUSTRY_WEIGHTS.values()]:validate_weights(_weights)
