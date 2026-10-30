# Data sources and access

Private research repository. Database exports retain their original provider restrictions; repository access is not a redistribution licence.

| Source | Included | Refresh requirements |
|---|---|---|
| Instructor intern list | Prepared Targets_560 CSV/JSON | Original Excel at the historical Desktop path is unavailable; not represented as an original workbook |
| Capital IQ | Original sources/capiq.xlsx + prepared CSVs | Licensed export / provided workbook |
| WRDS | Original sources/wrds.xlsx, prepared ratios, collection code | WRDS_API_TOKEN in local environment; account entitlements |
| LSEG | Five-year financial and company/segment CSV snapshots, acquisition code | LSEG Workspace running locally, app key and account entitlements; an app key alone is insufficient |
| SEC EDGAR | Cached documents embedded in master, acquisition code and provenance URLs | Public endpoint, descriptive User-Agent and rate limits; no API secret |
| Fama-French 49 | Original ff49.xlsx and SIC mapping, prepared benchmarks | Original snapshot and official mapping |
| Official company websites / calls | Cached evidence, links, periods; Wendy bilingual pilot | Web access; source availability and dated scope |

No API authorization token is included. Database availability, extraction and factual validation are different statuses. Unresolved evidence remains excluded, not silently filled.
