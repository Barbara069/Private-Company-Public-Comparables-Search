# Netchex — Five-Year Revenue-Index Forecast Prototype

**As of 16 November 2026. Executed scenario prototype; not a calibrated company forecast or monetary valuation.**

## What was executed

The current private-company pilot does not reliably select peers automatically. This run therefore uses a separately reviewed payroll/HCM reference basket: Paycom, Paylocity, ADP and Paychex at 25% each. Their operating roles overlap with Netchex, but their size, customer mix, client-funds income and service/PEO exposure differ. This is an exploratory reference basket, not a validated best-peer set. Asure is retained as a contextual fifth company with zero primary growth weight because its 2027 guidance includes an acquisition without a usable organic bridge. No automatic similarity scores enter the forecast.

Netchex target inputs are limited to its own website. Starting revenue, EBITDA, debt and cash are unknown. The 2026 reference revenue index of 100 is hypothetical and says nothing about Netchex’s actual financial scale or fiscal year. No fund operating metrics or hidden public-target finances enter the model.

## Five-year indexed scenarios

| Calendar year | Bear index | Base index | Bull index | Base growth |
|---|---:|---:|---:|---:|
| 2027 | 97.72 | 105.86 | 110.18 | 5.86% |
| 2028 | 96.70 | 110.85 | 118.68 | 4.72% |
| 2029 | 96.65 | 115.32 | 125.96 | 4.03% |
| 2030 | 97.36 | 119.49 | 132.38 | 3.62% |
| 2031 | 98.65 | 123.52 | 138.22 | 3.37% |

Base five-year CAGR: 4.32%. Scenario ranges are analyst sensitivities, not confidence intervals or probabilities. Dollar revenue and EBITDA/EV estimates remain unavailable.

## Sources and assumptions by stage

1. **Reported baseline:** retained LSEG annual peer revenues, with fiscal period, USD currency and retrieval date. Five annual observations provide four annual growth intervals; historical CAGR is context, not the forward growth rate. Paychex has no annual-history record in this local provider extract, so only its reported guidance growth is used in an indexed fiscal path.
2. **Management outlook:** Paycom FY2026 revenue range $2.213–$2.218 billion; Paylocity FY2027 $1.910–$1.925 billion; ADP FY2027 revenue growth about 6%; Paychex FY2027 total-revenue growth 5–6%. These are different fiscal periods, not five-year consensus. Asure FY2026 $162–$164 million and FY2027 $183–$187 million includes an October acquisition and stays outside the main aggregate.
3. **Unsupported fiscal years:** growth fades according to g_next = 3% + 0.6 × (g_last − 3%). Neither 3% nor 0.6 is empirically calibrated. Paycom has no admitted full-year 2027 revenue guidance; its 2027 value is an assumption derived by this rule, not management guidance.
4. **Calendar alignment:** fiscal annual revenue is spread uniformly across its year, then month-weighted to calendar years. June year-end uses half of each adjacent fiscal year; May uses 5/12 and 7/12. This is an approximate seasonality-free bridge, not a reconstruction from quarterly forecasts. The 2026 calendar baseline for some peers includes a guided/modelled period, not an entirely reported actual.
5. **Aggregation:** average the four peers’ log-growth rates at fixed 25% weights; effective peer count is four. Product/size/financial mismatches are disclosed; weights are not fitted or inherited from the failed automated matching.
6. **Target website:** the Mesh launch on 20 July 2026 is a real product event, but adoption, incremental price and recognized revenue are not disclosed. Spring early access and the July announcement are phases of the same product initiative. Repeated pages are not additional events. The 7,500+ organization count is an undated snapshot, not a revenue-growth rate. Base target-relative uplift is zero as a modelling default, not a factual conclusion about Mesh.
7. **Stress sensitivities:** initial target-relative log-growth shocks of −0.08 (bear), 0 (base), +0.04 (bull), with a two-year half-life. These are stress inputs, not LLM-estimated causal effects.

## EBITDA and EV/EBITDA

No starting Netchex EBITDA or margin is supplied, so the principal five-year table keeps EBITDA and EV empty. Separate conditional tables use assumed margins of 15%, 25% and 35% to show EBITDA per 100 units of hypothetical initial revenue. No margin is presented as Netchex’s observed or estimated actual margin.

The retained 27 October 2026 LSEG provider-LTM EV/EBITDA observations are Paycom 14.82×, Paylocity 17.24× and Asure 9.74× (median 14.82×). Provider EV/EBITDA arithmetic reconciles to the same provider EV and LTM EBITDA, but EBITDA definitions have not been fully reconciled to issuer adjusted EBITDA. These stale, dated multiples are reference sensitivities, not a current private-company valuation. A constant multiple is held over Years 1–5 only as an explicit scenario assumption; no future market prices are forecast.

Illustrative enterprise adjustments of 0%, 10% and 20% imply approximately 14.82×, 13.34× and 11.86× under that median reference. They are not observed private-company discounts. No equity DLOM, minority adjustment, revenue haircut or EBITDA haircut is applied. Debt and cash are unknown, so equity value is not calculated. Year-5 conditional EV is a future enterprise sensitivity, not today’s present value or a full DCF.

## Current readiness of the eight GrowthCurve companies

Only Netchex has this executed indexed prototype. The other seven remain blocked pending correctly attributed company facts, a reviewed peer basket, baseline financials and a defensible operating bridge. All eight lack supplied private revenue/EBITDA/debt. A standalone website-only numerical growth path is not supported by the available quantities. The pooled-regression challenger, weight calibration, historical backtest and unseen test evaluation have not been executed. No new train/test split was made.

## Validation and reproducibility

The code checks compounding, five-year CAGR reconciliation, calendarization arithmetic, scenario ordering, enterprise-adjustment placement, peer concentration and the absence of invented target financials. These tests validate arithmetic and source boundaries, not predictive accuracy. Present source documents were retrieved now; this is not an as-reported historical-vintage backtest.

`code/forecast_private.py` recomputes the published numbers from `website/data/private_forecast_prototype.json.gz`. The comprehensive CSV includes dataset labels for source observations, peer paths/history, assumptions, target signals, readiness, forecast scenarios, conditional valuation and validation. The notebook displays those records without loading the full source corpus into memory.

## Source links

- [PAYC_Q32026](https://investors.paycom.com/news/news-details/2026/Paycom-Software-Inc--Reports-Third-Quarter-2026-Results/default.aspx) — publication 2026-11-04; downloaded-document hash retained.
- [PCTY_Q12027](https://investors.paylocity.com/news-releases/news-release-details/paylocity-announces-first-quarter-fiscal-2027-financial-results) — publication 2026-11-05; downloaded-document hash retained.
- [ADP_Q12027](https://s205.q4cdn.com/887941133/files/content_files/ADP-1Q27-Earnings-Release.pdf) — publication 2026-10-28; downloaded-document hash retained.
- [PAYX_Q12027](https://investor.paychex.com/sec-filings/all-sec-filings/content/0000723531-26-000004/payx-ex99_1.htm) — publication 2026-09-23; downloaded-document hash retained.
- [ASUR_Q32026](https://investor.asuresoftware.com/news-releases/news-release-details/asure-announces-third-quarter-2026-results) — publication 2026-10-29; downloaded-document hash retained.
- [NETCHEX_MESH_LAUNCH](https://netchex.com/blog/netchex-mesh-ai/) — publication 2026-07-20; downloaded-document hash retained.
- [NETCHEX_MESH_EARLY](https://netchex.com/mesh/) — publication UNKNOWN; downloaded-document hash retained.
- [NETCHEX_QUOTE](https://netchex.com/request-quote/) — publication UNKNOWN; downloaded-document hash retained.

## Sensitivity diagnostics

Removing one growth peer at a time gives a 2031 base index of 122.35–124.39; the remaining three peers have 33.3% weights, explicitly above the original 25% reference weight. Varying the growth anchor from 2–4% and persistence from 0.4–0.8 gives 115.71–131.92. Adding Asure at equal five-peer weights increases the index to 127.64, illustrating the influence of acquisition-contaminated reported growth. None of these ranges is a confidence interval. The bear case explicitly permits early revenue contraction.

Retained provider observations and definitions: [LSEG fundamentals/segments](https://www.lseg.com/en/data-catalogue/company-data/company-fundamentals/business-geographic-segment-and-major-customers), retrieved 28 October 2026; issuer, fiscal dates, provider field names and market dates remain in the CSV.
