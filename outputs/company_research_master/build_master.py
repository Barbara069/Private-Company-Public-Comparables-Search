import csv, hashlib, json, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = pathlib.Path(__file__).resolve().parent
BASE = ROOT / 'global_comps_560'
csv.field_size_limit(2**31-1)
columns = ['record_type','dataset','record_id','entity_role','entity_id','company_name','target_id','candidate_id','facet','source_type','source_url','source_text','source_date','eligible_for_scoring','record_json']
counts = collections.Counter()
paths = set()

def first(row, *keys):
    return next((row[k] for k in keys if row.get(k) is not None), '')

with (OUT/'Company_Research_Master.csv').open('w', newline='', encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f, fieldnames=columns); writer.writeheader()
    def emit(kind, dataset, row):
        counts[dataset]+=1
        payload={k:v for k,v in row.items() if k!='Source Text'} if kind=='raw_source_document' else row
        writer.writerow(dict(zip(columns,[kind,dataset,f'{dataset}:{counts[dataset]}',first(row,'Entity Role','Evidence Role'),first(row,'Entity ID','Target ID','Candidate RIC','ID','Instrument'),first(row,'Company Name','Target Name','Candidate Name','Name'),first(row,'Target ID'),first(row,'Candidate RIC','Instrument'),first(row,'Facet'),first(row,'Source Type','SourceType'),first(row,'Source Link','Source URL'),first(row,'Corrected Value','Source Text','Text'),first(row,'Source Date'),first(row,'Eligible For Scoring'),json.dumps(payload,ensure_ascii=False,default=str)])))
    groups=[
        ('repair',BASE/'repaired_facets_20261028',['Corrected_Facets','Corrected_Facet_Scores','Corrected_Comp_Results','Conflict_Dispositions','Conflict_Pair_Dispositions','Rejected_Source_Statements','Final_Quality_Exclusions','Reextracted_Source_Evidence']),
        ('source',BASE/'multisource_audit_20261028',['Target_Sources','Public_Sources']),
        ('original_context',BASE/'global_run_20261028',['Target_Status','Candidate_Data','FF49_Context','Weights','target_allowed_profiles']),
    ]
    for kind,directory,names in groups:
        for name in names:
            jp=directory/(name+'.json'); cp=directory/(name+'.csv')
            if jp.exists():
                rows=json.loads(jp.read_text())
                if not isinstance(rows,list): raise ValueError(jp)
            elif cp.exists():
                with cp.open(encoding='utf-8-sig',newline='') as h:rows=list(csv.DictReader(h))
            else:raise FileNotFoundError(name)
            for row in rows:
                emit(kind,name,row)
                if kind=='source':
                    path=row.get('Full Text or Snapshot Path')
                    if path:paths.add(path)
    for kind,directory in [('provided_database',BASE/'prepared'),('lseg_download',ROOT/'lseg_downloads/delivery')]:
        for cp in sorted(directory.glob('*.csv')):
            dataset=('Prepared_' if kind=='provided_database' else 'LSEG_')+cp.stem
            with cp.open(encoding='utf-8-sig',newline='') as h:
                for row in csv.DictReader(h):emit(kind,dataset,row)
    seen=set();missing=[]
    for path in sorted(paths):
        p=pathlib.Path(path)
        if not p.exists():missing.append(path);continue
        raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha in seen:continue
        seen.add(sha)
        # Standalone cached evidence only; credentials/config files are never read.
        emit('raw_source_document','Embedded_Source_Documents',{'Source Link':path,'Source Text':raw.decode('utf-8',errors='replace'),'SHA256':sha,'Evidence Use':'Diagnostic only for target external sources; does not authorize selector use'})
    emit('metadata','Delivery_Manifest',{'Dataset Counts':dict(counts),'Missing Cached Source Paths':missing,'Scope':'Existing downloaded data consolidated, not a new download or assertion of completeness','Target Input Policy':'Official website only; external target references and financials diagnostic/held out','Ranking Scope':'Previous ten candidates per target only','Unresolved Fields':'Remain NULL and excluded from scoring','Raw Source Text':'Unique registered cached documents embedded; not the full content of every linked website','Format':'record_json retains each original record schema; source_text is a convenient view, not a new factual assertion'})

cells=[]
def md(s):cells.append({'cell_type':'markdown','metadata':{},'source':s.splitlines(True)})
def code(s):cells.append({'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':s.splitlines(True)})
md('# Company research: one CSV, one notebook\n\nPut this notebook beside **Company_Research_Master.csv**. All views below use only that file. It bundles existing financial downloads, target/candidate context, repaired facets, scores, conflict records and cached source documents. It does not rerun downloads, global discovery, factual verification or forecasting.\n\n**Important:** 2,111 flagged fields remain unresolved and excluded from scoring. Automatic excerpts and retained baselines are not individually verified. Scores rerank the existing ten candidates only. Target selector evidence is official website only; external target records and financials are diagnostic/held out. Source dates and review dates remain separate.\n\nThe CSV is a long-format record store: `dataset` identifies the table, and `record_json` preserves its complete fields. Different record types occupy separate rows, avoiding many-to-many joins that multiply observations. Embedded source documents make the notebook independent of old local source paths. Publication links and original snapshot paths are retained for traceability. Large raw documents make chunked loading preferable.')
code("from pathlib import Path\nimport csv, json, collections\nimport pandas as pd\ncsv.field_size_limit(2**31 - 1)\nDATA = Path('Company_Research_Master.csv')\nassert DATA.exists(), 'Place the master CSV beside this notebook.'\n\ndef records(dataset):\n    with DATA.open(encoding='utf-8-sig', newline='') as f:\n        for row in csv.DictReader(f):\n            if row['dataset'] == dataset:\n                item = json.loads(row['record_json'])\n                if row['record_type'] == 'raw_source_document':\n                    item['Source Text'] = row['source_text']\n                yield item\n\ndef table(dataset):\n    return pd.DataFrame.from_records(records(dataset))\n\nmanifest = next(records('Delivery_Manifest'))\npd.Series(manifest['Dataset Counts'], name='rows').sort_index()")
md('## Updated comparables and facet contributions\nScores withheld for missing core evidence remain missing. Inspect coverage alongside similarity; missing evidence is not a zero similarity.')
code("comps = table('Corrected_Comp_Results')\nfacets = table('Corrected_Facets')\ncontributions = table('Corrected_Facet_Scores')\ndispositions = table('Conflict_Dispositions')\nassert len(comps) == 5490\nassert len(facets) == 113310\nassert len(contributions) == 87840\nassert len(dispositions) == 3016\nassert not facets.duplicated(['Entity Role','Entity ID','Facet']).any()\nquarantined = facets['Repair Action'].eq('UNRESOLVED_VALUE_QUARANTINED')\nassert facets.loc[quarantined, 'Corrected Value'].isna().all()\nassert not facets.loc[quarantined, 'Eligible For Scoring'].any()\nassert facets.loc[facets['Entity Role'].eq('TARGET') & facets['Eligible For Scoring'], 'Source Type'].eq('OFFICIAL_WEBSITE').all()\nassert dispositions['Repair Action'].eq('UNRESOLVED_VALUE_QUARANTINED').sum() == 2111\ncomps.head(10)")
code("# Change the search text for any target.\nquery = 'Paylocity'\ncomps[comps['Target Name'].str.contains(query, case=False, na=False)]")
md('## Before/after, sources and unresolved evidence')
code("facets[facets['Company Name'].str.contains(query, case=False, na=False)][['Entity Role','Company Name','Facet','Before Value','Corrected Value','Eligible For Scoring','Source Link','Before Source Link','Repair Action','Human Reviewed Fact']]")
code("target_sources = table('Target_Sources')\npublic_sources = table('Public_Sources')\n# External target references are diagnostic; do not merge them into selector inputs.\npublic_sources.head(3)")
md('## Financial data and FF49 context\nThese are the existing snapshots, with their original identifiers, units, dates and coverage limitations. Presence of a dataset does not establish complete coverage or point-in-time validity. Target financials are not permitted selector inputs under the current pseudo-private policy.')
code("available = manifest['Dataset Counts']\npd.Series({k:v for k,v in available.items() if k.startswith(('Prepared_', 'LSEG_'))}, name='rows')")
code("# Load only the financial table you need; all original columns are retained.\nannual_financials = table('LSEG_annual_five_years')\nff49_benchmarks = table('Prepared_FF49_Benchmarks_560')\nannual_financials.head()")
md('## Read an embedded raw source document\nOriginal local snapshot paths are provenance references. The text itself is embedded in the master CSV, so those paths need not exist on another computer. To save memory this example reads one document rather than loading every full text.')
code("doc = next(records('Embedded_Source_Documents'), None)\nif doc:\n    print(doc['Source Link'])\n    print(doc['Source Text'][:6000])\nprint('Missing cached source paths:', len(manifest['Missing Cached Source Paths']))")
md('## Scoring reconciliation\nRetains original proposed weights and checks observed-facet weighted averages. This verifies arithmetic, not the factual accuracy of automatically extracted claims or the quality of the candidate pool.')
code("keys = ['Target ID','Candidate RIC']\ns = contributions.copy()\ns['observed_weight'] = s['Proposed Weight'].where(s['Facet Similarity Percent'].notna(), 0)\ns['numerator'] = s['observed_weight'] * s['Facet Similarity Percent'].fillna(0)\ncheck = s.groupby(keys)[['observed_weight','numerator']].sum()\ncheck['recomputed'] = check['numerator'].div(check['observed_weight'].replace(0, float('nan')))\ncheck = check.join(comps.set_index(keys)[['Partial Observed-Facet Similarity','Weighted Evidence Coverage']])\nassert (check['observed_weight'] - check['Weighted Evidence Coverage']).abs().max() < 1e-4\nassert (check['recomputed'] - check['Partial Observed-Facet Similarity']).abs().max() < .011\nprint('Structural, policy and score arithmetic checks passed. Factual conflicts remain explicitly unresolved.')")
nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'nbformat':4,'nbformat_minor':5}
for i,c in enumerate(cells):c['id']=f'cell-{i:03}'
(OUT/'Company_Research.ipynb').write_text(json.dumps(nb,ensure_ascii=False,indent=2))
print(json.dumps({'rows':sum(counts.values()),'datasets':len(counts),'csv_bytes':(OUT/'Company_Research_Master.csv').stat().st_size,'missing_cached_paths':len(missing)},indent=2))
