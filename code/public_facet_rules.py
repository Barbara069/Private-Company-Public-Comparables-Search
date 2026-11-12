"""Facet relevance gates shared by full research and website-only matching.
These gates remove obvious assignment errors; they do not certify facts.
"""
import re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'outputs/global_comps_560'))
from strict_facet_checks import strict_reasons
PROMO=re.compile(r'are you passionate|whether you.re|comes? from all walks|worked (?:their|your) way|visionary entrepreneur|entrepreneur who|exciting opportunity|new restaurant conversion|travel center conversion|career opportunit|we.re hiring|join our team|click here|cookie|privacy policy|all rights reserved|subscribe to|sign up for|your feedback|site navigation',re.I)
PRODUCT=re.compile(r'hamburgers?|burgers?|sandwich|chicken|fries|desserts?|beverages?|soft drinks|coffee|breakfast|software|platform|applications?|devices?|equipment|machinery|components?|chemicals?|pharmaceutical|therapeutic|drug|diagnostic|apparel|footwear|cosmetics?|steel|alumin|cement|paper|semiconductor|vehicles?|aircraft|boats?|food products|insurance products|investment products|loans?|financial products|electricity|natural gas|petroleum|real estate|properties|products? (?:include|consist|such as)|(?:sells?|retails?).{0,100}(?:goods|merchandise|products)',re.I)
OFFER=re.compile(r'\b(?:offers?|offering|provides?|providing|manufactur\w*|design\w*|develop\w*|produces?|producing|sells?|selling|retails?|supplies|supply|distributes?|markets?)\b|menu|portfolio|product (?:range|line)|products (?:include|consist)',re.I)
def acceptable(text,facet,block='MAIN'):
 if not isinstance(text,str) or not 35<=len(text)<=2400 or PROMO.search(text):return False
 if re.search(r'\b(?:Mr\.|Ms\.|chief executive officer|chief financial officer|board of directors|her career|his career)\b',text,re.I):return False

 if block=='MAIN' and facet=='Customer Concentration':
  if not re.search(r'(?:customers?|clients?).{0,100}(?:account(?:ed|s)? for|represent\w*|constitut\w*|contribut\w*|exceed\w*|comprised).{0,100}(?:revenues?|sales)|(?:largest|top|major|single|individual).{0,35}(?:customers?|clients?).{0,100}(?:revenues?|sales)',text,re.I):return False
  if re.search(r'addressable market|purchase.{0,60}(?:suite|solutions|products)|accounts receivable|trade receivable',text,re.I) and not re.search(r'(?:revenue|sales).{0,60}(?:customer|client)|(?:customer|client).{0,90}(?:total revenue|net sales)',text,re.I):return False
  return True
 if block=='MAIN' and facet=='Capital Intensity':
  if re.search(r'repurchas|dividend|general corporate purposes|cash commitments|access to capital markets|financial resources|fund working capital|liquidity needs|funding of general business|capital resources|could adversely|may adversely',text,re.I):return False
 if block=='MAIN' and facet=='Primary Products':
  if re.search(r'open.source software licens|intends? to distribute|competitive factors|third.party software licens|software used internally|intellectual property infringement',text,re.I):return False
 if block=='INDUSTRY':
  if re.search(r'deferred tax|accounting standard|financial statement presentation|fair value hierarchy',text,re.I):return False
  if facet in ['Customer Size','Client Segment','Customer Type'] and re.search(r'enterprise resource planning|\bERP\b',text,re.I) and not re.search(r'enterprise customers|large enterprises|small.{0,20}business|mid.market|large.{0,20}(?:business|employer|organization)',text,re.I):return False
  if facet in ['Pricing Metric','Price point / value proposition','Pricing Power'] and re.search(r'insurance premium|healthcare|fair value|stock option|pension|credit|debt|liabilities',text,re.I):return False
  if facet in ['Revenue Composition','Revenue Structure','Revenue Recurrence','Revenue Source'] and re.search(r'subscription agreement.{0,80}shares|shares.{0,80}subscription|employee subscription|license expense|licensing costs|amortization|deferred tax',text,re.I):return False
  if facet=='AI Exposure' and not re.search(r'(?:offer|provid|integrat|use|develop|deploy|embed|leverag|enable).{0,100}(?:artificial intelligence|machine learning|\bAI\b)|(?:AI|artificial intelligence).{0,60}(?:products|features|platform|tools|capabilities)',text,re.I):return False
  if facet in ['Brand Strength','Pricing Power'] and not re.search(r'brand recognition|brand awareness|brand loyalty|market share|pricing power|price elasticity',text,re.I):return False
  return True
 if facet=='Primary Products':
  if not PRODUCT.search(text):return False
  if not (OFFER.search(text) or re.search(r'learn about.{0,60}(?:burger|sandwich|software|products)|(?:our|its|the company.s) (?:products|software|platform|menu)',text,re.I)):return False
  if re.search(r'menu price|product mix|food cost|sampled|laboratory|quality assurance|animal welfare|processing facilities|preparation and service|supply chain|revenue (?:increas|decreas)|sales (?:increas|decreas)',text,re.I):return False
  return True
 if strict_reasons(text,facet):return False
 if re.search(r'indicate by check mark|interactive data file|rule 405|registrant has submitted|financial accounting standards|fair value hierarchy|level [123] inputs|accounting policies|unobservable inputs',text,re.I):return False
 if facet=='Customer Segment':
  return bool(re.search(r'customer base|customers? (?:include|are|consist)|clients? (?:include|are|consist)|(?:serve|serving|services to).{0,60}(?:consumers?|individuals|businesses|organizations|enterprises)|small.{0,20}business|mid.market|enterprise customers|government customers|retail customers|consumers seeking|individual consumers',text,re.I))
 if facet=='End Markets':
  if re.search(r'self.insur|workers. compensation|health care claims|liability|pension|credit risk|securities|market price',text,re.I):return False
  return bool(re.search(r'end.markets?|industries.{0,100}(?:include|serve)|(?:serve|serving|used in|applications? for).{0,130}(?:industr|consumer|commercial|healthcare|medical|aerospace|automotive|restaurant|residential|retail|government)|restaurant (?:industry|business)|consumer (?:demand|spending)',text,re.I))
 if facet=='Value Chain Position':
  if re.search(r'shortages or interruptions|could disrupt|may disrupt|risk factors|credit|liabilit',text,re.I):return False
  return bool(re.search(r'(?:we|company|group|it).{0,100}(?:manufactur|distribut|retail|franchis|operat|supply|supplies)|(?:is|as) (?:a|an|the).{0,45}(?:manufacturer|distributor|retailer|franchisor|supplier|producer)|original equipment|tier.one|tier.1',text,re.I))
 if facet=='Company Size Category':return bool(re.search(r'(?:approximately|about|over|more than)\s*[\d,]+.{0,20}(?:employees|restaurants|stores|locations)|(?:employs?|workforce).{0,30}\d',text,re.I))
 if facet=='Distribution Channels':
  if re.search(r'joint venture|partnership|distribution to shareholders|dividends|repurchase|share.based',text,re.I):return False
  return bool(re.search(r'sells?.{0,100}(?:through|direct|online)|sales channels?|distribution channels?|direct.to.consumer|e.commerce|online ordering|drive.thr|mobile app|wholesale|retail stores|distribution network',text,re.I))
 if facet=='Delivery Model':return bool(re.search(r'SaaS|software.as.a.service|cloud.based|on.premise|on.site|self.service|managed services|delivery.{0,50}(?:platform|orders|provider|third.party)|(?:orders|products|services).{0,50}deliver|mobile app|drive.thr|dine.in|takeaway|carryout',text,re.I))
 if facet=='Pricing Structure':
  if re.search(r'fair value|unobservable|market price|asset|liabilit|credit facility|interest rate|procurement|purchas.{0,50}supplies|pricing of (?:debt|securit)',text,re.I):return False
  return bool(re.search(r'per.(?:user|employee|seat|transaction|month|year)|fixed.fee|usage.based|cost.plus|pay.as.you.go|pricing (?:model|structure)|royalt\w*.{0,100}(?:percent|%|fee)|fees.{0,80}(?:calculated|based on|percentage)|franchise fee.{0,70}\$',text,re.I))
 if facet=='Recurring Revenue Profile':
  if re.search(r'depreciat|amortiz|useful lives|leasehold improvements|deferred tax|property lease|lease expense',text,re.I):return False
  return bool(re.search(r'recurring (?:revenue|fees|income)|subscription.{0,80}(?:revenue|fees|services)|revenues?.{0,80}(?:subscription|royalt)|royalt\w*.{0,80}(?:sales|revenues?|monthly|annual)|customers?.{0,70}(?:renew|contracts)',text,re.I))
 if facet=='Capital Intensity':
  if re.search(r'independent processors|supplied all|our suppliers|franchisees.{0,80}(?:own|invest)',text,re.I):return False
  return bool(re.search(r'asset.light|asset.heavy|capital.intensive|capital expenditures|capital investments|(?:we|company|group).{0,80}owns?.{0,70}(?:facilit|propert|plant|factories)|our (?:manufacturing|production) facilities',text,re.I))
 if facet=='Labor Intensity':return bool(re.search(r'labo[u]?r.intensive|personnel (?:cost|expens)|employee.{0,30}(?:cost|expens)|skilled (?:workforce|employees)|labor (?:cost|expens)',text,re.I))
 if facet=='Regulatory Exposure':return bool(re.search(r'FDA|food safety|franchise (?:law|regulation)|environmental (?:law|regulation)|regulat.{0,65}(?:food|labor|bank|insur|health|drug|clinical|product|environment|franchis|energy)|(?:business|operations?|products?).{0,90}(?:regulat|licens|approval)|government (?:regulation|approval)',text,re.I))
 if facet=='Competitive Positioning':
  if re.search(r'our ability to|may|could|risk|adverse|adversely|uncertainty',text,re.I):return False
  return bool(re.search(r'market leader|market share|competitive position|leading (?:provider|manufacturer|supplier|operator)|largest (?:provider|manufacturer|supplier|chain)|competes? (?:with|against)',text,re.I))
 if facet=='Product Differentiation':
  if re.search(r'QSCC|purchas|procurement|distribution of food|proprietary paper|operating supplies|credit|securities',text,re.I):return False
  return bool(re.search(r'patented (?:technology|products?|process)|differentiated|unique (?:products?|technology|design|features)|proprietary (?:software|platform|technology)|made.to.order|never.frozen|fresh.{0,25}beef|product.{0,65}(?:specializ|customiz)|specializ.{0,65}(?:hamburger|products|software)',text,re.I))
 if facet=='Company Maturity':
  if re.search(r'credit|loan|facility|line of credit|advertising fund|pension|subsidiary was|fund was',text,re.I):return False
  return bool(re.search(r'(?:company|corporation|group|business|it|we).{0,100}(?:was founded|was incorporated|was established|began operations|commenced operations)|(?:founded|incorporated|established) in (?:18|19|20)\d\d',text,re.I))
 if facet=='Technology Dependence':return bool(re.search(r'rely|reliance|depend.{0,90}(?:technology|systems|software|platform)|cloud.based (?:software|platform)|information technology systems|our (?:software|platform|technology|IT systems)',text,re.I))
 if facet=='Geographic Concentration':return bool(re.search(r'(?:primarily|principally|predominantly|concentrat|exclusively|majority|%|percent).{0,100}(?:United States|Canada|China|India|Europe|Japan|domestic|international|Asia)|(?:United States|Canada|China|India|Europe|Japan|domestic|international|Asia).{0,100}(?:primarily|principally|predominantly|concentrat|exclusively|majority|%|percent)',text,re.I))
 if facet=='Supply Chain Complexity':
  if re.search(r'^shortages or interruptions|our ability to|may disrupt|could disrupt',text,re.I):return False
  return bool(re.search(r'our suppliers|company.s suppliers|sourcing.{0,60}(?:materials|components|ingredients)|(?:we|company).{0,50}(?:purchase|procure|source)|supply chain.{0,60}(?:depend|disrupt|purchas|co.op)|(?:supplier|processor|distributor).{0,80}(?:suppl|contract|network)|contracts for the purchase',text,re.I))
 if facet=='Contract Duration':return bool(re.search(r'(?:customers?|clients?|franchis|supply agreement|service agreement).{0,130}(?:\d+.year|years|months|long.term|short.term|annual|multi.year|at.will)|(?:\d+.year|multi.year|annual).{0,70}(?:customer|client|franchis|service agreement)',text,re.I))
 if facet=='IP Dependence':return bool(re.search(r'our.{0,80}(?:patent|intellectual property|trademark)|company.{0,80}(?:patent|intellectual property|trademark)|(?:patents?|intellectual property).{0,90}(?:protect|important|depend|material)',text,re.I))
 if facet=='Brand Dependence':return bool(re.search(r'our brands?|company.s brands?|brand (?:reputation|recognition|loyalty)|owns?.{0,70}brands?|trademarks?.{0,70}(?:protect|registered|important)',text,re.I))
 if facet=='Primary Services' and not re.search(r'(?:provid|offer|deliver|perform|include|operat|franchis).{0,100}(?:services?|restaurants?|payroll|consulting|logistics|banking)|services?.{0,80}(?:include|consist)',text,re.I):return False
 if facet=='Core Business Activity' and re.search(r'each .{0,35}restaurant offers|menu (?:includes|features|specializ)',text,re.I) and not re.search(r'operat|franchis|primarily engaged',text,re.I):return False
 if facet=='Core Business Activity' and not re.search(r'\b(?:we|company|group|it|business|operations|restaurants?)\b.{0,120}(?:operat|engag|provid|offer|manufactur|develop|franchis|consist)|primarily engaged',text,re.I):return False
 if facet in ['Primary Services','Core Business Activity','Business Model','Value Chain Position'] and re.search(r'\b(?:profit|expenses?|margin|cost of sales|accounting standard)\b',text,re.I):return False
 if facet in ['Geography Served','Geographic Concentration'] and re.search(r'headquartered|incorporated in|registered office',text,re.I) and not re.search(r'serves?|sales|customers|operates|markets across',text,re.I):return False
 if facet=='Contract Duration' and re.search(r'credit facility|term loan|senior notes|borrowings',text,re.I):return False
 return True
def specificity(text,facet):
 score=0
 if re.search(r'primarily engaged|business consists|our products include|menu (?:specializ|features|includes)|products (?:include|consist)|company (?:is|operates|provides|manufactures)',text,re.I):score+=5
 if facet=='Primary Products':score+=min(len(PRODUCT.findall(text)),8)
 if facet in ['Core Business Activity','Business Model'] and re.search(r'primarily engaged|business consists|company is engaged|operating, developing and franchising',text,re.I):score+=15
 if re.search(r'\b(?:may|could|risk|adversely|uncertain)\b',text,re.I):score-=3
 if re.search(r'\b(?:historically|formerly|prior to|used to)\b',text,re.I):score-=3
 return score
