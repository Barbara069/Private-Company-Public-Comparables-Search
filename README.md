# Barbara069 / Private Company Comparables Research

**[Open the website](https://barbara069.github.io/Private-Company-Public-Comparables-Search/)** · [Code](code/) · [Latest downloads](https://github.com/Barbara069/Private-Company-Public-Comparables-Search/releases/latest)

This is the single repository for the website, research code, notebook and methodology.

## Sources and downloads

From the latest Release, place `Company_List_for_Interns.xlsx`, `CapitalIQ_560.xlsx` and `Research_Data.csv.gz` beside [Research_Workflow.ipynb](Research_Workflow.ipynb). Pandas reads the compressed CSV directly. The CSV includes permitted provider observations, company research, original evidence/source links, industry and growth records, and the 560 restricted target-input records.

**WRDS-delivered data is excluded everywhere in the active publication pipeline.** Its text, ratios, classifications, identifiers and dependent results must not be reused or relabeled as another source. This also applies to Capital IQ/Compustat data obtained through that service. Independently supplied Capital IQ workbook content has separate provenance. Other data providers remain subject to their own access and redistribution terms; removal of one source does not grant rights to the rest.

Sources retained where independently available include official company websites, SEC disclosures, directly obtained LSEG observations, and the supplied instructor/Capital IQ workbooks. Missing evidence is UNKNOWN. No credentials are committed.

## Methodology

1. [General facets](code/01_General_Facets.md)
2. [Industry facets](code/02_Industry_Facets.md)
3. [Similarity scoring standard](code/03_Similarity_Scoring.md)
4. [Five-year revenue, EBITDA and valuation forecast plan](code/04_Revenue_Growth_Methodology.md)

## Current status

The source policy changed on 15 November 2026. Previous candidate baskets and scores were produced from a mixed-source corpus and have been withdrawn pending allowed-source re-selection and scoring. Surviving excerpts are not automatically semantically verified. Forecast methodology is specified; company forecasts are not yet executed or validated.

The website lives in `website/`; canonical code and documentation live in `code/`. The publication guard checks decompressed payloads and evidence references. Original permitted target inputs remain isolated from unrestricted public research.
