# GrowthCurve diagnostic reproduction

Set `PILOT_OUTPUT` to an empty writable work directory and `COMPARABLE_CACHE` to the permitted-source inference cache (never a retired mixed-source cache). Install requests and beautifulsoup4 for collection; inference dependencies are listed in code/README.md.

1. Run `python code/private_company_pilot/collect_websites.py`, then `python code/private_company_pilot/expand_business_pages.py`. Ordinary failures are recorded; no access controls are bypassed.
2. Run `python code/rebuild_permitted_comparables.py --inputs "$PILOT_OUTPUT/private_inputs.json.gz" --output-prefix growthcurve_ --cache "$COMPARABLE_CACHE"`.
3. Repeat with `expanded_inputs.json.gz` and prefix `growthcurve_expanded_`.
4. Run `python code/private_company_pilot/build_pilot_report.py`. It preserves the frozen automatic outputs and separately applies the explicit analyst-review notes recorded for this experiment. The review annotations are not an automated semantic verifier. Future website changes require a fresh review, not blind reuse of these notes.

No numerical weights were tuned on this diagnostic. The production 560 inputs and matches are not modified. Full downloaded text and failed facet/score records are in the separate pilot CSV artifact; the public HTML/Markdown report uses paraphrased findings.
