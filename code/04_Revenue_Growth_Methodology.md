# 04. Revenue Growth and EBITDA Forecasting Methodology
**Methodology and extraction specification | Updated 12 November 2026**

## Research objective
This independent research pipeline complements the team’s main project by testing whether broader public-company coverage, evidence-linked business facets, and explicit industry and segment comparisons improve comparable selection and financial forecasting. The proposed forecasting stage compares two approaches: similarity-weighted public comparables and pooled industry-informed regression. Neither approach has yet produced evaluated forecasts in this pipeline.

## Information available to the target
Each of the original 560 listed companies is simulated as a private target. Matching and prediction may use only its official website and the revenue, EBITDA, and debt values supplied in the original instructor file. Missing values remain unknown. Target SEC filings, vendor financials, stock prices, and otherwise hidden segment financials must not enter target features, peer selection, weight selection, or forecast adjustments.

A separate unrestricted research view can show those records for audit. Website visibility does not make a field eligible for the simulated-private experiment. Hidden target outcomes are reserved for evaluation; this restriction applies equally when constructing narratives and numerical forecasts.

## Extraction specification: information and sources

The table distinguishes the **current extraction** from fields **specified for the forecasting stage**. Database access or a planned field does not mean that field has already been downloaded or validated for every company.

| Source | Information to extract | Role in the method | Current status and target restriction |
|---|---|---|---|
| Instructor Excel | Supplied revenue, EBITDA and debt; original company identifier, currency, units and any stated financial period | Starting target revenue, EBITDA margin and leverage context | Use original values only; do not invent dates, units or missing amounts. These three financial measures are the permitted target financial inputs. |
| Official company website | Product/service descriptions; customers and end markets; business and revenue models; operating locations; disclosed business lines; dated announcements about launches, store openings, customers and partnerships | Target facet extraction, industry-module assignment and qualitative growth assumptions | Website passages are already used in restricted target matching. A dedicated, dated growth-signal pass over target websites is still required; current growth-tab filing excerpts do not substitute for it. |
| Capital IQ Excel | Available identity fields, business descriptions, industry/segment fields, and supplied financial observations | Public-peer identity and financial comparison; cross-check against filings | Imported workbook fields must retain workbook name, sheet, row, column, period and unit. Do not assume every desired field exists. Target vendor descriptions and financials beyond the instructor inputs remain hidden from matching and prediction. |
| LSEG | Retained business summaries, including TR.BusinessSummary; available public-peer revenue, EBITDA, debt, geographic/segment information and dated estimates if separately entitled and retrieved | Public-peer description, financial history and forward-growth inputs | Business descriptions are retained in research profiles. The current growth-signal batch is SEC-based; LSEG estimates, financial bridges and segment figures are not claimed complete. Retain actual field code, instrument, parameters, period and retrieval date for every downloaded observation. |
| WRDS / Compustat | Available company business description (e.g. company.busdesc where available); public-peer revenue, operating-performance and balance-sheet observations; identifiers and fiscal periods | Independent retrieval route for descriptions and historical financial baselines | Existing WRDS records can support peer research. Dataset/table/column coverage must be checked before extraction. Do not label an operating-income field EBITDA without a documented bridge. WRDS and Capital IQ may share an underlying vendor and are not automatically independent confirmations. |
| SEC filings and company-facts data | 10-K/20-F business discussion; 10-Q/6-K updates where applicable; MD&A revenue bridges; segment notes; debt notes; issuer-defined EBITDA reconciliations; structured reported revenue and debt facts where available | Source-backed public-peer facts, reported growth and financial reconciliation | Current growth batch extracts retained filing text, not a completed structured company-facts financial panel. Target filing text is research-only and excluded from simulated-private forecasting features. |
| Earnings releases and earnings calls | Management guidance, forecast horizon, price/mix versus volume commentary, demand, retention, backlog conversion, unit growth and margin drivers | Explain peer outlook and proposed assumptions | Use issuer IR releases and legally available transcripts with date and speaker. A transcript observation is not a reported result. Comprehensive call/release extraction remains pending; do not infer completion from SEC coverage. |
| Google Search and news | Discovery of official product pages, IR releases, filings and material dated developments; attributable third-party corroboration | Find missing evidence and investigate discrepancies | Google is a discovery route, not the underlying fact source. Download and cite the destination passage. Broad news coverage is not yet complete. Non-website target news is excluded unless the allowed-input policy is explicitly expanded. |
| Fama–French industry classification / WRDS industry ratios | Industry membership or mapping, available industry-level ratios, dates, units and population definitions | Industry controls and peer/industry reference statistics | Distinguish a published industry statistic from a median computed over our peer sample. FF49 is an industry classification here, not a Fama–French stock-return factor model. Do not import a hidden target SIC/FF49 label; infer permitted target industry from its website. |

### Growth signals extracted from retained SEC text

| Signal family | Specific content retrieved | Interpretation required before use |
|---|---|---|
| Revenue / sales | Reported increases, declines and quoted growth figures | Identify period, consolidated versus segment scope, organic versus acquired growth and currency basis. |
| Price and mix | Pricing changes, average check/selling price, customer/product mix | Separate price effects from volume; do not count the same effect twice. |
| Volume and demand | Unit volumes, transactions, traffic and demand commentary | Distinguish issuer results from general market commentary. |
| Customer recurrence | Customer acquisition, retention, subscription revenue and recurring-revenue statements | ARR and retention metrics need their issuer definitions and are not identical to recognized revenue. |
| Orders / backlog | Order intake, bookings, backlog and conversion statements | Preserve expected conversion timing; backlog is not immediate revenue. |
| New units / geography | New stores, restaurants, outlets and market entries | Separate gross openings, closures and net additions; establish revenue ramp assumptions separately. |
| Products / milestones | Launches, platforms, commercialization and regulatory milestones | A launch or approval does not establish realized sales. |
| Capacity / investment | Capacity expansion, facilities, production and capital expenditures | Investment is a possible enabling driver, not a direct revenue forecast. |
| Acquisitions / disposals | Portfolio changes and stated revenue contributions | Separate acquired growth from organic growth and reconcile continuing operations. |
| Guidance / outlook | Management expectations and forward-looking statements | Keep the forecast horizon, date, range and conditions. |
| Macro / FX / constraints | Exchange-rate effects, inflation, supply constraints and demand softness | Establish whether an effect occurred, is expected, or is merely a conditional risk. |
| EBITDA / margin | Operating-margin, gross-margin and adjusted-EBITDA drivers | Preserve accounting definition and reconciliation; operating margin is not EBITDA margin. |

The current extractor searches the entire retained text, ranks relevant passages and retains at most two passages per category per document and four per category per company. It is a bounded evidence-retrieval pass, not an exhaustive capture of every relevant sentence. Statement type is assigned by text rules and still requires semantic review.

### What is saved for each observation

Store company/issuer identifier, facet or signal category, exact downloaded passage, source family, direct document URL or workbook locator, filing form/accession where applicable, publication date, financial period, retrieval timestamp, company/segment scope, quoted figures, units/currency when stated, and discrepancy/review status. Retain full downloaded text separately where already collected and link the excerpt to its document hash. Never manufacture missing metadata.

Derived calculations must additionally identify their input observations and formula. For example, historical CAGR = (ending revenue / starting revenue)^(1 / years) − 1; forecast revenue and margins are calculated outputs, not quotations. Industry medians must disclose the included issuers, period, metric definition, currency treatment and observation count.

A field may be retrieved, source-matched, meaning-reviewed, or forecast-eligible; these are different states. Three passages are not necessarily three independent sources. Store restricted-target eligibility explicitly so the unrestricted research display cannot silently feed hidden information into the model.


## Evidence collected so far
The retained-filing extraction scanned 1,616 unique linked SEC documents, representing 527 companies, and retrieved 14,581 growth-related excerpts. These are retrieval results, not 14,581 verified independent facts or completed forecasts. Coverage is uneven and does not establish complete filing coverage for the global candidate universe.

Each excerpt retains its source URL, filing form, filing date, reporting period, and original text. Historical results, management outlook, and conditional risk disclosures are distinguished. Retrieved target SEC excerpts remain outside the simulated-private model inputs. Financial histories are intended to cover the latest five available years; longer histories are not required merely because a database offers them.

## Method 1: Similarity-weighted public comparables
Select economically comparable public companies using permitted target information. Compare general facets, applicable industry facets, and the target’s disclosed business activities. Product, customer, revenue model, operating role, geography, and relevant industry characteristics should drive selection; a shared industry code alone is insufficient.

For eligible peers j, estimate future target growth as:
```
predicted target growth = sum(peer weight_j × peer growth estimate_j)
sum(peer weights) = 1
```
Peer growth must refer to the same forecast horizon, currency treatment, and definition. Use dated analyst estimates or explicitly labeled forecasts where available. Historical realized growth is a backward-looking baseline, not a future estimate. In retrospective tests, use only peer information available on the forecast date.

Weights should reflect reviewed business similarity and evidence quality. Report similarity and evidence coverage separately; a high score from a few observed facets is not strong evidence of overall comparability. Exclude unreviewed identity and material business-model mismatches. Avoid counting multiple share classes as independent peers. Regional listed operators and global brand owners are separate comparison units, but should not crowd out the economically appropriate parent or create unreported group concentration.

Provide a weighted central estimate, an unweighted median baseline, peer dispersion, and sensitivity to removing the largest-weight peer. Freeze the weighting rule before evaluating held-out targets.

## Method 2: Pooled industry-informed regression
Estimate revenue growth across public training companies using business characteristics and financial inputs that will also be available for simulated-private targets. Industry indicators and interactions can capture economic differences without fitting 49 separate small regressions.

An illustrative specification is:
```
future revenue growth =
  intercept
  + permitted starting financial characteristics
  + encoded website-derived business facets
  + industry controls
  + selected industry × business-model interactions
  + error
```
Industry assignment must be inferred consistently from permitted target information; do not import a hidden target SIC code. Starting EBITDA margin and debt-to-revenue may be used only when the original values are available and consistently defined. Standardization, feature selection, missing-value handling, and any model tuning must be fitted within the development sample.

Compare a regularized pooled model against simple industry-median and historical-growth baselines. Report insufficient evidence rather than forcing an estimate for unsupported business types.

## Multiple business segments
Distinguish economically different business lines from geographic reporting segments. Assign industry facets separately to each supported activity and record the evidence for the assignment. Geography alone does not automatically require another industry module.

Where permitted website evidence discloses segment revenue shares, combine segment growth using those shares. Where it does not, do not borrow hidden filings or invent precise mix weights. Use a company-level forecast with disclosed uncertainty, or clearly labeled alternative segment-mix scenarios. Shared central costs and intersegment eliminations prevent mechanically summing standalone segment EBITDA without reconciliation.

## Revenue and EBITDA bridge
Convert an annual growth estimate g into revenue using Revenue(t+1) = Revenue(t) × (1 + g). For several years, compound the sequence of annual growth estimates. State whether the reported measure is cumulative growth or CAGR.

Estimate EBITDA separately:
```
EBITDA(t+h) = Revenue(t+h) × forecast EBITDA margin(t+h)
```
Use a documented peer-margin baseline and justified adjustments for franchise mix, operating leverage, maturity, and business mix only when permitted target evidence supports them. Keep reported EBITDA and adjusted EBITDA distinct. Revenue growth does not imply the same EBITDA growth.

Extracted drivers such as price/mix, volume, customer retention, bookings, new units, acquisitions, and FX help explain assumptions. Avoid double counting: total peer growth already includes many of these effects. A filing risk factor is a conditional risk, not evidence that a headwind occurred. Bookings and backlog are not automatically recognized revenue.

## Source reconciliation
For each material assumption, retain the exact relevant passage, source link, document date, reporting period, company/segment scope, and unit. Prefer the latest applicable SEC disclosure for reported public-candidate facts; preserve older or conflicting observations with a short discrepancy note. A newer document does not supersede every historical statement or every differently scoped metric.

Cross-source agreement requires compatible meaning, scope, period, and units. Repeated vendor copies of the same filing are not independent confirmations. LLM-assisted extraction may identify passages and propose interpretations, but unsupported numbers and invented quotations are prohibited.

## Evaluation plan
Before any fitted or tuned experiment, freeze an issuer-level 75% development / 25% final out-of-sample split. The split is a planned evaluation design, not a claim that it has already been executed. Keep related securities within one group and prevent held-out target outcomes from entering peer features or forecast construction.

Tune peer counts, weights, models, and abstention thresholds only within development data, using internal validation. For historical evaluation, also enforce an information cutoff and allow future outcomes to mature. Current filings cannot be used to simulate earlier knowledge.

Compare revenue-growth error and revenue/EBITDA forecast error using MAE, median absolute error, and appropriate percentage-error measures. Percentage errors become unstable near zero; EBITDA losses require separate treatment. Report evidence coverage, abstention rate, and performance by industry and segment complexity alongside aggregate error.

## Current limitations and next steps
Growth evidence has been extracted, but semantic review and numerical forecasting remain incomplete. Candidate ranking still requires extraction-quality review; the Wendy’s / McDonald’s example exposed unrelated product labels and regional-versus-global scope issues. Those errors must be repaired before relying on the affected similarity scores.

Next, reconcile the most material growth passages, validate forecast-date financial inputs, repair candidate facet assignments, and evaluate both methods under identical information restrictions. Keep judgment-based overrides explicit and separate from computed similarity.

## Research access
- [Research website](https://barbara069.github.io/Private-Company-Public-Comparables-Search/)
- [Research code and data repository](https://github.com/Barbara069/Private-Company-Public-Comparables-Search)
