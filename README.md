# Private Company / Public Comparables Research

Private research workspace for Barbara069. This repository contains research snapshots, acquisition scripts, a reading/validation notebook, source spreadsheets and an online-viewer source tree.

## Start here

1. Open `Research_Workflow.ipynb`: source inventory, data reconstruction/loading, current results and validation checks.
2. Open `outputs/company_research_master/Company_Research.ipynb` from its own directory for the existing full master reader.
3. Review `DATA_SOURCES.md` and `file_manifest.csv` for provider scope and file checksums.
4. Online website: https://barbara-company-comparables.awaremars21.chatgpt.site — deployed owner-private. No data API keys are required to view snapshots.

## Data structure

- `data/master/`: byte parts of the full compressed master CSV; restore with `python tools/restore_master.py`. Splitting preserves the exact master bytes while keeping individual Git files below 50 MiB.
- `outputs/global_comps_560/sources/`: original provided Capital IQ, WRDS and FF49 workbooks; the historical original instructor workbook is unavailable.
- `outputs/global_comps_560/prepared/`: cleaned input tables and provenance.
- `outputs/lseg_downloads/delivery/`: downloaded LSEG financial/company/segment snapshots and coverage.
- `outputs/global_comps_560/repaired_facets_20261028/`: current facet values, scores, exclusions and conflict dispositions. Large CSVs are gzip-compressed.
- `outputs/global_comps_560/semantic_validation_20261028/`: cross-source comparison and validation records, including unresolved findings.
- `outputs/wendys_segment_facets/`: pilot, including English/Chinese long descriptions and source dates.
- `outputs/company_research_viewer/`: local read-only web viewer source.

## Interpretation limits

The global results rerank an existing ten-candidate pool; they are not a completed exhaustive global search. Wendy is the enriched pilot; the other companies have not received equivalent segment research. Some source conflicts remain unresolved. Existing target selection uses website-only evidence; expanded database/SEC target facts are research/diagnostic data and have not been silently added to those scores. No new forecast is represented as complete.

## Credentials

Viewing cached data needs no keys. Refreshing WRDS/LSEG requires the user's authorized credentials and entitlements, configured locally, never committed. See `.env.example`. SEC uses a descriptive User-Agent. Scripts are historical acquisition code: examine input paths and dependencies before running; do not assume a notebook review refreshes vendor data.

## Git transport

Files above 8 MiB are stored as lossless byte chunks under `transport/`. The notebook restores and SHA-256 checks them automatically. Or run `python tools/restore_transport.py` before `python tools/restore_master.py`. Original spreadsheet/CSV file contents are