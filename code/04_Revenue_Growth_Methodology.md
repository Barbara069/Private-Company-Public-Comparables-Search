# 04. Five-Year Private-Company Revenue, EBITDA and Valuation Forecasting

**Methodology and execution status | 20 November 2026 | Company-specific peer + website scenarios executed for 96 targets; 464 insufficient-evidence outcomes; no calibrated accuracy claim**

**Source restriction:** No WRDS-delivered data, text, ratios, classifications, joins or derived results are eligible for this pipeline, exports or website. Reacquire needed facts independently from permitted original sources; never relabel the old database text as another provider. Other providers remain subject to their own access and redistribution rights.

## Current executed implementation — 20 November 2026

- **Coverage:** 560 targets evaluated; 96 company-specific provisional scenarios and 464 explicit insufficient-evidence outcomes. Minimum support is an admitted target-website signal plus two independent selected peers and at least 20% coverage of the original basket's squared-score weight. This threshold is an analyst assumption, not an accuracy gate calibrated on outcomes.
- **Peer growth sources:** existing permitted LSEG annual records and consolidated, dimension-free SEC inline-XBRL revenue from retained original annual filings. The current run extracted 174 SEC peer series. Exact issuer IDs are used; target's own issuer is excluded. Peer quarter/annual MD&A passages are displayed as source context; percentages are not blindly harvested from arbitrary sentences.
- **Forward hierarchy actually implemented:** reuse dated guidance only for exactly matched issuers in the reviewed public-source pilot bundle. Otherwise use the median of up to three peer annual log-growth observations as an explicitly labeled historical extrapolation, then fade toward the selected basket's historical median log-growth anchor with persistence 0.6. Fiscal-calendar alignment uses a disclosed uniform-within-year approximation. FY4/FY5 consensus is not invented.
- **Weights actually implemented:** squared existing Ranking Score × growth-quality factor, normalized over a fixed financially usable cohort. The growth-quality factor is 0.5 if M&A/disposal appears in retained peer growth passages, otherwise 1; this is a simple disclosed risk heuristic, not an organic-growth audit. Show all exclusions and original-basket coverage.
- **Target website contribution:** exact same-domain business-site passages; exclude investor/filing/financial-result mirrors. Unquantified claims have **zero base-rate uplift**. Operational opportunities/risks widen the respective upside/downside log-growth sensitivity by 50% of observed peer dispersion, decaying with a two-year half-life. This coefficient is a transparent analyst sensitivity, not a fitted causal estimate. Context-only statements do not widen scenarios.
- **Financial baseline:** supplied revenue, EBITDA and debt are shown with original workbook cells. Forecast index starts at 100 in 2026. Conditional original-unit revenue equals supplied revenue × index / 100 **only if** that supplied value is treated as the 2026 baseline; its actual period/currency/scale remain unconfirmed. A supplied EBITDA/revenue ratio can be chosen as an explicitly conditional margin sensitivity. No target cash or hidden public financials are introduced.
- **Example:** Wendy's uses McDonald's 53.59%, Restaurant Brands International 24.18%, Yum! 22.23%; its base 2031 revenue index is 143.57 (2026=100), versus Paylocity's independently computed 136.12. These are uncalibrated provisional paths, not investment forecasts.
- **Reproduction:** `code/build_target_growth_forecasts.py` reads the existing permitted website data and retained original SEC files under the project workspace. Output: `website/data/target_growth_forecasts.json.gz`; derivations are retained in the comprehensive research CSV. Run `python code/test_target_growth_forecasts.py` and `node code/test_forecast_company_binding.js`. Tests include hidden-target-history mutation, source-domain filtering, self-peer exclusion, path arithmetic, company identity and no universal replacement curves.

The sections below distinguish the full research design from this narrower executed fallback. Margin convergence, learned website coefficients, full peer consensus coverage and predictive holdout validation remain unimplemented.

## 1. Objective and deliverables

For each eligible private target, estimate annual revenue, EBITDA, and EV/EBITDA for Years 1–5, with bear/base/bull scenarios, explicit assumptions and linked evidence. Combine (A) public-comparable historical growth and forward expectations with (B) growth signals on the target’s official website. Keep a pooled regression as a challenger rather than fit 49 separate small industry models.

Report separately: current public-equivalent EV/EBITDA; current target-adjusted multiple; each future year’s contemporaneous EV/EBITDA; Year-5 exit multiple; and today's implied value. These have different dates and denominators. An EV/EBITDA forecast is not obtained by simply growing today’s multiple with revenue.

Primary outputs are a five-year financial table, an assumption/evidence ledger, selected-peer table, scenario/discount sensitivity table, and validation results. Forecasts require a dated starting financial baseline. If dates, units or accounting definitions cannot be reconciled, output an illustrative indexed path or an insufficient-data result instead of a precise currency valuation.

## 2. Target information firewall

**Reconfirmed 20 November 2026:** the three allowed numerical target inputs are **revenue, EBITDA and debt**, sourced only from the supplied instructor workbook. The only target qualitative/growth source is its official business website. Public-comparable financial histories, guidance, consensus where licensed, filings and growth signals belong to the **peer side**, never to the target bundle.

**Required forecast construction:** freeze the selected public-comparable basket; derive a dated, weighted peer forward-growth path; extract dated positive and negative operational signals from the target website; then apply an evidence-supported relative adjustment or operating-bridge blend as described in Sections 6–7. Unknown website effects stay qualitative or scenario assumptions. Debt informs financial-risk/valuation sensitivities, not an automatic revenue-growth uplift. Target EBITDA supplies the initial margin only when its period and definition reconcile with revenue.

**Display is not model input:** the website's full-public 2022–2026 history may be displayed for research, but must not enter target forecast retrieval, prompts, peer selection, parameter fitting or calibration. The universal 0%/5%/10% paths have been removed from target pages. The current run uses each target's own provisional selected peers, source-linked peer revenue histories/available dated guidance, and official-website operating signals. Unsupported targets receive an insufficient-evidence result, not a replacement curve.


The original 560 public companies are simulated-private targets. Permitted inputs are their official website and the instructor-file revenue, EBITDA and debt. Use original values; do not fabricate missing numbers. Record currency, scale, period and whether debt is supplied directly or derived from an instructor ratio. Cash is unavailable unless explicitly authorized; debt is not automatically net debt.

Exclude target SEC reports, vendor financial histories, consensus estimates, market capitalization, stock prices, actual EV/EBITDA, and hidden segment financials from extraction prompts, retrieval, matching, assumptions and model tuning. A target’s unrestricted research profile remains separate. Do not pass it to the forecasting agent even as context. Target website pages replicating filings, stock information, or unauthorized financial outcomes are also excluded. Allowed website operational disclosures may supply growth signals; they do not authorize additional target revenue history.

Each target run receives a separate allowlisted evidence bundle. Public-as-private training examples must obey the identical restriction. Hidden outcomes are accessible only to the evaluator after forecasts are frozen. Current website data cannot be used to predict already-realized historical outcomes.

## 3. Source-to-field extraction matrix

| Source | Download and retain | Use | Limits |
|---|---|---|---|
| Instructor workbook | Target revenue, EBITDA, debt and original cell locations; units and dates if stated | Starting financial baseline | Missing metadata is unknown, not assumed |
| Target official website | Product/customer pages, operating locations, dated launches, expansions, customer wins, capacity plans, partnerships, closures and management operational outlook | Website-only target facets and forward growth signals | Exclude hidden public-company financial disclosures and outside target news under the current policy |
| Capital IQ supplied Excel | Available peer financials, descriptions, identifiers, periods and industry fields | Peer financial baseline and identity reconciliation | Do not assume the workbook contains consensus forecasts |
| LSEG | Entitled peer revenue/EBITDA history, business/segment descriptions, available FY1/FY2/FY3 estimates, contributor count, estimate date and dispersion | Public-peer outlook and financials | Discover actual field codes and entitlement first; unavailable estimates remain unavailable |
| SEC submissions/company facts and filings | Public-peer 10-K/20-F, updates in 10-Q/6-K, MD&A, segment notes, debt, reconciliations, revenue bridges | Reported actuals, organic/acquired growth, normalized EBITDA and operational drivers | SEC generally supplies reported facts, not sell-side consensus forecasts; retain accession and periods |
| Peer official IR releases/calls | Dated guidance ranges, assumptions, unit/customer growth, pricing, bookings and margin outlook | Peer forward bridge; verify changes since consensus snapshot | Guidance is management expectation, not realized results; issuer-defined metrics need definitions |
| Search and attributable news | Search query plus downloaded destination passage, URL, publisher/date and issuer linkage | Discover or corroborate public-peer evidence | Search snippets alone are discovery evidence; no invented or inaccessible transcript text |
| FF49 / industry references | SIC-to-FF49 mapping and peer/industry populations | Industry controls and sector anchors | FF49 is a classification here, not a stock-return factor; target assignment must come from permitted website text |

Download the latest five completed peer fiscal years plus dated available forward estimates. One additional opening balance may be needed to calculate five annual changes; do not collect 2010 onward by default. Keep historical FX, nominal/real and fiscal-calendar conventions explicit. Do not blend GAAP EBITDA, adjusted EBITDA and operating income without a bridge.

Every observation needs: observation_id, issuer_id, segment_id, field, raw value/text, normalized value, unit/currency, period, publication/estimate-as-of date, retrieval date, direct URL or workbook/sheet/cell, source family, underlying vendor, document hash, exact excerpt locator, allowed_target_input, validation status and discrepancy note. Derived values reference their input IDs and formula version. Downloading, citation matching and semantic verification are separate states.

## 4. Reconcile sources before forecasting

1. Resolve economic issuer identity, share classes, listed subsidiaries and parent relationships. Do not average parent/subsidiary duplicates as independent companies.
2. Compare only the same period, entity/segment, currency and metric definition. Record historical restatements and continuing/discontinued operations.
3. For public-peer reported facts, prefer the newest applicable regulatory report and retain the superseded observation. For forward estimates, retain the newest available-as-of snapshot; guidance and consensus remain distinct.
4. Classify comparisons as agreement, compatible detail, time difference, scope difference, definition difference, genuine contradiction or insufficient evidence. Text similarity alone cannot decide factual consistency.
5. Material unresolved contradictions block the affected driver, not necessarily the entire company. Show the selected source and a short discrepancy note alongside alternatives.

## 5. Freeze the public-comparable basket

Select 5–10 public issuers where supported; do not force ten or fill the basket with weak peers. Review offering, customer, revenue model, value-chain role, geography, industry-specific economics and business mix using only allowed target information. Size checks may use permitted revenue/EBITDA/debt once units align. No target multiple is used to select peers.

Candidate review precedes numerical weighting. A provisional forecast weight is q_j = (S_j/100)^2 × C_j × Q_j × F_j, normalized across eligible peers. S is observed business similarity, C evidence coverage, Q reviewed source/definition quality, and F financial-period/forecast comparability. These are analyst assumptions to test, not learned probabilities. Suggested Q/F anchors are 1 for reconciled, 0.5 for usable with a material limitation, and 0 for unusable. Publish every factor. Do not silently treat missingness as business mismatch.

With at least five peers, cap a single issuer group at 25%, redistributing weights iteratively among eligible groups. When the basket is too small for the cap, disclose concentration rather than pretending the cap holds. Report equal-weight median, effective peer count 1/Σw², and leave-largest-peer-out sensitivity. Freeze peers and weights before forecasting and evaluation.

## 6. Path A: public-comparable revenue outlook

### Historical anchor

For each peer compute annual revenue growth, three-/five-year CAGR, volatility and organic growth when disclosed. Flag acquisitions, disposals, FX, closures and abnormal recovery years. Never equate trailing CAGR with a forward forecast. Use weighted medians as robust references and show distribution/sample size.

### Forward peer paths

For each peer and year, prefer dated, calendar-aligned consensus revenue levels where available; then management guidance; then an explicit historical/industry fallback. Do not average conflicting guidance and consensus indiscriminately: retain one primary path, an alternative scenario and the reason. Convert revenue levels into growth on the same basis. Where fiscal calendars differ materially, calendarize or disclose approximation.

No invented FY4/FY5 consensus: extend the last supported peer growth gradually toward a sector/maturity anchor. The anchor uses available-as-of training evidence and macro assumptions, and is labeled an assumption. Both contraction and recovery are allowed. A provisional extension is g_(h+1) = g_anchor + rho × (g_h − g_anchor), with rho initially 0.6 for sensitivity testing, not a universal fitted constant.

Aggregate in log growth: mu_peer,h = Σ w_j × log(1 + g_j,h). Display public peers’ forward revisions, estimate age, dispersion and fallback share. Missing future observations do not silently change basket composition year by year: fill eligible missing paths transparently, or use a fixed common-coverage basket and show exclusions.

## 7. Path B: target website growth signals

### Structured extraction

Extract both positive and negative signals: net location expansion, customer wins/losses, churn/retention where disclosed, new products, capacity increases, partnerships, geographic entry/exit, closures, delays and regulatory milestones. For each retain exact source text, URL/date, scope, status (plan/in progress/completed), numerical amount/unit if stated, timing, cancellation conditions and whether the event is already reflected in the baseline.

Promotional language such as “leading” or “rapidly growing” receives no numerical uplift by itself. Three pages repeating one press release are one event. A missing signal is not evidence of no growth.

### Quantify with operating bridges where possible

| Business | Useful bridge | Required cautions |
|---|---|---|
| Restaurants/retail | System/unit growth, owned-store comparable sales, royalty revenue and opening ramps | System sales are not consolidated revenue; distinguish franchisor and operator |
| SaaS | Customer growth × revenue/customer, retention, pricing and recognized-revenue lag | ARR/bookings are not GAAP revenue; do not add net retention and expansion twice |
| Manufacturing | Capacity × utilization × realized price/product mix | New capacity requires commissioning, demand and funding |
| Services | Billable capacity × utilization × rate | Hiring announcements do not prove productive headcount or demand |
| Project businesses | Backlog conversion + new awarded work recognized within the year | Avoid double-counting work already in backlog; project timing matters |
| Other industries | Industry-specific volume × yield/price bridge | Financial firms may require revenue and valuation definitions other than EBITDA |

Where the website does not disclose sufficient quantities, record a qualitative directional feature. Estimate its numerical effect from public training examples with the same restricted information, or keep a bounded analyst scenario. LLM judgment extracts/structures evidence; it must not invent a percentage effect.

### Combine the two paths without double counting

If a complete target operating bridge exists, compute its independent log-growth path mu_signal,h and blend: mu_final,h = (1 − lambda_h) × mu_peer,h + lambda_h × mu_signal,h. If only relative signals exist, use mu_final,h = mu_peer,h + delta_h, where delta represents the target-minus-peer difference in drivers. Do not apply both rules to the same event.

Calibrate lambda and delta on grouped development folds. Before calibration, publish alternative lambda scenarios (0, 0.25, 0.5), rather than call one empirically optimal. Effects fade after the event horizon; a provisional two-year half-life is a sensitivity, not a fact. Material signed contracts or capacity ramps can have different documented schedules. Peer expansion/pricing already embedded in peer growth only justifies an adjustment when target exposure differs.

Revenue_h = Revenue_0 × exp(Σ_(k=1..h) mu_final,k). All five annual outputs must reconcile to the stated five-year CAGR. If a segment lacks revenue shares, do not borrow hidden target segment accounts: publish company-level results and mix scenarios. Geographic reporting segments need not be distinct business models; economically different activities do.

## 8. EBITDA forecast

Starting margin m_0 = EBITDA_0 / Revenue_0 only when periods and definitions align. Forecast margins separately from revenue growth. Use reconciled public-peer forward margins, maturity and operating economics; quantify ramp costs, pricing/cost pressure and fixed-cost leverage only with evidence.

A transparent initial bridge is m_h = m_0 + a_h × (m_peer,h − m_0) + b_h. The convergence schedule a_h and evidenced adjustment b_h are calibrated or labeled analyst assumptions; margins need not converge to peers. EBITDA_h = Revenue_h × m_h. Keep accounting-adjusted and reported variants separate. Negative or near-zero EBITDA makes EV/EBITDA unreliable; show N/M and consider an explicitly separate EV/revenue or cash-flow approach, not an arbitrary multiple.

## 9. Five-year EV/EBITDA framework

For public peers, distinguish EV_0 / EBITDA_0, EV_0 / expected EBITDA_h (today’s forward multiple), and expected EV_h / EBITDA_h (future contemporaneous multiple). Consensus earnings do not provide future EV automatically.

Forecast the target’s future public-equivalent multiple using either (A) a regularized pooled public-market model of log multiples versus forward growth, margin, business model, capital intensity and risk, with industry controls; or (B) a transparent same-date peer-median anchor with scenario-based mean reversion. Use out-of-time market data and comparable definitions. If a fitted model is unsupported, choose B and label the multiple path an assumption. Do not claim precision from a 49-industry model with tiny samples.

Growth and margin forecasts may enter a multiple model because market pricing reflects them, but adding a second manual “growth premium” for the same effect double counts. Separate operating adjustments, market-cycle uncertainty and ownership/liquidity effects.

For each h: EV_h = adjusted_multiple_h × EBITDA_h. Year-5 EV is an exit enterprise value, not today’s value. Do not discount EV_5 alone and call it a full DCF. A DCF cross-check needs intervening FCFF, tax, capex, depreciation, working capital and WACC; these are not known from the permitted three target figures and would require clearly labeled peer-based assumptions. No full DCF is necessary for the initial comps-based deliverable.

## 10. Private-company adjustment: no automatic haircut

First define the interest valued: a controlling enterprise sold to a strategic/financial buyer, or an illiquid minority equity holding. Public-to-private differences in size, concentration, governance and operational risk must be evidenced; “private” alone does not prove a fixed discount.

**Enterprise adjustment:** apply documented residual operating/transferability differences to public-equivalent enterprise multiples, only if not already reflected in growth, margins, peer selection or the fitted multiple. A simple sensitivity is M_private,h = M_public,h × (1 − d_enterprise,h). Before calibration, present 0%, 10% and 20% as illustrative sensitivities only, with no asserted universal base discount. Private transaction comparisons may inform this after controlling for date, sector, scale, leverage, control and EBITDA definition; headline deal multiples alone are insufficient.

**Equity marketability adjustment:** where the valuation mandate calls for an illiquid equity interest, first bridge enterprise to equity: Equity_pre = EV + cash − debt − other senior claims, adding nonoperating assets where applicable. Apply a separately justified DLOM to the relevant equity interest. Cash and future debt are currently unknown, so absolute equity value may be unavailable. Do not subtract debt twice, apply DLOM to EV by default, or stack a generic minority discount and generic private discount.

Carry distinct columns for public-equivalent EV/multiple, enterprise-adjusted EV/multiple, equity before marketability, DLOM assumptions and equity after adjustment. Do not discount forecast revenue or EBITDA for illiquidity. Show financing/key-person/customer concentration effects once in the assumption ledger. Public-as-private tests can evaluate the liquid-equivalent model; they cannot empirically validate a genuine private-company discount. That requires suitable private transaction/holding evidence.

Conceptual references: [Damodaran: private-company valuation](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/lectures/pvt.html), [illiquidity considerations](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/illiquiddisc.htm), and [cash-flow/discount-rate consistency](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/lectures/approach.html). These inform the framework, not the proposed numerical scenario settings.

## 11. Scenarios and uncertainty

Generate coherent bear/base/bull paths for demand, pricing, execution/ramp, margins and market multiples. Bear should include failed/delayed signals; bull must remain capacity/demand constrained. Estimate ranges from grouped/time-based residuals and peer dispersion when possible. An illustrative scenario range is not a calibrated 80% interval. Account for shared sector and macro shocks; do not independently bootstrap highly correlated peers and claim narrow confidence.

Show Year-1 to Year-5 revenue and EBITDA, margin, annual growth, cumulative CAGR, public-equivalent and adjusted multiples/EV, source coverage and sensitivity to each major assumption. Include a two-dimensional Year-5 margin × exit-multiple sensitivity and a separate private-adjustment sensitivity. Freeze assumptions before viewing hidden target outcomes.

## 12. Validation design

Do not split or resplit the dataset as part of this planning task. At execution, preserve existing development use and establish a genuinely untouched test population. The original 160-company holdout has already informed research and cannot simply be relabeled unseen. A proposed 75% development / 25% final test is a future protocol requiring an approved fresh partition, grouped by economic issuer; tuning happens inside development only.

For historical validation, forecast-date target website snapshots, peer actuals/estimate vintages and guidance must precede the cutoff. Mask any target appearing in its own peer basket; deduplicate parent/share-class relations and prevent their crossing folds. Sector overlap is acceptable but economic-group leakage is not. Restrict public peers to those actually observable and eligible at the cutoff to avoid survivorship bias.

Compare: sector-median fallback; historical-peer-only; peer-forward-only; website-only where supported; combined forecast; pooled regression challenger. Perform ablations for signals, segments, industry facets and financial size. Use identical targets and report coverage/abstention separately.

Metrics by horizon: revenue WAPE and median absolute log error, signed bias and CAGR error; EBITDA absolute error scaled by starting revenue (also valid near zero), margin error; multiple APE only for positive meaningful multiples; EV error separately. Show sector/size/source-coverage slices and grouped bootstrap intervals. A five-year forecast requires five years of future outcomes for validation; shorter realized horizons do not validate Year 5. Private discount validation remains a separate study.

## 13. Implementation sequence and acceptance gates

1. **Audit baseline:** verify instructor units/dates and allowed-input bundles. Inventory existing CSV fields and identify actual missing peer histories/estimates. No claimed complete extraction without a coverage table.
2. **Pilot five targets:** Wendy’s, Paylocity and three contrasting businesses chosen before results. Use one frozen peer basket per target, website-only signal packets and all five forecast years.
3. **Retrieve and reconcile:** five-year peer history; forward consensus where licensed; guidance and source text; target website events. Unresolved critical definitions block numerical output.
4. **Build transparent baselines:** peer forecast, signal bridge, EBITDA margin and multiple paths; all adjustments have evidence or explicit assumption tags. Generate scenario and concentration diagnostics.
5. **Human review:** check identity, franchise/operator economics, target leakage, signal timing, acquisition/organic double counting and discount placement. Approve the pilot layout before scaling.
6. **Batch eligible 560 targets:** resumable per-company execution; unknowns/abstentions retained. Publish counts of baseline-ready, peer-ready, signal-supported, forecast-ready and blocked targets.
7. **Backtest and calibrate:** obtain historical snapshots/vintages before any claim of predictive performance; tune only on development. Freeze method, then evaluate untouched data.
8. **Publish results:** update website and canonical GitHub repository only after checking source licensing and public-display boundaries. This plan alone does not publish results or authorize fabricated forecasts.

## 14. Files, website and reproducibility

Retain one comprehensive `Research_Data.csv.gz`, using dataset and entity-role columns to separate targets, public peers, evidence, assumptions and forecasts. Add each relevant sourced observation to that CSV; forecasts and assumptions can be additional record types. Link full raw document payloads by hash/location rather than replicate entire filings for every facet. A single analysis notebook reads the comprehensive CSV and produces all forecast tables; no need for a proliferation of manually maintained intermediate deliverables.

Suggested forecast record keys: target_id, forecast_asof, scenario, horizon_year, revenue, growth, EBITDA, margin, public_equivalent_multiple, enterprise_adjustment, adjusted_multiple, EV, currency, peer_basket_id, model_version, assumption_ids, evidence_ids, validation_state. Equity fields are nullable where cash/debt-path evidence is missing. Source observations are immutable; recalculated outputs receive a version and timestamp.

Website Growth & Revenue Forecast stays immediately before Evidence sources. Display allowed target inputs, five-year table, public-peer outlooks and their sources, website signal ledger, assumption waterfall, uncertainty and private-adjustment basis. Show “proposed / illustrative / calibrated / backtested” accurately. Public pages must not expose licensed vendor text or estimates merely because they are available locally.

## 15. Worked arithmetic example — fictional, not a company forecast

Assume permitted Revenue_0 = 100 and EBITDA_0 = 15 in consistent units. Public-peer growth is 8%, 7%, 6%, 5%, 4%; an explicitly hypothetical target-relative website effect adds 1, 0.5, 0, 0, 0 percentage points. For simple illustration in annual-rate space, resulting growth is 9%, 7.5%, 6%, 5%, 4% (production uses the log-growth equations above).

| Year | Revenue | EBITDA margin | EBITDA | Public-equivalent multiple | 10% illustrative enterprise adjustment | Adjusted EV |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 109.00 | 15.5% | 16.90 | 10.0× | 9.00× | 152.06 |
| 2 | 117.18 | 16.0% | 18.75 | 9.8× | 8.82× | 165.36 |
| 3 | 124.21 | 16.5% | 20.49 | 9.6× | 8.64× | 177.07 |
| 4 | 130.42 | 17.0% | 22.17 | 9.4× | 8.46× | 187.56 |
| 5 | 135.63 | 17.0% | 23.06 | 9.2× | 8.28× | 190.92 |

Values are rounded for display; calculations use unrounded inputs. The 10% is a sensitivity, not an estimated private discount. Year-5 EV is measured in Year 5 and is neither present value nor equity value. No factual forecast or observed private-company discount is established by this example.

## 16. Executed private-company prototype — 16 November 2026

[Netchex worked report](Netchex_Revenue_Forecast_Prototype.md) documents an executed five-year indexed scenario, using a separately reviewed payroll/HCM reference basket rather than the failed automated private-company peer lists. Revenue is normalized to a hypothetical 2026 level of 100; base 2031 index is 123.52 (4.32% scenario CAGR), with illustrative bear/bull indices 98.65/138.22. No Netchex dollar revenue, EBITDA, debt or cash is supplied. Conditional margin/multiple sensitivities are clearly separate from target financial estimates.

Peer guidance comes from the issuer releases dated September–November 2026. Unsupported years use explicit growth-fade assumptions; fiscal/calendar alignment assumes uniform intrayear revenue. The website Mesh product event is observed, but adoption/pricing/revenue effects are unknown, so no automatic base uplift is applied. Source vintage, acquired growth, PEO mix and EBITDA-definition limitations remain material. The standalone website-only quantitative path, pooled regression, empirical calibration, backtest and private-discount estimation remain unexecuted. No new train/test split was created.

Run `python code/forecast_private.py --input website/data/private_forecast_prototype.json.gz --output /tmp/forecast_reproduced.json` to reproduce the published scenario arithmetic. `Forecast_*` records in the comprehensive CSV preserve source facts, assumptions, calendarized peer paths, scenarios, conditional valuations and diagnostics. This prototype is not approval to use the current automatic baskets for valuation or to forecast all 560 targets without the acceptance gates above.
