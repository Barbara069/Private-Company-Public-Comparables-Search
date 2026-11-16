# GrowthCurve Capital — Actual Private-Company Pipeline Test

**Conclusion: the current automated pipeline is not reliable enough for unattended private-company comparable selection.** Public websites contain useful business evidence, but the extraction and industry-routing stages confuse the company with its customers, partners, executives and competitors. Producing a candidate list is not evidence that it is correct.

## Test design

Tested all eight companies displayed on GrowthCurve Capital’s official portfolio page on 16 November 2026. Portfolio membership is evidence of a listed investment, not proof of 100% ownership. The fund page was used only to define the sample, never as target matching evidence. Made 50 successful page requests across the companies’ own domains, including Mistplay’s linked business subdomain. No target filings, commercial-provider target profiles, WRDS data, fund operating metrics, target financial estimates, market capitalization or actual multiples entered matching. Revenue, EBITDA and debt are UNKNOWN for all eight.

The existing 60/40 general/industry weights, retrieval, coverage adjustment and abstention thresholds were frozen. Baseline: 44 successful page requests, 54 candidates across six companies; PureFacts and Mistplay abstained. Expanded own-website coverage: six additional pages, 61 candidates across seven companies; PureFacts still abstains. These are source-coverage runs on the same eight companies, not independent test sets and not an out-of-sample accuracy estimate.

## What could genuinely be filled for a private company?

Own operating websites can support named products/services, buyer types, customer verticals, distribution, workflow, technology/deployment and supported activity/segment descriptions. They often do not support company revenue, EBITDA, debt, contract duration, customer concentration, recurring-revenue percentage, retention, capital intensity or segment revenue weights. Marketing claims and platform client metrics are not audited financials. Unknowns must stay unknown.

## Results by company

| Company | Automatic industry | General fills /32 | Top automatic candidate | Assessment |
|---|---:|---:|---|---|
| TailorMed | UNKNOWN | 5 | CareDx, Inc. | 73 / 7372 software and service activity hypothesis; hospital/pharmacy/pharma customers are end markets, not its SIC. |
| PlanHub | UNKNOWN | 6 | Xometry, Inc. | 73 / 737x software/platform hypothesis; construction is the customer vertical. |
| PureFacts | 62 | 5 | ABSTAIN | 73 / 7372 software hypothesis, not 62 securities/asset management. |
| Duetto | 80 | 7 | Jet.AI Inc | 73 / 7372 software hypothesis; hotel customers do not make it a hotel operator, and 80 healthcare is incorrect. |
| Netchex | 63 | 5 | Insperity, Inc. | 73 / 7372 software hypothesis, not 63 insurance carrier. |
| Revecore | 63 | 5 | CorVel Corporation | 73 / 7389 business-service hypothesis; 7372 only for separately established software activities. Not an insurance underwriter. |
| Brightway Insurance | 63 | 8 | Ryan Specialty Holdings, Inc. | 64 / 6411 insurance agency/broker hypothesis, not 63 insurance carrier. |
| Mistplay | UNKNOWN | 6 | PLAYSTUDIOS, Inc. | 73 / 7311 advertising plus software activity hypothesis; gamers are users, advertisers/publishers form the business side. |

The review checked all 256 general-facet slots and flagged each populated field as supported in reviewed context, partial/contaminated, or unsupported. Industry assignments remain unvalidated because routing is wrong or absent. A supported excerpt is not independent factual corroboration. No reviewed-complete peer basket or valuation is claimed.

### Concrete failure cases

**TailorMed** — Workforce geography is not customer geography. Manufacturer-support activity is not drug manufacturing. CareDx is a diagnostic/testing business; proximity to healthcare does not establish the same offering. GoodRx is an adjacent medication-access candidate to investigate, not a validated peer.
Website-supported business description (analyst paraphrase): Provides medication-access, affordability and adherence coordination, including care-team software and assisted services. [Own website](https://www.tailormed.com/)

**PlanHub** — FAQ questions are not value-chain facts; platform seats and subscription regions are not supply-chain complexity. Xometry operates a manufacturing-sourcing marketplace. Marketplace overlap alone does not establish construction-workflow equivalence.
Website-supported business description (analyst paraphrase): Connects general contractors, subcontractors and suppliers with project discovery, bidding and takeoff/estimation tools. [Own website](https://planhub.com/)

**PureFacts** — Client fee/billing economics were mistaken for vendor monetization; a North American AUM benchmark was mistaken for its served geography. The pipeline abstains. That avoids a forced list but does not mean no public peer exists.
Website-supported business description (analyst paraphrase): Provides a connected platform for practice management, fees and billing, compensation, and a revenue book of record for financial firms. [Own website](https://purefacts.com/)

**Duetto** — Executive career histories contaminated product, business-model, delivery and geography fields. Jet.AI and hotel operators are poor primary-business matches for hotel revenue-management software; reject this basket as a recommendation.
Website-supported business description (analyst paraphrase): Offers hotel pricing, forecasting, group-business and profitability tools through its revenue/profit operating system. [Own website](https://www.duettocloud.com/)

**Netchex** — A Transamerica partner description was attributed to Netchex; implementation timing is not a customer segment. Insperity has relevant HR/payroll overlap but PEO/service economics differ from software; this requires an operating-role comparison.
Website-supported business description (analyst paraphrase): Provides payroll, time/attendance, hiring/onboarding and HR tools for employers, with an emphasis on hourly/frontline work. [Own website](https://netchex.com/)

**Revecore** — Payer rules, coverage intelligence and claims data describe customer workflows, not evidence that Revecore underwrites insurance. CorVel is an adjacent claims-management business; payer/employer versus hospital-client workflows must be distinguished before accepting it.
Website-supported business description (analyst paraphrase): Combines claims expertise, automation and its ReClaim platform to recover complex claims, underpayments and denied revenue for health systems. [Own website](https://revecore.com/)

**Brightway Insurance** — Testimonials and FAQ questions contaminate fields. Own pages give 2003 versus 2008 founding statements; entity/event scope must be resolved. Annual premium is not company revenue. Ryan Specialty and Goosehead have insurance-distribution relevance. Safety Insurance is a carrier, so the list mixes different economic roles.
Website-supported business description (analyst paraphrase): Supports independent agency owners with branding, carrier access, technology and centralized client service; carriers underwrite policies. [Own website](https://www.brightway.com/)

**Mistplay** — The consumer homepage caused a competitor Freecash description to enter Primary Products. Advertiser-facing pages improve coverage but do not remove the bad assignment. PLAYSTUDIOS has a loyalty/gaming adjacency. A generic gaming or casino supplier is not automatically a comparable rewarded-advertising network.
Website-supported business description (analyst paraphrase): Connects rewarded gameplay with publisher/advertiser user acquisition and offers loyalty-platform capabilities; consumer and business pages describe different sides. [Own website](https://www.mistplay.com/)

## Required fixes before valuation

1. Extract issuer-owned business claims from product/company pages and relevant business subdomains; reject biography, testimonial, customer-story and competitor subjects at paragraph level. Keep source quotations separate from inferred categories.
2. Separate seller activity from customer industry and distinguish paying customer, end user and partner. Route software vendors to software modules and insurance agencies to agency/broker modules, while retaining relevant end-market facets.
3. Require correctly attributed primary offering and business-model evidence before ranking; display coverage as availability, never as factual correctness. Withhold baskets that fail this gate.
4. Review an independent labeled target–candidate set before fitting weights or reporting accuracy. This eight-company diagnostic must not become a repeatedly tuned holdout.
5. Use the corrected private target facts only when rerunning; preserve the failed baseline and expanded-source runs so improvements are auditable. Do not forecast or assign private-company discounts from these current baskets.

## Files and provenance

`GrowthCurve_Private_Pilot.csv.gz` contains the downloaded text/URLs, isolated private inputs, every general and routed industry fill, baseline and expanded candidate scores, score evidence, and analyst review. The 560-company production target set and published rankings were not overwritten by this diagnostic. The full evidence dataset is supplied as a separate downloadable pilot artifact; the public report contains paraphrased findings.

[GrowthCurve official portfolio](https://www.growthcurvecapital.com/portfolio) · [Pipeline code](https://github.com/Barbara069/Private-Company-Public-Comparables-Search/tree/main/code)

All results are preliminary research diagnostics; no accuracy claim or numeric revenue forecast is made.
