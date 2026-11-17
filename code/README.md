# Research code

The current permitted-evidence rebuild uses `rebuild_permitted_comparables.py`, `matching_rules.json`, `strict_facet_checks.py` and `public_facet_rules.py`. It reads only the source-filtered catalog, attributed public profiles, the isolated 560 target inputs and the numbered facet/weight dictionaries. It never loads retired mixed-source matches, vectors or classifications.

For inference install Python 3, numpy, torch, scikit-learn, sentence-transformers<4, transformers<5, tokenizers<0.23 and huggingface-hub<1. Cache the public `sentence-transformers/all-MiniLM-L6-v2` model before an offline run. The model is not fine-tuned on target financial outcomes. The notebook additionally uses pandas, requests and openpyxl; direct LSEG retrieval needs an authorized SDK/session. No academic-database adapter or credentials are included.

Run `python code/rebuild_permitted_comparables.py --cache /path/to/cache`, then `python code/package_rebuilt_comparables.py --cache /path/to/cache`. Cache files are resumable intermediate embeddings, not publication data. `--pilot` produces a separate two-target diagnostic and must not be published as the full result.

Before publishing run `python code/validate_rebuilt_comparables.py`, `python code/exclude_restricted_sources.py --validate`, `python code/check_publication_tree.py` and `python code/build_unified_research_site.py`. Do not rerun the destructive source-cleanup generation step on newly rebuilt matches. The shared `source_policy.py` rejects excluded observations. `publish_clean_release.py` packages the comprehensive CSV and preserves the two permitted original workbooks in Releases.

See `03_Similarity_Scoring.md` for active 60/40 general/industry indices, frozen target weights, evidence coverage, ordering and abstention rules. These are provisional automated results, not completed human validation or five-year forecasts. All source excerpts retain their provenance; unknown facts remain unknown.

The executed Netchex indexed forecast is in `forecast_private.py` and `Netchex_Revenue_Forecast_Prototype.md`. Reproduce it using the frozen `website/data/private_forecast_prototype.json.gz` bundle. This is a scenario prototype with unknown actual private financials, not a calibrated five-year forecast or valuation.

Optional source refresh: `python code/fetch_forecast_sources.py` downloads the eight explicitly named issuer/target documents used in this frozen prototype, saving payloads under `outputs/forecast_source_downloads` (override with `FORECAST_WORKDIR`). It requires requests, beautifulsoup4 and Poppler `pdftotext` for the ADP PDF. This is a source download helper, not an automatic update to assumptions or a search for new guidance; numeric fields require review before replacing the frozen input bundle.
