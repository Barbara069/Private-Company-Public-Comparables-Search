"""Source-to-source semantic comparison, never target-to-comp similarity.
NLI predictions are review evidence, not verified facts or calibrated probabilities.
"""
import collections,csv,hashlib,itertools,json,pathlib,re,sys,time,unicodedata
P=pathlib.Path(__file__).resolve().parent;I=P/'multisource_audit_20261028';O=P/'semantic_validation_20261028';O.mkdir(exist_ok=True)
def load(p):return json.loads(pathlib.Path(p).read_text())
def dump(name,rows):
    (O/(name+'.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2,default=str))
    if isinstance(rows,list) and rows and isinstance(rows[0],dict):
        cols=list(dict.fromkeys(k for r in rows for k in r))
        with (O/(name+'.csv')).open('w') as f:
            w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
def canonical(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s).replace('’',"'")).strip().lower()
def english(s):
    letters=[c for c in s if c.isalpha()]
    return len(letters)>=20 and sum('a'<=c.lower()<='z' for c in letters)/len(letters)>.8
def businesssection(s):
    options=[]
    for m in re.finditer(r'\bITEM\s*1\s*[.\-:]?\s*BUSINESS\b',s,re.I):
        rest=s[m.end():];end=re.search(r'\bITEM\s*1A\b',rest,re.I);part=rest[:end.start()] if end else rest[:50000]
        if len(part)>2000:options.append(part)
    return (max(options,key=len) if options else s)[:50000]
def prepare():
    # Read static facet definitions without importing the ranking/model pipeline.
    import ast
    tree=ast.parse((P/'score_comp_draft.py').read_text());defs={}
    for n in tree.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('PATTERNS','CATS') for t in n.targets):
            defs[n.targets[0].id]=ast.literal_eval(n.value)
    patterns=defs['PATTERNS'];cats=defs['CATS'];docs=load(I/'Target_Sources.json')+load(I/'Public_Sources.json');byid={r['Evidence ID']:r for r in docs}
    textcache={};chunks={};sourcequality={}
    for d in docs:
        key=d['Evidence ID'];text=d.get('Source Text') or '';fp=d.get('Full Text or Snapshot Path') or ''
        if fp.endswith('.txt') and pathlib.Path(fp).is_file():
            if fp not in textcache:
                raw=pathlib.Path(fp).read_text(errors='replace');textcache[fp]=businesssection(raw) if d['Source Type']=='SEC_ANNUAL_FILING' else raw[:50000]
            text=textcache[fp]
        elif d['Source Type']=='LSEG' and fp.endswith('.json') and pathlib.Path(fp).is_file():
            if fp not in textcache:textcache[fp]=load(fp)
            rows=textcache[fp];ric=(d.get('Source Field or Location') or '').split('Instrument=')[-1].split(';')[0]
            matches=[r for r in rows if r.get('Instrument')==d['Entity ID'] or (d['Entity Role']=='TARGET' and r.get('Company ID')==d['Entity ID']) or r.get('Instrument')==ric]
            if matches:text=next((r.get('TR.BUSINESSSUMMARY') for r in matches if r.get('TR.BUSINESSSUMMARY')),text)
        text=re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','',text)
        bad=bool(re.search(r'domain (?:is )?for sale|buy this domain|parked domain|access denied|verify you are human|enable javascript and cookies',text[:1500],re.I))
        sourcequality[key]='UNUSABLE_OR_BLOCK_PAGE' if bad else 'NON_ENGLISH_OR_TOO_SHORT' if text and not english(text[:1500]) else 'AVAILABLE_NOT_FACT_VERIFIED' if text else 'NO_TEXT'
        if 'SEARCH_RESULT_ONLY' in d['Status']:sourcequality[key]='SEARCH_SNIPPET_NOT_ADMITTED_AS_FACT'
        chunks[key]=[s.strip() for s in re.split(r'\n+|(?<=[.!?;])\s+',text) if 45<len(s.strip())<1600] if not bad else []
    print('Source sentences prepared',len(docs),flush=True)
    rows=load(I/'Facet_Cross_Check.json');statements=[];pairs=[];jobs={};seenstatements={}
    # Preserve all source documents, including multiple pages within a source family.
    for ri,r in enumerate(rows):
        facet=r['Facet'];ss=[]
        for provider in ['OFFICIAL_WEBSITE','LSEG','WRDS_COMPUSTAT','CAPITAL_IQ','SEC_ANNUAL_FILING','OTHER_WEB']:
            ids=(r.get(provider+' Evidence IDs') or '').split('; ')
            for key in ids:
                if key not in byid or sourcequality[key]!='AVAILABLE_NOT_FACT_VERIFIED':continue
                hits=[s for s in chunks[key] if re.search(patterns[facet],s,re.I)]
                if facet=='Geography Served':hits=[s for s in hits if re.search(r'operat|serves?|customers?|across|markets?|worldwide|global|international|sales',s,re.I) and not re.search(r'headquarter|based in|based company',s,re.I)]
                if not hits:continue
                old=r.get(provider+' Value') or ''
                def order(s):
                    anchor=canonical(s).startswith(canonical(old.split(' | ')[0])[:65]) if facet not in cats and len(old)>50 else False
                    return (-int(anchor),-min(len(re.findall(patterns[facet],s,re.I)),4),len(s)>650,-min(len(s),400))
                hits.sort(key=order)
                # Whole-source sentence, not keyword tags. Limit to two complete sentences.
                chosen=[];seen=set()
                for s in hits:
                    if canonical(s) in seen:continue
                    seen.add(canonical(s));chosen.append(s)
                    if len(chosen)==2:break
                text=' '.join(chosen)
                # Keep the complete original selected statement in the evidence file.
                d=byid[key];sid=f'S{len(statements)+1:07d}'
                item={'Statement ID':sid,'Entity Role':r['Entity Role'],'Entity ID':r['Entity ID'],'Company Name':r['Company Name'],'Facet':facet,'Source Type':provider,'Evidence ID':key,'Statement Text':text,'Source Link':d['Source Link'],'Source Date':d['Source Date'],'Source Location':d['Source Field or Location'],'Selection Note':'Complete keyword-retrieved source sentences; facet assignment itself may need review. No original text is overwritten.','Source Identity Status':d['Status']}
                statements.append(item);ss.append(item)
        # Exact duplicates are still counted as separate document comparisons, but require no inference.
        for a,b in itertools.combinations(ss,2):
            ca,cb=canonical(a['Statement Text']),canonical(b['Statement Text'])
            if ca==cb:status='EXACT_SAME_TEXT';job=None
            elif not english(a['Statement Text']) or not english(b['Statement Text']):status='NON_ENGLISH_NEEDS_TRANSLATION';job=None
            else:
                status='AWAITING_NLI';ta=a['Statement Text'];tb=b['Statement Text'];ka,kb=sorted((ta,tb));job=hashlib.sha256((ka+'\nPAIR\n'+kb).encode()).hexdigest();jobs[job]={'key':job,'a':ka,'b':kb}
            pairs.append({'Pair ID':f'P{len(pairs)+1:07d}','Entity Role':r['Entity Role'],'Entity ID':r['Entity ID'],'Company Name':r['Company Name'],'Facet':facet,'Source A':a['Source Type'],'Source B':b['Source Type'],'Statement A ID':a['Statement ID'],'Statement B ID':b['Statement ID'],'Evidence A ID':a['Evidence ID'],'Evidence B ID':b['Evidence ID'],'Source A Date':a['Source Date'],'Source B Date':b['Source Date'],'Source A Link':a['Source Link'],'Source B Link':b['Source Link'],'Initial Status':status,'NLI Job Key':job,'Reversed Versus Job':bool(job and a['Statement Text']!=jobs[job]['a']),'Same Source Family':a['Source Type']==b['Source Type'],'Same Upstream Vendor':a['Source Type'] in ('WRDS_COMPUSTAT','CAPITAL_IQ') and b['Source Type'] in ('WRDS_COMPUSTAT','CAPITAL_IQ')})
        if ri%20000==0:print('Prepared groups',ri,'/',len(rows),'pairs',len(pairs),'unique NLI jobs',len(jobs),flush=True)
    dump('Source_Statements',statements);dump('Source_Pairs',pairs);dump('NLI_Jobs',list(jobs.values()));dump('Source_Quality',[{'Evidence ID':k,'Status':v} for k,v in sourcequality.items()]);print('PREPARED',len(statements),len(pairs),len(jobs),flush=True)
def infer():
    import torch
    from transformers import AutoTokenizer,AutoModelForSequenceClassification
    torch.set_num_threads(6);name='cross-encoder/nli-MiniLM2-L6-H768';tokenizer=AutoTokenizer.from_pretrained(name,local_files_only=True);model=AutoModelForSequenceClassification.from_pretrained(name,local_files_only=True).eval()
    jobs=load(O/'NLI_Jobs.json');out=O/'nli_predictions.jsonl';done=set()
    if out.exists():
        for line in out.read_text().splitlines():
            try:done.add(json.loads(line)['key'])
            except json.JSONDecodeError:pass
    todo=[r for r in jobs if r['key'] not in done]
    # Bucket similarly sized pairs to reduce padding. Full statements remain in Source_Statements.
    todo.sort(key=lambda r:len(r['a'])+len(r['b']));start=time.time();processed=0
    with out.open('a') as f,torch.inference_mode():
        for i in range(0,len(todo),48):
            if (O/'STOP_INFERENCE').exists():print('Checkpoint stop requested',flush=True);break
            batch=todo[i:i+48];aa=[];bb=[]
            for r in batch:aa.extend([r['a'],r['b']]);bb.extend([r['b'],r['a']])
            features=tokenizer(aa,bb,padding=True,truncation=True,max_length=384,return_tensors='pt');probs=model(**features).logits.softmax(-1).cpu().tolist()
            for j,r in enumerate(batch):
                # The checkpoint's documented order is contradiction, entailment, neutral.
                f.write(json.dumps({'key':r['key'],'forward':probs[2*j],'reverse':probs[2*j+1],'max_length':384,'possibly_truncated':len(tokenizer.encode(r['a'],r['b'],truncation=False))>384})+'\n')
            processed+=len(batch)
            if i%960==0:f.flush();print('NLI unique pairs',processed,'/',len(todo),'elapsed_s',round(time.time()-start),'pairs_per_s',round(processed/max(1,time.time()-start),2),flush=True)
    print('NLI COMPLETE',processed,'new jobs',len(done),'cached',flush=True)
if __name__=='__main__':{'prepare':prepare,'infer':infer}[sys.argv[1]]()
