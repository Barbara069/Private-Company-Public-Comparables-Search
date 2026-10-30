"""Build allowlisted target inputs and a deterministic, pre-model holdout."""
import csv,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'blinded';OUT.mkdir(exist_ok=True)
original=ROOT.parent/'wrds_ratios_20261020/input_companies.json'
rows=json.loads(original.read_text())
assert len(rows)==560 and len({r['IQ_COMPANY_ID'] for r in rows})==560
seed='20261027-pseudo-private-v1'
ordered=sorted(rows,key=lambda r:(0 if r['target_ciq_ticker'] in ('WEN','PCTY') else 1,hashlib.sha256((seed+'|'+r['IQ_COMPANY_ID']).encode()).hexdigest()))
split={r['IQ_COMPANY_ID']:('DEVELOPMENT_VALIDATION' if i<420 else 'FINAL_HOLDOUT') for i,r in enumerate(ordered)}
inputs=[];labels=[];manifest=[]
for r in rows:
    cid=r['IQ_COMPANY_ID'];rev=r.get('target_revenue');debt_ratio=r.get('target_debt_to_revenue')
    # Original file supplies a debt/revenue ratio, not an explicit debt amount.
    debt=rev*debt_ratio if isinstance(rev,(float,int)) and isinstance(debt_ratio,(float,int)) else None
    inputs.append(dict(target_id=cid,company_name=r['target_company_name'],website=r['target_ciq_website'],
                       revenue=rev,ebitda=r.get('target_ebitda'),debt=debt,
                       debt_basis='DERIVED: original target_revenue * target_debt_to_revenue',
                       amount_unit='NOT_DOCUMENTED_IN_ORIGINAL_HEADERS',period='NOT_DOCUMENTED_IN_ORIGINAL_HEADERS',
                       financial_source='Original interns company list, cached exact records',
                       website_text_status='Use fetched company website only. Exclude IR/SEC financial disclosures beyond the three permitted figures.'))
    labels.append(dict(target_id=cid,actual_ev_ebitda=r.get('target_ev_to_ebitda'),source='Original interns company list',split=split[cid]))
    manifest.append(dict(target_id=cid,company_name=r['target_company_name'],split=split[cid],seed=seed,
                         permitted_candidate_reference=split[cid]!='FINAL_HOLDOUT'))
for name,data in [('target_inputs',inputs),('evaluation_labels_DO_NOT_LOAD_FOR_SELECTION',labels),('split_manifest',manifest)]:
    (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2))
    with (OUT/(name+'.csv')).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
policy='''# Pseudo-private evaluation protocol

## Target allowlist
Company name and website; company-owned business-description pages; original interns-list revenue, EBITDA and debt only. The cached original records have revenue, EBITDA and debt/revenue: debt is explicitly derived as revenue times debt/revenue, never replaced by CapIQ net debt. Original amount units and period labels remain undocumented.

Target ticker, exchange, SIC/FF49, CapIQ description, SEC business description, WRDS facts, analyst estimates, public multiple and news are NOT selection inputs. Ticker/CIK may be used internally for exclusion and entity matching only, never passed to the target profiler. Public-only disclosures on the target IR site are outside the intended limited-information profile.

## Split before model work
Seed 20261027-pseudo-private-v1. Previously explored WEN and PCTY are assigned to development first. Remaining targets sort by SHA256(seed + target ID). First 420 are development/validation; last 140 are sealed final holdout. The split is fixed before any new scores. This is not a 420-observation training plus separate validation experiment: tune inside the 420 using inner folds or a predefined internal split. Do not tune on the final 140. Existing exploratory access means this cannot be described as perfect historical analyst blinding.

Holdout targets are excluded from the public candidate reference pool during development and final benchmarking, to avoid feeding their evaluation labels back as other firms' public comp multiples. Candidate pool remains global, with 420 development firms and independently sourced external firms eligible. Exclude each target and its aliases/subsidiaries from its own candidate list. Record the entity exclusion map.

## Freeze then test
Freeze prompt, facets, weights, candidate retrieval rules, abstention rules, source cutoff and aggregation method before opening final labels. Run the frozen procedure on all 140 once. Report coverage and errors including abstentions; do not discard difficult targets. A repeated revised run is exploratory, not a fresh unseen test.

## Evidence access roles
Website rows can support the target only when they describe business without public-only information. Any target's SEC, WRDS or CapIQ supplemental data is CANDIDATE_ONLY_OR_EVALUATION, never target input. The evidence warehouse may store both roles, but the profiler reads an explicit allowlist, not the warehouse. FF49 for a target must be inferred from allowed business text, not copied from its hidden SIC. Inference and verified public candidate classification are separate fields.

## Status
Inputs and split prepared. No global candidate rankings or calibrated scores completed by this script. Existing full-information exploratory work must not be reported as blinded out-of-sample performance.
'''
(OUT/'PROTOCOL.md').write_text(policy)
print('Prepared 560 allowlisted input records, 420 development and 140 final holdout. Labels separate.')
