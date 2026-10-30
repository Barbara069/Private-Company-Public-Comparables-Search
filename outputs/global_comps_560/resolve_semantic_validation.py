"""Conservative interpretation of NLI, with source/date/scope qualifications.
No NLI contradiction is promoted to a verified factual error automatically.
"""
import collections,csv,hashlib,json,pathlib,re,sys
P=pathlib.Path(__file__).resolve().parent;O=P/'semantic_validation_20261028';I=P/'multisource_audit_20261028'
def load(p):return json.loads(pathlib.Path(p).read_text())
def dump(name,rows):
    (O/(name+'.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2,default=str))
    if isinstance(rows,list) and rows and isinstance(rows[0],dict):
        cols=list(dict.fromkeys(k for r in rows for k in r))
        with (O/(name+'.csv')).open('w') as f:w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
def events(text):
    out=collections.defaultdict(set)
    for m in re.finditer(r'\b(founded|established|incorporated)\b[^.!?;\n]{0,45}?\b((?:18|19|20)\d{2})\b',text,re.I):
        event='INCORPORATION' if m[1].lower()=='incorporated' else 'FOUNDING_OR_ESTABLISHMENT';out[event].add(m[2])
    return out
def eventcheck(a,b):
    aa=events(a);bb=events(b);shared=set(aa)&set(bb);diff=[f'{k}: A={sorted(aa[k])}, B={sorted(bb[k])}' for k in shared if not aa[k]&bb[k]]
    distinct=bool(aa and bb and not shared)
    return '; '.join(diff),distinct
def main(partial=False):
    ss=load(O/'Source_Statements.json');sby={r['Statement ID']:r for r in ss};pairs=load(O/'Source_Pairs.json');base=load(I/'Facet_Cross_Check.json');pred={}
    for line in (O/'nli_predictions.jsonl').read_text().splitlines():
        try:r=json.loads(line);pred[r['key']]=r
        except json.JSONDecodeError:pass
    manual={r['Pair ID']:r for r in load(O/'Manual_Adjudications.json')} if (O/'Manual_Adjudications.json').exists() else {}
    badstatements={r['Statement ID']:r for r in load(O/'Statement_Adjudications.json')} if (O/'Statement_Adjudications.json').exists() else {}
    bygroup=collections.defaultdict(list);statementgroups=collections.defaultdict(list)
    for r in ss:statementgroups[r['Entity Role'],r['Entity ID'],r['Facet']].append(r)
    results=[];review=[]
    for p in pairs:
        a=sby[p['Statement A ID']];b=sby[p['Statement B ID']];texta=a['Statement Text'];textb=b['Statement Text'];q=pred.get(p['NLI Job Key']);f=None;back=None;raw=None
        numeric,distinctevent=eventcheck(texta,textb) if p['Facet']=='Company Maturity' else ('',False)
        datestatus='BOTH_SOURCE_DATES_KNOWN' if all(re.match(r'^\d{4}-\d{2}-\d{2}$',str(p[k]) or '') for k in ['Source A Date','Source B Date']) else 'ONE_OR_BOTH_SOURCE_DATES_UNKNOWN'
        if datestatus=='BOTH_SOURCE_DATES_KNOWN' and p['Source A Date']!=p['Source B Date']:datestatus='DIFFERENT_DOCUMENT_DATES; FACT_PERIOD_ALIGNMENT_NOT_ESTABLISHED'
        if p['Initial Status']=='EXACT_SAME_TEXT':status='EXACT_SAME_TEXT';why='两份选取文本相同；转载或同一上游供应商不构成独立事实验证。'
        elif p['Initial Status']=='NON_ENGLISH_NEEDS_TRANSLATION':status='NON_ENGLISH_NEEDS_TRANSLATION';why='Selected text requires translation before this English-language semantic model can compare it.'
        elif not q:status='PENDING_NLI';why='语义模型尚未完成此组比较。'
        else:
            f=q['reverse'] if p['Reversed Versus Job'] else q['forward'];back=q['forward'] if p['Reversed Versus Job'] else q['reverse'];cmax=max(f[0],back[0]);cmin=min(f[0],back[0]);raw=cmax
            if q.get('possibly_truncated'):status='CONTEXT_TOO_LONG_REVIEW';why='原文超过模型上下文；不能把截断后的结果当作完整核验。'
            elif distinctevent:status='DIFFERENT_EVENT_DEFINITIONS';why='一方描述成立/创办，另一方描述法律注册；不是同一个日期概念，不能直接认定矛盾。'
            elif numeric:status='NUMERIC_EVENT_DISAGREEMENT_REVIEW';why='同类成立日期表述出现不同年份；需核对主体是否为同一法律实体、品牌或前身。'
            elif (cmin>=.8 and cmax>=.9) or (cmax>=.97 and cmin>=.5):status='HIGH_NLI_CONTRADICTION_REVIEW';why='双向语义模型提示冲突；尚需核对实体、业务分部、时期及否定/排他条件，不自动判成事实错误。'
            elif cmax>=.85:status='POSSIBLE_CONTRADICTION_OR_SCOPE_REVIEW';why='模型一方向提示冲突，尚不能排除不同范围、互补事实或模型误判。'
            elif min(f[1],back[1])>=.8:status='SEMANTICALLY_ALIGNED_MODEL';why='双向推断支持两段表述语义一致；这是文本一致性支持，不是现实真伪的独立验证。'
            elif max(f[1],back[1])>=.85 and cmax<.15:status='ONE_WAY_SUPPORT_DETAIL_OR_SCOPE';why='一段支持另一段，反向未必成立；可能是一方更具体、另一方更概括，不是直接矛盾。'
            elif min(f[2],back[2])>=.65:status='COMPLEMENTARY_OR_DIFFERENT_CLAIMS_UNRESOLVED';why='两段未形成互相否定；可能互补，也可能描述了不同事实/分部。不能仅因措辞不同判矛盾。'
            else:status='SEMANTIC_RELATION_UNCERTAIN';why='模型关系不明确，保留双方原文，不强行合并结论。'
        # Numeric disagreements are visible even when the general-language model misses arithmetic.
        if numeric and status not in ('PENDING_NLI','CONTEXT_TOO_LONG_REVIEW'):status='NUMERIC_EVENT_DISAGREEMENT_REVIEW';why='同类创办/成立年份不同；未核对前身、品牌、法律实体前不确认哪方错误。'
        if distinctevent and status!='PENDING_NLI':status='DIFFERENT_EVENT_DEFINITIONS';why='创办/成立与法律注册属于不同事件；该日期差别本身不构成矛盾。'
        if p['Pair ID'] in manual:
            m=manual[p['Pair ID']];status=m['Verdict'];why=m['Reason']
        bad=[badstatements[k] for k in [p['Statement A ID'],p['Statement B ID']] if k in badstatements]
        if bad:status=next((x['Verdict'] for x in bad if x['Verdict'].startswith('REVIEWED_')),bad[0]['Verdict']);why='; '.join(x['Reason'] for x in bad)
        needs=status not in ('EXACT_SAME_TEXT','SEMANTICALLY_ALIGNED_MODEL','ONE_WAY_SUPPORT_DETAIL_OR_SCOPE','DIFFERENT_EVENT_DEFINITIONS','REVIEWED_COMPATIBLE_DIFFERENT_SCOPE','REVIEWED_EXTRACTION_SUBJECT_ERROR','REVIEWED_FACET_RELEVANCE_ERROR','EXCLUDED_MARKUP_NOT_BUSINESS_PROSE')
        row={'Pair ID':p['Pair ID'],'Entity Role':p['Entity Role'],'Entity ID':p['Entity ID'],'Company Name':p['Company Name'],'Facet':p['Facet'],'Verdict':status,'Reason':why,'Source A':p['Source A'],'Text A':texta,'Source A Link':p['Source A Link'],'Source A Date':p['Source A Date'],'Source B':p['Source B'],'Text B':textb,'Source B Link':p['Source B Link'],'Source B Date':p['Source B Date'],'Date Alignment':datestatus,'Event Year Difference':numeric or None,'Same Source Family':p['Same Source Family'],'Shared Upstream Vendor':p['Same Upstream Vendor'],'A to B Contradiction Score':round(f[0],6) if f else None,'B to A Contradiction Score':round(back[0],6) if back else None,'A to B Entailment Score':round(f[1],6) if f else None,'B to A Entailment Score':round(back[1],6) if back else None,'Raw Model Score Note':'Uncalibrated model class score, not probability that a fact is wrong','Needs Further Review':needs,'Manual Adjudication':p['Pair ID'] in manual or any(x['Verdict'].startswith('REVIEWED_') for x in bad),'Evidence A ID':p['Evidence A ID'],'Evidence B ID':p['Evidence B ID']}
        results.append(row);bygroup[p['Entity Role'],p['Entity ID'],p['Facet']].append(row)
        if 'CONTRADICTION' in status or 'DISAGREEMENT' in status or status.startswith('REVIEWED_'):review.append(row)
    statusrows=[];companies=collections.defaultdict(list)
    for r in base:
        key=(r['Entity Role'],r['Entity ID'],r['Facet']);pr=bygroup[key];st=statementgroups[key];counts=collections.Counter(x['Verdict'] for x in pr);observed_ids=set(x['Evidence ID'] for x in st)
        original_ids=set()
        for k,v in r.items():
            if k.endswith(' Evidence IDs') and v:original_ids.update(v.split('; '))
        lost=len(original_ids-observed_ids)
        unresolved=sum(x['Needs Further Review'] for x in pr);confirmed=[x for x in pr if x['Verdict']=='REVIEWED_STATEMENT_CONFLICT'];pending=counts['PENDING_NLI']
        probable=[x for x in pr if 'CONTRADICTION' in x['Verdict'] or 'DISAGREEMENT' in x['Verdict']]
        if not st:status='NO_USABLE_FACET_TEXT';why='当前填值没有足够可用原文，无法判定跨来源一致或矛盾。'
        elif len(st)==1 and st[0]['Statement ID'] in badstatements:status='EXTRACTION_REQUIRES_CORRECTION';why='The only selected sentence has an extraction problem. No admissible cross-source verification is established.'
        elif len(st)==1:status='SINGLE_USABLE_SOURCE';why='只有一份可用来源，不能做跨来源核验。'
        elif pending:status='SEMANTIC_CHECK_IN_PROGRESS';why='仍有来源文本对未完成语义比较。'
        elif confirmed:status='REVIEWED_STATEMENT_CONFLICT';why='已回看原文确认表述冲突；真值和采用值仍依核验说明，不自动覆盖。'
        elif any(x['Statement ID'] in badstatements for x in st):status='EXTRACTION_REQUIRES_CORRECTION';why='At least one selected sentence has the wrong subject or is markup rather than prose. Exclude it from this facet; other relations may remain unresolved.'
        elif probable:status='POSSIBLE_CONFLICT_NEEDS_SOURCE_REVIEW';why='存在疑似冲突或年份差别，须查看双方原文及实体/日期/范围。'
        elif lost or counts['CONTEXT_TOO_LONG_REVIEW'] or counts['NON_ENGLISH_NEEDS_TRANSLATION']:status='PARTIAL_CONTEXT_OR_SOURCE_COVERAGE';why='部分原文不可用、非英文或超出上下文，不能宣称所有来源已一致。'
        elif counts['COMPLEMENTARY_OR_DIFFERENT_CLAIMS_UNRESOLVED'] or counts['SEMANTIC_RELATION_UNCERTAIN']:status='DETAIL_SCOPE_OR_COMPLEMENTARITY_UNRESOLVED';why='未证实矛盾，但不等于表述相同；部分来源可能讲不同细节或业务范围。'
        elif counts['DIFFERENT_EVENT_DEFINITIONS']:status='EVENT_DEFINITIONS_DIFFER; NOT_DIRECT_DATE_CONFLICT';why='日期描述涉及不同事件，例如创办与法律注册，保留各自口径。'
        elif counts['ONE_WAY_SUPPORT_DETAIL_OR_SCOPE']:status='COMPATIBLE_WITH_DETAIL_OR_SCOPE_DIFFERENCES';why='模型支持兼容或包含关系，不能把更具体的说法强行改成相同文本。'
        elif counts['SEMANTICALLY_ALIGNED_MODEL']:status='MODEL_SUPPORTED_SEMANTIC_ALIGNMENT';why='已比较的来源文本语义一致；尚未独立证实每项现实事实。'
        else:status='SAME_TEXT; CHECK_SOURCE_LINEAGE';why='可比较文本相同，但可能同源转载，不视为独立验证。'
        sr={'Entity Role':r['Entity Role'],'Entity ID':r['Entity ID'],'Company Name':r['Company Name'],'Facet':r['Facet'],'Validation Status':status,'Interpretation':why,'Usable Source Documents':len(st),'Excluded Or Adjudicated Statements':sum(x['Statement ID'] in badstatements for x in st),'Admissible Source Statements After Review':sum(x['Statement ID'] not in badstatements for x in st),'Source Pairs':len(pr),'Completed Pair Comparisons':len(pr)-pending,'Unresolved Pair Comparisons':unresolved,'Possible Conflict Pairs':len(probable),'Unavailable Original Evidence Documents':lost,'Relevant Pair IDs':'; '.join(x['Pair ID'] for x in (confirmed or probable or pr)[:6]),'Verified Truth Claim':False,'Target Boundary':'External sources are diagnostic only; original target selector inputs unchanged' if r['Entity Role']=='TARGET' else 'Public candidate source-to-source check; not target-to-comp similarity'}
        statusrows.append(sr);companies[r['Entity Role'],r['Entity ID'],r['Company Name']].append(sr)
    companyrows=[]
    for (role,ident,name),rs in companies.items():companyrows.append({'Entity Role':role,'Entity ID':ident,'Company Name':name,'Total Facets':len(rs),'Facets With Cross Source Pairs':sum(x['Source Pairs']>0 for x in rs),'Facets With No Or Single Usable Source':sum(x['Usable Source Documents']<2 for x in rs),'Facets With Possible Conflict':sum(x['Possible Conflict Pairs']>0 for x in rs),'Facets With Unresolved Scope Or Context':sum('UNRESOLVED' in x['Validation Status'] or 'PARTIAL' in x['Validation Status'] for x in rs),'All Facets Independently Fact Verified':False})
    review.sort(key=lambda r:(r['Manual Adjudication'],bool(r['Event Year Difference']),min(r['A to B Contradiction Score'] or 0,r['B to A Contradiction Score'] or 0)),reverse=True)
    dump('Pair_Semantic_Results',results);dump('Conflict_Review_Queue',review);dump('Company_Facet_Validation',statusrows);dump('Company_Validation_Coverage',companyrows)
    summary={'entity_roles':len(companyrows),'company_facet_rows':len(statusrows),'source_statement_rows':len(ss),'source_pairs':len(pairs),'different_source_family_pairs':sum(not x['Same Source Family'] for x in pairs),'same_source_family_pairs':sum(x['Same Source Family'] for x in pairs),'shared_upstream_vendor_pairs':sum(x['Same Upstream Vendor'] for x in pairs),'unique_nli_jobs':len(load(O/'NLI_Jobs.json')),'completed_unique_nli_jobs':len(pred),'pending_source_pairs':sum(x['Verdict']=='PENDING_NLI' for x in results),'pair_verdict_counts':dict(collections.Counter(x['Verdict'] for x in results)),'facet_status_counts':dict(collections.Counter(x['Validation Status'] for x in statusrows)),'manual_adjudications':len(manual),'reviewed_wrong_subject_statements':sum(x['Verdict']=='REVIEWED_EXTRACTION_SUBJECT_ERROR' for x in badstatements.values()),'reviewed_facet_relevance_errors':sum(x['Verdict']=='REVIEWED_FACET_RELEVANCE_ERROR' for x in badstatements.values()),'excluded_markup_statements':sum(x['Verdict']=='EXCLUDED_MARKUP_NOT_BUSINESS_PROSE' for x in badstatements.values()),'reviewed_statement_conflicts':sum(x['Verdict']=='REVIEWED_STATEMENT_CONFLICT' for x in results),'prior_scores_modified':False,'forecasting_started':False,'model':'cross-encoder/nli-MiniLM2-L6-H768; bidirectional natural language inference; original FP32 checkpoint','not_claimed':'No claim that NLI verifies reality, that all sources are independent, or that neutral means factual agreement.'}
    dump('summary',summary);print(json.dumps(summary),flush=True)
    if not partial:assert not summary['pending_source_pairs'],'Inference still pending; do not present as a completed semantic pass.'
if __name__=='__main__':main('--partial' in sys.argv)
