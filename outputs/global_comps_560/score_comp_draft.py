"""Transparent draft facet scoring; unknown evidence remains unknown."""
import collections,csv,json,pathlib,re,sys
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from build_comp_draft import P,O,load,save,sentences,encode,norm
PATTERNS={
'Primary Products':r'product|software|equipment|platform|device|manufactur|offers? |portfolio|food|beverage|drug|chemical|component',
'Primary Services':r'services?|provides?|support|consult|maintenance|management|payroll|outsourc|logistics',
'Core Business Activity':r'operat|manufactur|develop|distribut|specializ|provid|design|market|business|restaurant|bank',
'Customer Segment':r'customers?|clients?|businesses|organizations|enterprises|consumers|households|government|employers|patients|homeowners',
'End Markets':r'industries|industrials?|healthcare|automotive|aerospace|defense|commercial|residential|retail|education|hospital|financial institutions|construction|data cent',
'Business Model':r'manufactur|franchis|subscription|software.as.a.service|saas|marketplace|distribut|retail|bank|insurance|leasing|consult',
'Revenue Model':r'subscription|fees?|commissions?|royalt|licens|transaction|franchis|rental|leasing|sells? |sales of|premiums',
'Value Chain Position':r'manufactur|original equipment|\boem\b|distribut|wholesale|retail|supplier|reseller|upstream|downstream|producer|operator',
'Geography Served':r'united states|north america|europe|asia|global|worldwide|international|canada|countries|united kingdom|china|japan|australia',
'Company Size Category':r'(?!)',
'Product Specialization':r'specializ|niche|diversif|broad range|comprehensive|focused on|focuses on',
'Customer Concentration':r'customer concentration|largest customer|top .{0,12}customer|concentrated customer|diversified customer',
'Distribution Channels':r'direct sales|sales force|dealer|partner|distributor|online|e.commerce|retail store|broker|independent agent',
'Delivery Model':r'cloud|on.premise|on.site|online|physical|digital|saas|remote|software.as.a.service',
'Pricing Structure':r'per.user|per.employee|fixed.fee|usage.based|price per|pricing|pay.as.you.go',
'Recurring Revenue Profile':r'recurring revenue|subscription|renewal|repeat purchase|long.term contract',
'Capital Intensity':r'asset.light|asset.heavy|manufacturing facilit|manufacturing plant|production facilit|owns and operates|capital.intensive',
'Labor Intensity':r'labor.intensive|labour.intensive|skilled workforce|personnel expenses|staffing|professional employees',
'Regulatory Exposure':r'regulat|\bfda\b|compliance|licensing requirements|medicare|medicaid|insurance authority',
'Competitive Positioning':r'market leader|leading provider|market share|competitive position|largest provider|largest manufacturer',
'Product Differentiation':r'proprietary|differentiat|patented|unique technology|specialized|customiz',
'Customer Switching Costs':r'switching cost|switch providers|customer retention|migration cost|integrated workflow',
'Revenue Cyclicality':r'cyclical|seasonal|cyclicality|economic cycle|commodity price|recession',
'Company Maturity':r'founded|established|incorporated|since [12][09][0-9]{2}',
'Technology Dependence':r'technology|software|platform|algorithm|data analytics|automation|digital|artificial intelligence',
'Geographic Concentration':r'primarily in|principally in|predominantly in|concentrated in|exclusively in',
'Supply Chain Complexity':r'supply.chain|sourcing|suppliers|supply network|logistics network',
'Contract Duration':r'long.term contract|multi.year|short.term contract|contract duration|annual contract|month.to.month',
'IP Dependence':r'patent|intellectual property|proprietary technolog|licensing technolog',
'Brand Dependence':r'brands?|trademark|franchise',
}
CATS={
'Customer Segment':{'B2B':r'business customers|enterprise|organizations|employers|small businesses|corporate customers|institutional clients','B2C':r'consumers|households|shoppers|homeowners|patients|individual customers|retail customers','B2G':r'government agencies|government customers|public sector'},
'Business Model':{'manufacturing':r'manufactur','franchise':r'franchis','SaaS':r'saas|software.as.a.service|cloud.based software','marketplace':r'marketplace','distribution':r'distribut|wholesale','retail':r'retailer|retailing|retail store','bank':r'banking|commercial bank','insurance':r'insurance','consulting':r'consult','leasing':r'leasing|rental'},
'Revenue Model':{'subscription':r'subscription','fees':r'\bfees?\b','commission':r'commission','royalty':r'royalt','licensing':r'licens','transaction':r'transaction','franchise':r'franchis','rent':r'rental|leasing','product sales':r'sells? |sales of|product sales','insurance premium':r'premiums'},
'Value Chain Position':{'manufacturer':r'manufactur','distributor':r'distribut|wholesale','retailer':r'retailer|retailing|retail store','producer':r'producer|production','operator':r'operator|operates','supplier':r'supplier|supplies'},
'Delivery Model':{'cloud':r'cloud|saas|software.as.a.service','on-premise':r'on.premise','on-site':r'on.site','online':r'online|digital','physical':r'physical'},
'Geography Served':{'US':r'united states|\bU\.S\.','North America':r'north america','Europe':r'europe','Asia':r'asia','Global':r'global|worldwide|international','Canada':r'canada','UK':r'united kingdom','China':r'china','Japan':r'japan','Australia':r'australia'},
}
INDUSTRY={'SOFTW':r'payroll software|human capital management|enterprise software|software.as.a.service|saas|cloud.based software', 'MEALS':r'restaurant|quick.service|fast.food|dining|hotels?|resorts?|casino', 'BANKS':r'commercial bank|banking services|deposit.{0,25}loan', 'INSUR':r'insurance|underwriting|policyholders', 'DRUGS':r'pharmaceutical|biopharmaceutical|biotechnology|clinical.stage', 'MEDEQ':r'medical devices|surgical instruments|diagnostic equipment', 'CHIPS':r'semiconductor|integrated circuit|microchip', 'TRANS':r'railroad|freight|trucking|shipping|airline', 'OIL':r'oil and gas|petroleum|oilfield|drilling', 'UTIL':r'electric utilit|natural gas utilit|electricity distribution|water utilit', 'RTAIL':r'retailer|retail stores|department stores', 'TELCM':r'telecommunication|wireless network|broadband', 'HLTH':r'healthcare services|health care services|hospitals?|veterinary', 'AERO':r'aircraft|aerospace', 'MACH':r'industrial machinery|air conditioning|heating equipment|manufacturing equipment'}
def ff_infer(text):
    ranked=sorted(((len(re.findall(p,text,re.I)),k) for k,p in INDUSTRY.items()),reverse=True)
    return ranked[0][1] if ranked and ranked[0][0]>=2 and (len(ranked)<2 or ranked[0][0]>ranked[1][0]) else None
def facets(quotes):
    out={}
    for name,pattern in PATTERNS.items():
        choices=[q for q in quotes if re.search(pattern,q['text'],re.I)]
        if name=='Geography Served':choices=[q for q in choices if re.search(r'operat|serves?|customers?|across|markets?|worldwide|global|international|sales',q['text'],re.I) and not re.search(r'headquarter|based in|based company',q['text'],re.I)]
        choices.sort(key=lambda q:(-len(re.findall(pattern,q['text'],re.I)), -min(len(q['text']),500)))
        selected=choices[:2];text=' '.join(q['text'] for q in selected)
        tags=sorted(k for k,p in CATS.get(name,{}).items() if re.search(p,text,re.I))
        out[name]=dict(text=text,tags=tags,urls='; '.join(dict.fromkeys(q['url'] for q in selected)),evidence=selected,status='SOURCE_SENTENCE_MATCH_REQUIRES_REVIEW' if selected else 'UNKNOWN')
    return out
def main():
    ts=load(O/'target_allowed_profiles.json');cs=load(O/'candidate_reference.json');retr=load(O/'retrieval_top25.json')
    profiles={r['Instrument']:r for r in load(O/'shortlist_profiles.json')} if (O/'shortlist_profiles.json').exists() else {}
    cby={r['candidate_ric']:r for r in cs};used={r['candidate_ric'] for r in retr}
    # Enrich the retained shortlist only, rather than rerun discovery with evaluation labels.
    for ric in sorted(used):
        c=cby[ric];r=profiles.get(ric,{})
        if r.get('TR.BUSINESSSUMMARY'):
            c['description']=r['TR.BUSINESSSUMMARY'];c['candidate_name']=r.get('TR.COMMONNAME') or c['candidate_name'];c['description_source']='LSEG';c['source_link']='https://www.lseg.com/en/data-analytics';c['source_locator']='TR.BusinessSummary; Instrument='+ric;c['description_identity_match']='LSEG_DIRECT'
        c.update({'public_revenue_usd':r.get('TR.TOTALREVENUE'),'public_ebitda_usd':r.get('TR.EBITDA'),'public_debt_usd':r.get('TR.TOTALDEBT'),'financial_period_end':r.get('TR.TOTALREVENUE.DATE'),'financial_period':r.get('TR.TOTALREVENUE.FPERIOD'),'financial_currency':r.get('TR.TOTALREVENUE.CURRENCY'),'public_TRBC_industry':r.get('TR.TRBCINDUSTRY')})
    tby={t['target_id']:t for t in ts};tf={t['target_id']:facets(t['quotes']) for t in ts}
    cf={ric:facets([dict(text=s,url=cby[ric]['source_link'],file=cby[ric]['source_locator']) for s in sentences(cby[ric]['description'])]) for ric in sorted(used)}
    weights=load(P/'prepared/Scoring_Weights.json');wm={r['facet']:r['proposed_weight'] for r in weights}
    for w in weights:
        w['score_scale']='Continuous 0–100. Explicit-category Jaccard for categorical facets; normalized-embedding cosine for text facets; FF49 same-industry binary. UNCALIBRATED.'
        w['note']='Proposed baseline; overlapping facets are not independent. Missing facts remain UNKNOWN. Size is unscored until original unit/period is verified. No evaluation-label fitting.'
    names=list(PATTERNS);positive=[n for n in names if wm.get(n,0)>0]
    texts=sorted(set(v['text'] for f in list(tf.values())+list(cf.values()) for n,v in f.items() if n in positive and v['text']))
    emb=encode(texts,'facet_embedding');ix={text:i for i,text in enumerate(texts)}
    # TF-IDF here supplies an interpretable independent lexical check beside cosine.
    vect=TfidfVectorizer(stop_words='english',ngram_range=(1,2),max_features=90000,sublinear_tf=True);lex=vect.fit_transform(texts)
    ranges=load(P/'prepared/FF49_SIC_Mapping.json')
    def publicff(c):
        try:sic=int(c['wrds_sic'])
        except (TypeError,ValueError):return None
        return next((r['ff49'] for r in ranges if r['sic_from']<=sic<=r['sic_to']),None)
    bytarget=collections.defaultdict(list)
    for r in retr:bytarget[r['target_id']].append(r)
    results=[];detail=[];coverage=[];targetfacet=[];ffrows=[]
    ffmed={r['Fama and French 49 Industries - Description']:r for r in load(P/'prepared/FF49_Latest_49.json')}
    for t in ts:
        tid=t['target_id'];inferred=ff_infer(t['text']);ff=ffmed.get(inferred,{})
        ffrows.append({'Target ID':tid,'Target Name':t['target_name'],'Website-inferred FF49':inferred,'Classification Status':'RULE_INFERENCE_UNVERIFIED' if inferred else 'UNKNOWN; do not copy hidden SIC','FF49 Benchmark Date':ff.get('Date'),'Industry EV Multiple Median':ff.get('Enterprise Value Multiple_Median'),'Industry Net Margin Median':ff.get('Net Profit Margin_Median'),'Industry Debt EBITDA Median':ff.get('Total Debt/EBITDA_Median'),'Benchmark Source':'Provided WRDS FF49 workbook','Source Link':'https://drive.google.com/drive/folders/1tcvtTs4eQcA9Cjd0eoq2GlUW_k5LUpAH','Note':'Context only, not a valuation prediction; negative industry multiples may be economically unsuitable. No industry factor return used.'})
        for n in names:
            v=tf[tid][n];targetfacet.append({'Target ID':tid,'Target Name':t['target_name'],'Facet':n,'Observed Categories':'; '.join(v['tags']),'Evidence Status':v['status'],'Source Text':v['text'][:1500] or None,'Source Link':v['urls'] or None,'Evidence Role':'TARGET_OFFICIAL_WEBSITE_ONLY','Extraction':'Keyword-selected source sentences; not a verified structured fact','Proposed Weight':wm.get(n,0)})
        scored=[]
        for r in bytarget[tid]:
            ric=r['candidate_ric'];c=cby[ric]
            if norm(c['candidate_name'])==norm(t['target_name']):continue
            ds=[];weighted=0.;observed=0.;known=0
            for n in positive:
                a=tf[tid][n];b=cf[ric][n];w=wm[n];sc=None;cos=None;lx=None;method='UNKNOWN_NOT_SCORED'
                if a['text'] and b['text']:
                    ai=ix[a['text']];bi=ix[b['text']];cos=float(np.dot(emb[ai],emb[bi]));lx=float((lex[ai]@lex[bi].T).toarray()[0,0])
                    if n in CATS:
                        aa=set(a['tags']);bb=set(b['tags'])
                        if aa and bb:sc=100*len(aa&bb)/len(aa|bb);method='EXPLICIT_CATEGORY_JACCARD'
                    else:
                        sc=100*max(0.,min(1.,cos));method='SOURCE_TEXT_EMBEDDING_COSINE_UNCALIBRATED'
                    if sc is not None:observed+=w;weighted+=w*sc;known+=1
                ds.append({'Target ID':tid,'Target Name':t['target_name'],'Candidate RIC':ric,'Candidate Name':c['candidate_name'],'Facet':n,'Target Categories':'; '.join(a['tags']),'Target Source Text':a['text'][:1100] or None,'Target Source Link':a['urls'] or None,'Public Categories':'; '.join(b['tags']),'Public Source Text':b['text'][:1100] or None,'Public Source Link':b['urls'] or None,'Public Source Field':c['source_locator'],'Facet Similarity Percent':round(sc,2) if sc is not None else None,'Proposed Weight':w,'Observed Weight':w if sc is not None else None,'Contribution Percent Points':None,'Scoring Method':method,'Semantic Cosine':round(cos,4) if cos is not None else None,'Lexical Cosine':round(lx,4) if lx is not None else None,'Verification':'AUTOMATED_DRAFT_NOT_HUMAN_VERIFIED'})
            pf=publicff(c);ffs=100. if inferred and pf and inferred==pf else 0. if inferred and pf else None
            fw=wm.get('FF49 Industry',.02)
            if ffs is not None:observed+=fw;weighted+=fw*ffs;known+=1
            ds.append({'Target ID':tid,'Target Name':t['target_name'],'Candidate RIC':ric,'Candidate Name':c['candidate_name'],'Facet':'FF49 Industry','Target Categories':inferred,'Target Source Text':'Website keyword rule. See Target Facets; no hidden target SIC loaded.','Target Source Link':t['website'],'Public Categories':pf,'Public Source Text':'WRDS public candidate SIC: '+str(c.get('wrds_sic')),'Public Source Link':'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Siccodes49.zip','Public Source Field':c.get('wrds_gvkey'),'Facet Similarity Percent':ffs,'Proposed Weight':fw,'Observed Weight':fw if ffs is not None else None,'Contribution Percent Points':None,'Scoring Method':'SAME_INFERRED_FF49_BINARY_UNVERIFIED_TARGET_LABEL','Semantic Cosine':None,'Lexical Cosine':None,'Verification':'INFERENCE_REVIEW_REQUIRED'})
            score=weighted/observed if observed else None
            if not observed:continue
            for d in ds:
                if d['Facet Similarity Percent'] is not None:d['Contribution Percent Points']=round(d['Proposed Weight']*d['Facet Similarity Percent']/observed,4)
            row={'Target ID':tid,'Target Name':t['target_name'],'Rank':None,'Candidate RIC':ric,'Candidate Name':c['candidate_name'],'Similarity Percent':round(score,2) if score is not None else None,'Weighted Evidence Coverage':round(observed,4),'Scored Facets':known,'Status':'DRAFT_REQUIRES_HUMAN_BUSINESS_REVIEW' if observed>=.5 and r['retrieval_semantic_cosine']>=.5 else 'WEAK_OR_INCOMPLETE_EVIDENCE_REVIEW','Listing Country':c['listing_country'],'Listing Status':c['listing_status'],'Candidate Source':c['description_source'],'Source Text':c['description'][:2500],'Source Link':c['source_link'],'Source Field':c['source_locator'],'Target Website':t['website'],'Retrieval Semantic Cosine':r['retrieval_semantic_cosine'],'Retrieval Lexical Cosine':r['retrieval_lexical_cosine'],'Segment Warning':'WHOLE_COMPANY_VS_SEGMENT_ELIGIBILITY_NOT_VALIDATED; do not automatically aggregate valuation','Score Meaning':'Weighted observed-facet text/category similarity; not probability, valuation accuracy, or validated comp quality'}
            scored.append((row,ds))
        for row,ds in scored:row['Evidence Adjusted Ranking Index']=round((row['Similarity Percent'] or 0)*row['Weighted Evidence Coverage']**.5,4)
        scored.sort(key=lambda x:x[0]['Evidence Adjusted Ranking Index'],reverse=True)
        selected=scored[:10]
        for rank,(row,ds) in enumerate(selected,1):row['Rank']=rank;results.append(row);detail.extend(ds)
        coverage.append({'Target ID':tid,'Target Name':t['target_name'],'Website':t['website'],'Website Source Sentences':len(t['quotes']),'Candidate Rows':len(selected),'Reviewable Draft Rows':sum(x[0]['Status']=='DRAFT_REQUIRES_HUMAN_BUSINESS_REVIEW' for x in selected),'Status':'DRAFT_CANDIDATES_NOT_VALIDATED' if selected else 'ABSTAIN_INSUFFICIENT_ALLOWED_WEBSITE_OR_SCORABLE_FACET_EVIDENCE','Reason':'Only website business text and instructor three figures permitted. Unknown units prevent financial size scoring.','Human Review':'PENDING'})
    selectedrics={r['Candidate RIC'] for r in results};candidate_rows=[cby[r] for r in sorted(selectedrics)]
    # Supplied databases enrich PUBLIC candidate output only, after ranking is complete.
    mapping={r['ric']:r for r in load(P.parent/'lseg_downloads/target_mapping_560.json')}
    cap={r['company_id']:r for r in load(P/'prepared/Targets_560.json')}
    wr={r['company_id']:r for r in load(P/'prepared/WRDS_Matched_Latest.json')}
    catalog={r['gvkey']:r for r in load(P/'web_evidence/wrds_api/company_catalog_all.json')}
    for c in candidate_rows:
        m=mapping.get(c['candidate_ric'],{});cid=m.get('company_id');a=cap.get(cid,{});w=wr.get(cid,{})
        identity_ok=bool(cid) and 'REVIEW_REQUIRED' not in m.get('mapping_status','')
        c['Provided CapIQ Description']=a.get('business_description') if identity_ok else None
        c['CapIQ Source Link']=a.get('source_url') if identity_ok else None
        c['CapIQ Source Location']=a.get('source_location') if identity_ok else None
        c['Provided WRDS Ratio Date']=w.get('Date') if identity_ok else None
        c['Provided WRDS EV Multiple']=w.get('Enterprise Value Multiple') if identity_ok else None
        c['Provided WRDS Net Margin']=w.get('Net Profit Margin') if identity_ok else None
        c['WRDS Source Link']='https://drive.google.com/drive/folders/1tcvtTs4eQcA9Cjd0eoq2GlUW_k5LUpAH' if identity_ok and w else None
        c['WRDS Description']=catalog.get(c.get('wrds_gvkey'),{}).get('busdesc')
        c['WRDS Description Link']=catalog.get(c.get('wrds_gvkey'),{}).get('_source_url')
        c['Financial Use Note']='PUBLIC CANDIDATE CONTEXT ONLY. USD base units; FY0 latest annual, not LTM. Financial-period metadata may be missing. EBITDA not an economically suitable bank/insurer metric. No financial-size score with unconfirmed instructor units.'
    save('Comp_Results',results);save('Facet_Scores',detail);save('Target_Status',coverage);save('Target_Facets',targetfacet);save('Candidate_Data',candidate_rows);save('FF49_Context',ffrows);save('Weights',weights)
    publicfacets=[]
    for ric in sorted(selectedrics):
        for name,v in cf[ric].items():publicfacets.append({'Candidate RIC':ric,'Candidate Name':cby[ric]['candidate_name'],'Facet':name,'Categories':'; '.join(v['tags']),'Evidence Status':v['status'],'Source Text':v['text'][:1800] or None,'Source Link':v['urls'] or None,'Source Field':cby[ric]['source_locator']})
    save('Public_Facets',publicfacets)
    stats={'targets':len(ts),'targets_with_drafts':sum(r['Candidate Rows']>0 for r in coverage),'targets_abstained':sum(r['Candidate Rows']==0 for r in coverage),'ranked_pairs':len(results),'distinct_public_candidates':len(selectedrics),'facet_score_rows':len(detail),'global_listed_security_records':len(load(O/'listed_universe.json')),'global_issuer_descriptions_screened':len(cs),'human_verified_pairs':0,'forecast_status':'DEFERRED_UNTIL_USER_REVIEWS_COMPS','model':'sentence-transformers/all-MiniLM-L6-v2','status':'AUTOMATED_EVIDENCE_LINKED_DRAFT; NOT FINAL_VALIDATED_COMPS'}
    (O/'stats.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats),flush=True)
if __name__=='__main__':main()
