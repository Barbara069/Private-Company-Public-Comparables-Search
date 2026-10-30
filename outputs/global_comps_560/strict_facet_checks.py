"""High precision checks that prevent obvious extraction noise being used as facts."""
import re
FINITE=re.compile(r'\b(?:is|are|was|were|has|have|can|will|include|includes|sell|sells|lease|leases|offer|offers|provide|provides|operate|operates|manufacture|manufactures|develop|develops|design|designs|supply|supplies|serve|serves|market|markets|generate|generates|charge|charges|specialize|specializes|focus|focuses|engage|engages|own|owns|support|supports|distribute|distributes|earn|earns|receive|receives|founded|established|incorporated)\b',re.I)
BIO=re.compile(r'\b(?:Mr\.|Ms\.|Mrs\.|Dr\.|M\.B\.A\.|B\.A\.|joined (?:the |our )?company|joined \w+ in|served as|her career|his career|chief executive officer|chief financial officer|senior vice president|board of directors|received (?:a|an) (?:degree|B\.|M\.))',re.I)
PRIVACY=re.compile(r'personal information|personal data|sell or share|do not sell|GPC will|privacy|cookies|consent|unsubscribe|all rights reserved|terms of use|newsletter|receive notifications via email|email alerts|site navigation|opens in new tab',re.I)
def strict_reasons(t,facet):
 t=t or '';r=[]
 if PRIVACY.search(t):r.append('PRIVACY_OR_SUBSCRIPTION_BOILERPLATE')
 if not FINITE.search(t):r.append('NO_FINITE_COMPANY_CLAIM')
 if BIO.search(t) and facet not in ['Company Maturity']:r.append('PERSON_BIOGRAPHY_NOT_CORPORATE_FACET')
 if facet in ['Primary Products','Primary Services','Core Business Activity','Business Model','Revenue Model'] and re.search(r'our (?:own )?(?:team|associates|employees|sales force)|provide our sales force|sales force with intensive training|company.wide health and safety|employee wellness|wellness activities',t,re.I) and not re.search(r'clients.{0,25}employees|customers.{0,25}employees|client employees',t,re.I):r.append('INTERNAL_WORKFORCE_NOT_CUSTOMER_OFFERING')
 if facet=='Revenue Model':
  if re.search(r'\bcommissions?\b',t,re.I) and not re.search(r'\b(?:earn\w*|revenue|income|paid|received|charges?|fees?)\b',t,re.I):r.append('COMMISSION_IS_NOT_EARNED_REVENUE')
  rev=re.search(r'\b(?:revenues?|income|earn\w*|charg\w*|paid|paying|payments? from)\b',t,re.I)
  mechanism=re.search(r'\b(?:subscriptions?|fees?|commissions?|royalt\w*|premiums?|rent\w*|leasing|licens\w*|franchis\w*)\b',t,re.I)
  sales=re.search(r'\b(?:we|company|group|it)\b.{0,100}\b(?:sells?|leases?|rents?|franchises?)\b',t,re.I) or re.search(r'\bsales of\b.{0,60}(?:products|goods|services|properties|equipment|software)',t,re.I)
  if not ((rev and mechanism) or sales or re.search(r'recurring (?:fees|subscriptions)|subscription.based services|rental income|insurance premiums',t,re.I)):r.append('NO_EXPLICIT_MONETIZATION_CLAIM')
 if facet=='Core Business Activity' and re.search(r'\b(?:was incorporated with an object|formerly|historically|prior to|used to)\b',t,re.I):r.append('HISTORICAL_NOT_CURRENT_BUSINESS')
 if facet=='Business Model' and re.search(r'we don.t sell direct|our customers.{0,40}(?:manufactur|bank|insur)',t,re.I):r.append('CHANNEL_OR_CLIENT_MODEL_NOT_CORPORATE_MODEL')
 return r
