"""Package complete source comparisons and verify saved workbook values."""
import collections,csv,hashlib,json,pathlib,zipfile
P=pathlib.Path(__file__).resolve().parent
O=P/'semantic_validation_20261028'
def load(n):return json.loads((O/(n+'.json')).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    summary=load('summary');assert summary['pending_source_pairs']==0
    assert summary['completed_unique_nli_jobs']==summary['unique_nli_jobs']==115238
    for name in ['Manual_Adjudications','Statement_Adjudications','Proposed_Corrections']:
        rs=load(name);cols=list(dict.fromkeys(k for r in rs for k in r))
        with (O/(name+'.csv')).open('w') as f:
            w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rs)
    facets=load('Company_Facet_Validation');pairs=load('Pair_Semantic_Results');companies=load('Company_Validation_Coverage')
    assert len(facets)==113310 and len(pairs)==138266 and len(companies)==3777
    assert len({r['Pair ID'] for r in pairs})==len(pairs)
    assert len({(r['Entity Role'],r['Entity ID'],r['Facet']) for r in facets})==len(facets)
    assert collections.Counter(r['Entity Role'] for r in facets)=={'TARGET':16800,'PUBLIC':96510}
    assert all(r['Completed Pair Comparisons']==r['Source Pairs'] for r in facets)
    assert sum(r['Source Pairs'] for r in facets)==len(pairs)
    ss={r['Statement ID']:r for r in load('Source_Statements')}
    assert all(r['Statement ID'] in ss for r in load('Statement_Adjudications'))
    manifest=load('workbook_manifest')
    import openpyxl
    wb=openpyxl.load_workbook(O/'Company_Facet_Source_Validation.xlsx',read_only=True,data_only=True)
    checks=[]
    for m in manifest:
        s=wb[m['name']]
        if s.max_row is None or s.max_column is None:s.calculate_dimension(force=True)
        assert s.max_row==m['rows']+1 and s.max_column==m['columns'],(m,s.max_row,s.max_column)
        checks.append({'sheet':m['name'],'data_rows':s.max_row-1,'columns':s.max_column})
    wb.close()
    old=P/'global_run_20261028';ranks=old/'Comp_Results.csv'
    baseline=old/'Global_Comps_560_Dataframes.zip'
    with zipfile.ZipFile(baseline) as z:
        member=next(n for n in z.namelist() if n.endswith('Comp_Results.csv'))
        priorhash=hashlib.sha256(z.read(member)).hexdigest()
    assert sha(ranks)==priorhash,'Original rankings unexpectedly changed'
    validation={'pending_pairs':0,'all_facet_keys_unique':True,'pair_counts_reconcile':True,'original_ranking_unchanged':True,'original_ranking_sha256':priorhash,'workbook_sheets':checks}
    (O/'validation.json').write_text(json.dumps(validation,indent=2))
    (O/'README.md').write_text('''# Company facet source validation

This delivery compares selected factual text among sources for the same company and facet. It does not rescore comparable companies.

The Excel provides all company-facet statuses, reviewed cases, proposed corrections, company coverage and the possible-conflict queue. The CSV package contains every source statement and all source pairs, including texts, links, dates, evidence identifiers, semantic results and explicit unresolved cases.

The automated pass is complete for the prepared English statement pairs. It is not a manual fact check of every company, every original document line, or every financial number. The source retriever selects up to two matching sentences per document and facet, with a 50,000-character source limit or extracted annual-report business section. The selected sentences can have an incorrect subject or facet assignment. Human-reviewed examples demonstrate these errors.

NLI model: cross-encoder/nli-MiniLM2-L6-H768, original FP32 checkpoint, bidirectional comparison, maximum 384 model tokens. Longer pairs are marked for context review. Contradiction scores are uncalibrated model class scores, not probabilities that a statement is false. Neutral relations do not establish agreement. A high contradiction flag can be a model false positive, different segments, different dates or an extraction error.

Wrong-subject and markup exclusions preserve the original text and apply only to the affected facet. Proposed corrections are separate from original values. Source dates can be unknown, and matching language from shared vendors is not independent corroboration.

Pseudo-private target selection inputs remain unchanged. External target data is diagnostic only. Original rankings and forecasts are unchanged; no forecasting is performed here.
''')
    names=['Pair_Semantic_Results','Source_Statements','Company_Facet_Validation','Company_Validation_Coverage','Conflict_Review_Queue','Source_Quality','Manual_Adjudications','Statement_Adjudications','Proposed_Corrections']
    with zipfile.ZipFile(O/'Source_Validation_All_Comparisons.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for n in names:z.write(O/(n+'.csv'),n+'.csv')
        for n in ['summary.json','validation.json','README.md']:z.write(O/n,n)
    print(json.dumps(validation))
if __name__=='__main__':main()
