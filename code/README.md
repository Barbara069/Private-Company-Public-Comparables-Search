# Research and website code

This directory contains the current website JavaScript, SIC/general dictionaries, SEC refresh, evidence extraction, CSV packaging/readback, and similarity protocol. `../website/index.html` is the self-contained HTML/JavaScript website entry point; it needs the existing public website `data/` bundles to show cached research. No API is needed merely to view those cached data.

These scripts preserve their original project paths under `outputs/main_facets_refresh`; the code copy here is for source review, not a claim that a clean clone contains the complete local execution environment. Some helpers reference retained `outputs/global_comps_560` scripts/data and local source caches. Do not run extraction or packaging against your only data copy without restoring those dependencies.

`refresh_latest_disclosures_20261111.py` downloads source text; `complete_evidence_pass_20261111.py` extracts evidence; `validate_evidence_pass_20261111.py` validates structure and isolation; `package_evidence_pass_20261111.py` writes the two comprehensive population CSVs; `check_delivery_csvs_20261111.py` reads them back. Filename dates identify reproducible snapshots and should not be silently rewritten as live results.

`similarity_protocol.py` is the older reviewed-evidence formula. `scoring_policy_v3.json` and `03_Similarity_Scoring.md` describe a proposal; they are not the algorithm behind historical scores. Industry evidence/semantic review and the new field-level weights/rankings remain incomplete.

No API tokens or credentials are included. This code upload does not upload or refresh the large CSVs in Releases. The root Research_Workflow.ipynb remains the main notebook.
