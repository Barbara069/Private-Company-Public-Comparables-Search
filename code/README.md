# Research code

Python 3 and Node.js are required for source filtering and viewer validation. The notebook additionally uses pandas, requests and openpyxl; direct LSEG retrieval needs its authorized SDK/session. No academic-database adapter is included.

Run `python code/exclude_restricted_sources.py --validate` and `python code/build_unified_research_site.py` before publishing. These validate the decompressed website payloads and check JavaScript. `source_policy.py` is the shared exclusion gate. Original target website plus instructor revenue, EBITDA and debt are the only simulated-private model inputs.

Source-extraction utilities describe research work; presence of code does not prove all fields were downloaded or verified. Current candidate ranking must be rebuilt from the source-filtered corpus.
