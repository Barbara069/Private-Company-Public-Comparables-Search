# Information-level provenance

Targets: the 560 company IDs in the supplied Capital IQ workbook. Candidate
discovery: global listed companies, excluding the target and duplicate listings
of the same issuer. Current listing eligibility requires a dated check.

The files in this folder are a data-preparation deliverable, not a completed
global comparable-company study. No final target–comp scores have been calculated.

## Required fields on every factual observation

- Company ID and issuer name; distinguish original and current names/tickers.
- Facet or metric name and value. Preserve raw and normalized values separately.
- `information_source`: `PROVIDED_CAPITAL_IQ_EXCEL`,
  `PROVIDED_WRDS_COMPANY_EXCEL`, `PROVIDED_WRDS_FF49_EXCEL`, or `WEB`.
- Workbook, worksheet and cell for supplied Excel information.
- Exact webpage URL, document title and supporting passage for web information.
- Source publication date, financial observation/period date and retrieval date.
  If not stated, use `UNKNOWN`, not the retrieval date as a substitute.
- Company versus industry scope. An industry median is not a company's metric.
- Extraction status: supported source fact, derived calculation, interpretation,
  conflicting evidence, unknown or not applicable.

The official SIC-to-FF49 definition is an additional web source. Its input SIC
comes from the supplied Capital IQ workbook. Record both when explaining the
derived industry assignment.

## Outside the supplied 560

The supplied spreadsheets do not establish the company-level facets or financials
of any external candidate. Research those observations on the web or in a newly
supplied dataset. Do not attach a provided-Excel citation merely because an
external candidate shares an industry or resembles a target.

The same company can have several source types. Preserve disagreements and dates
instead of silently overwriting one source with another. A website URL stored in
Capital IQ is an Excel-sourced URL until that website is actually read.

## Matching and scoring

- Extract source facts first; score the target–candidate pair afterwards.
- Scores and weights are model/analyst assumptions, not values reported by the
  cited sources. Show each contribution and its evidence references.
- The proposed initial weights sum to 100%. They are not calibrated or validated.
- Unknown and not-applicable fields never create a perfect similarity match.
- Retain coverage alongside the weighted score. Missing core business evidence
  prevents automatic acceptance even if the observed-facet score is high.
- FF49 is a soft comparison feature, not a hard same-industry restriction or a
  substitute for segment-level business evidence.
- Do not remove business peers based on their actual EV/EBITDA to improve apparent
  valuation fit. Any user-approved eligibility rule must be reported separately.
- Do not imply a global exhaustive search. Retain search logs and the examined pool.

## Prepared source outputs

`prepare_sources.py` reads all three downloaded originals without modifying them.
It keeps the 560 IDs, joins conservative WRDS ticker/name matches, maps SIC to
official FF49 groups, copies the supplied industry medians, and compares same-month
WRDS company ratios where possible. Duplicate metric labels are withheld from
automatic differences until their meanings are verified. Historical identities
remain review items; ticker reuse is not treated as a valid entity join.

The facet table currently contains deterministic source excerpts and UNKNOWN
fields. It is not a completed semantic extraction or independent web verification.
The accompanying CSVs preserve all prepared fields and date-aligned comparison
records. The Excel view displays selected aligned ratios for readability.
