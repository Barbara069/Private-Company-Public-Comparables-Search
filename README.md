# Barbara069 / Private Company Comparables Research

**[Open the research website](https://barbara069.github.io/Private-Company-Public-Comparables-Search/)**

This is the single canonical repository for the research code, Notebook, methodology, and website. The separate website repository has been consolidated here. The website is public and requires no login.

## Download the existing delivery files

| File | Purpose |
|---|---|
| [Company_List_for_Interns.xlsx](https://github.com/Barbara069/Private-Company-Public-Comparables-Search/releases/latest/download/Company_List_for_Interns.xlsx) | Original instructor input |
| [CapitalIQ_560.xlsx](https://github.com/Barbara069/Private-Company-Public-Comparables-Search/releases/latest/download/CapitalIQ_560.xlsx) | Original Capital IQ input |
| [WRDS_560.xlsx](https://github.com/Barbara069/Private-Company-Public-Comparables-Search/releases/latest/download/WRDS_560.xlsx) | Original WRDS input |
| [Research_Data.csv.gz](https://github.com/Barbara069/Private-Company-Public-Comparables-Search/releases/latest/download/Research_Data.csv.gz) | One consolidated downloaded-data CSV |
| [Research_Workflow.ipynb](Research_Workflow.ipynb) | Load the data and see the download code |

Put the four downloads beside the notebook. The CSV is compressed as one file; pandas reads it directly without extracting it. Large downloads are stored in Releases, not split into repository folders.

Install pandas, requests, openpyxl and Jupyter. Refreshing WRDS/LSEG needs authorized credentials configured locally; none are uploaded. Source dates, links and original text are retained in the CSV. Existing comparable scores remain provisional.

The repository is public. Website data is stored under `website/data/`; source code and methodology have one canonical location under `code/`. Large downloadable snapshots remain in Releases; consolidating repositories does not refresh those release assets.


## Current research and website source

- [Code directory](code/) — SEC refresh, evidence extraction, validation, CSV packaging/readback, dictionaries and scoring protocols.
- [Website entry point](website/index.html) and [website JavaScript](code/website_app.js).
- [01. General facets](code/01_General_Facets.md).
- [02. Industry facets](code/02_Industry_Facets.md).
- [03. Similarity scoring](code/03_Similarity_Scoring.md).
- [04. Revenue growth methodology](code/04_Revenue_Growth_Methodology.md).
- [Actual completion status and remaining gaps](code/Research_Completion_Status.md).
- [Execution dependencies and version notes](code/README.md).

The root notebook remains in place. These source files were synchronized on 2026-11-12; API credentials are excluded. This code upload does not update the large data assets in Releases. New industry evidence extraction and the new-standard similarity calibration are still in progress.

## Repository consolidation

On 2026-11-13, all 361 website data files were migrated from website snapshot `d6331b95f491e9e1244173001438543b2c609d86` and verified by Git blob hashes. The Notebook, original inputs, existing Releases and research code were preserved. Website-specific source files were merged into `code/`; duplicate root methodology copies were removed.
