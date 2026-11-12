# Barbara069 / Private Company Comparables Research

## Download the five delivery files

| File | Purpose |
|---|---|
| [Company_List_for_Interns.xlsx](https://github.com/Barbara069/Private-Company-Public-Comparables-Search/releases/latest/download/Company_List_for_Interns.xlsx) | Original instructor input |
| [CapitalIQ_560.xlsx](https://github.com/Barbara069/Private-Company-Public-Comparables-Search/releases/latest/download/CapitalIQ_560.xlsx) | Original Capital IQ input |
| [WRDS_560.xlsx](https://github.com/Barbara069/Private-Company-Public-Comparables-Search/releases/latest/download/WRDS_560.xlsx) | Original WRDS input |
| [Research_Data.csv.gz](https://github.com/Barbara069/Private-Company-Public-Comparables-Search/releases/latest/download/Research_Data.csv.gz) | One consolidated downloaded-data CSV |
| [Research_Workflow.ipynb](Research_Workflow.ipynb) | Load the data and see the download code |

Put the four downloads beside the notebook. The CSV is compressed as one file; pandas reads it directly without extracting it. Large downloads are stored in Releases, not split into repository folders.

Install pandas, requests, openpyxl and Jupyter. Refreshing WRDS/LSEG needs authorized credentials configured locally; none are uploaded. Source dates, links and original text are retained in the CSV. Existing comparable scores remain provisional.

Website: https://barbara069.github.io/private-company-comparables-research/ — public viewer, no login required. Original inputs and the complete CSV remain in this private repository.


## Current research and website source

- [Code directory](code/) — SEC refresh, evidence extraction, validation, CSV packaging/readback, dictionaries and scoring protocols.
- [Website entry point](website/index.html) and [website JavaScript](code/website_app.js).
- [Proposed similarity standard and weights](code/Similarity_Scoring_Standard.md).
- [Actual completion status and remaining gaps](code/Research_Completion_Status.md).
- [Execution dependencies and version notes](code/README.md).

The root notebook remains in place. These source files were synchronized on 2026-11-12; API credentials are excluded. This code upload does not update the large data assets in Releases. New industry evidence extraction and the new-standard similarity calibration are still in progress.
