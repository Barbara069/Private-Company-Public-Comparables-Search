# 03. Similarity Scoring Standard — Proposed v3.1

Version: 2026-11-12. Status: proposed v3.1 research protocol, not a calibrated prediction model. Historical website scores still use the legacy v2 method; they have not been recomputed under this standard or the new SIC dictionary.

## Scoring Framework and Industry-Specific Weighting

Use the same evidence rules, score anchors, missing-value treatment and formulas for everyone. Select a target-level policy from its permitted business information before scoring candidates; freeze that policy for all candidates of that target. Industry relevance can change weights, but candidate missingness or a desired ranking cannot. P0–P3 extraction priorities are not numerical weights.

Default: general facets 60%, industry facets 40%. Proposed sector variants: subscription software 55/45, financial services 50/50, professional services 65/35. All other targets use 60/40 until a justified policy is approved. These are analyst judgments requiring validation, not empirically optimal weights. No data split has been created in this revision.

## General facet weights (within the general block)

| ID | Facet | Priority | Weight % |
|---|---|---|---:|
| G01 | Primary Products | P0 | 10 |
| G02 | Primary Services | P0 | 5 |
| G03 | Core Business Activity | P0 | 0 |
| G04 | Customer Type | P0 | 5 |
| G05 | Customer Segment | P0 | 4 |
| G06 | End Markets | P0 | 7 |
| G07 | Customer Size | P0 | 3 |
| G08 | Business Model | P0 | 9 |
| G09 | Revenue Model | P0 | 9 |
| G10 | Value Chain Position | P0 | 5 |
| G11 | Geography Served | P0 | 3 |
| G12 | Product Specialization | P1 | 3 |
| G13 | Distribution Channels | P1 | 3 |
| G14 | Delivery Model | P1 | 3 |
| G15 | Pricing Structure | P1 | 3 |
| G16 | Recurring Revenue Profile | P1 | 4 |
| G17 | Customer Concentration | P1 | 2 |
| G18 | Contract Duration | P1 | 2 |
| G19 | Capital Intensity | P1 | 3 |
| G20 | Regulatory Exposure | P1 | 3 |
| G21 | Customer Switching Costs | P1 | 3 |
| G22 | Company Size Category | P2 | 2 |
| G23 | Labor Intensity | P2 | 1 |
| G24 | Revenue Cyclicality | P2 | 2 |
| G25 | Supply Chain Complexity | P2 | 1 |
| G26 | Technology Dependence | P2 | 1 |
| G27 | Geographic Concentration | P2 | 1 |
| G28 | Product Differentiation | P2 | 1 |
| G29 | IP Dependence | P2 | 1 |
| G30 | Brand Dependence | P2 | 1 |
| G31 | Competitive Positioning | P3 | 0 |
| G32 | Company Maturity | P3 | 0 |

The business activity field is a required relevance gate but has no extra numerical weight because product/service, operating model and value-chain fields already capture it. Competitive-positioning claims and maturity remain optional diagnostic context. Company size is the supplier’s size; Customer Size is its buyers’ size. Duplicate economic facts must not earn weight twice.

## Industry block

The operational proposal is now the **explicit per-field schedule in the appendix**: all 83 SIC2 modules and 546 fields are listed with importance points, base reference percentages and activation rules. Earlier 25/30/15/20/10 economic-dimension budgets were conceptual planning guidance; they are superseded by this field-level schedule and are not an additional set of simultaneous weights. The five dimensions remain useful explanation categories, not a second weighting layer.

Weights are analyst-proposed starting assumptions, not fitted or empirically validated coefficients. Activate only evidenced applicable activities/subtypes and exclude duplicate economic dimensions before freezing a target policy. Do not treat all 546 fields as applicable or normalize away missing candidate evidence. Performance KPIs and unavailable target facts remain diagnostic. Historical website results have not been recomputed with this appendix.

## Per-facet judgments

100 = same economic offering/role/customer need; 75 = close substitute with a limited material difference; 50 = adjacent with meaningful overlap and material differences; 25 = weak overlap; 0 = evidenced economic mismatch. Each judgment needs the two source excerpts, scope/date, matching and mismatching dimensions and rationale. Word overlap or cosine similarity can retrieve candidates; it is not sufficient evidence of economic equivalence. No evidence means UNKNOWN, never zero and never an automatic positive score.

## Similarity and completeness are separate

Let applicable base weights w sum to 1, reviewed observed facet similarities s be between 0 and 1, and O contain facets supported on both sides by eligible evidence:

- Evidence coverage C = sum(w for observed facets).
- Observed similarity S = 100 × sum(w × s for observed facets) / C; undefined when C = 0.
- Evidence-supported points E = 100 × sum(w × s for observed facets).
- Missing-information bounds = [E, E + 100 × (1 − C)]. These are arithmetic bounds, not statistical confidence intervals.

Show all three values: S, 100C and E. Separately report source collection, source-type diversity, semantic-review completion and unresolved conflicts. Having three sources does not imply independent corroboration. Source identity/period/scope conflicts must be resolved or excluded from O. Missing evidence does not change base weights; genuine non-applicability must be determined at target level with a reason before candidate comparisons.

Preliminary final-ranking gate: at least 80% overall coverage, at least 70% coverage in each block, reviewed critical business facets, resolved issuer identity, no unresolved material conflicts and no forbidden target inputs. These are proposed minimums, not a guarantee of good comparables. Until those gates pass, label results exploratory and abstain from final recommendations.

## Multiple segments and valuation suitability

Compare segment activities separately. Use source-supported segment importance weights only when available under the target’s permitted information; do not borrow hidden SEC revenue shares or assume equal weights. If the target mix is unknown, present segment-specific comparisons or explicit sensitivity scenarios and withhold a single definitive blended score.

Business comparability and valuation suitability are separate gates. For banks and insurers, EV/EBITDA is generally not the appropriate automatic valuation basis; establish a sector-specific downstream valuation protocol instead. Similarity does not justify mixing incompatible periods, accounting definitions or capital structures.

## Evidence discipline

Retain original excerpts, sources, document and fact dates, units, entity and segment scope. The source-priority rule is newest applicable authoritative disclosure, after checking definitions and scope; a newer unrelated document does not override all older facts. Public research may use SEC/LSEG/WRDS/web sources. Pseudo-private target matching may use only approved official business-website information and instructor Revenue, EBITDA and Debt. Complete public research and classification must not leak into restricted target routing or scoring.


## Valuation reference

Sector-specific valuation caveat: [Aswath Damodaran, Valuing Financial Service Firms](https://pages.stern.nyu.edu/~adamodar/pdfiles/papers/finfirm09.pdf). This supports treating financial firms separately; it does not validate the analyst-proposed similarity weights above.

## Industry field weights — all 83 SIC2 modules / 546 fields

These are **analyst-proposed starting weights**, not fitted coefficients and not the weights behind historical website scores. Every dictionary field is listed, including diagnostic and reference-only rows. Zero means excluded from matching under this proposed protocol; it does not mean the facet is unimportant for financial research.

**How to read each table:** `Base %` sums to 100 within a module's scored base fields. Conditional subtype extensions show 0 in the base reference; that is an inactive template setting, not a missing-data judgment. For a known applicable subtype, activate its nonzero **points**, deactivate genuinely inapplicable subtype fields with an evidenced reason, and normalize the activated points to 100 before comparing candidates. Unknown evidence must never be used to deactivate a field. Freeze the target scope/activation/duplicate exclusions once for all its candidates. If applicability is unresolved, do not publish a definitive new-standard score.

**Do not double-count general facets:** if one claim supplies the same economic dimension to both blocks, exclude the duplicate dimension at target-policy level and renormalize the remaining applicable weights. Menus, customer size, delivery channels, regulatory exposure and revenue models are especially prone to duplication.

For SIC 73, software, staffing, advertising and building-service extensions must not all be activated for a single-line SaaS business. For a diversified company, use separate segment policies and source-supported aggregation, not every subtype in one bucket. Shared company/brand wording remains labelled as shared; it is not an independently reported segment observation.

**Concrete example:** SIC 58 base reference = restaurant format 25%, franchise/company-operated role 35%, menu focus 25%, ordering/delivery mix 15%; same-store sales, traffic/check, AUV, unit counts and store-level margin are diagnostic in this restricted-input matching policy. With a 40% industry block, a nonduplicated 35%-within-block franchise field contributes at most 14 percentage points to the total. Menu/channel duplicates must first be removed if already scored in general facets.

**Judgment:** product/use case and operating/revenue role receive the largest starting importance because sharing a broad SIC code is insufficient. Financial performance, market valuation and unsupported operating quantities do not establish a match and can violate the pseudo-private information boundary. Specialist industries may need a documented policy override before scoring, not a change made after seeing candidate results.

Quick links: [Restaurants — SIC 58](#sic-58) · [Business/software services — SIC 73](#sic-73) · [Real estate — SIC 65](#sic-65) · [Banking — SIC 60](#sic-60) · [Insurance — SIC 63](#sic-63).

<a id="sic-01"></a>

### SIC 01 — Agricultural Production — Crops

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I01-01 | Crop / cultivation category | 4 | 25.00 | Base; confirm target scope and deduplication |
| I01-02 | Land area by use and tenure | 2 | 12.50 | Base; confirm target scope and deduplication |
| I01-03 | Crop-specific yield | 0 | 0.00 | Diagnostic only |
| I01-04 | Crop calendar | 2 | 12.50 | Base; confirm target scope and deduplication |
| I01-05 | Irrigation system / water dependence | 2 | 12.50 | Base; confirm target scope and deduplication |
| I01-06 | Crop price realization / hedging | 2 | 12.50 | Base; confirm target scope and deduplication |
| I01-07 | Harvest frequency | 2 | 12.50 | Base; confirm target scope and deduplication |
| I01-08 | Land / water constraints | 2 | 12.50 | Base; confirm target scope and deduplication |

<a id="sic-02"></a>

### SIC 02 — Agricultural Production — Livestock and Animal Specialties

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I02-01 | Animal / production category | 4 | 18.18 | Base; confirm target scope and deduplication |
| I02-02 | Animal inventory / output scale | 0 | 0.00 | Diagnostic only |
| I02-03 | Production / finishing cycle | 4 | 18.18 | Base; confirm target scope and deduplication |
| I02-04 | Feed ration / input exposure | 5 | 22.73 | Base; confirm target scope and deduplication |
| I02-05 | Breeding / grower arrangement | 2 | 9.09 | Base; confirm target scope and deduplication |
| I02-06 | Processing integration | 5 | 22.73 | Base; confirm target scope and deduplication |
| I02-07 | Biosecurity / animal health | 2 | 9.09 | Base; confirm target scope and deduplication |
| I02-08 | Aquaculture system [0273] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I02-09 | Aquaculture operating drivers [0273] | 2 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-07"></a>

### SIC 07 — Agricultural Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I07-01 | Agricultural / animal service specialty | 4 | 20.00 | Base; confirm target scope and deduplication |
| I07-02 | Service equipment / crew model | 5 | 25.00 | Base; confirm target scope and deduplication |
| I07-03 | Seasonal workload | 2 | 10.00 | Base; confirm target scope and deduplication |
| I07-04 | Service charging / contract basis | 5 | 25.00 | Base; confirm target scope and deduplication |
| I07-05 | Customer operating scale | 4 | 20.00 | Base; confirm target scope and deduplication |

<a id="sic-08"></a>

### SIC 08 — Forestry

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I08-01 | Tree / forest-product species | 4 | 22.22 | Base; confirm target scope and deduplication |
| I08-02 | Timberland ownership / management role | 5 | 27.78 | Base; confirm target scope and deduplication |
| I08-03 | Silvicultural / rotation cycle | 2 | 11.11 | Base; confirm target scope and deduplication |
| I08-04 | Timberland area | 2 | 11.11 | Base; confirm target scope and deduplication |
| I08-05 | Regeneration / forest stewardship | 2 | 11.11 | Base; confirm target scope and deduplication |
| I08-06 | Forest health / climate exposure | 3 | 16.67 | Base; confirm target scope and deduplication |

<a id="sic-09"></a>

### SIC 09 — Fishing, Hunting & Trapping

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I09-01 | Species / aquatic-resource focus | 4 | 21.05 | Base; confirm target scope and deduplication |
| I09-02 | Capture / harvest method | 2 | 10.53 | Base; confirm target scope and deduplication |
| I09-03 | Fishing rights / quota basis | 2 | 10.53 | Base; confirm target scope and deduplication |
| I09-04 | Capture / hatchery / managed-resource model | 5 | 26.32 | Base; confirm target scope and deduplication |
| I09-05 | Fishing fleet / effort scale | 2 | 10.53 | Base; confirm target scope and deduplication |
| I09-06 | Catch handling / landing route | 2 | 10.53 | Base; confirm target scope and deduplication |
| I09-07 | Hunting / trapping permissions | 2 | 10.51 | Base; confirm target scope and deduplication |
| I09-08 | Hatchery / preserve operating drivers [0921] | 2 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-10"></a>

### SIC 10 — Metal Mining

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I10-01 | Metal / commodity mix | 2 | 14.29 | Base; confirm target scope and deduplication |
| I10-02 | Reserve / resource classification | 3 | 21.43 | Base; confirm target scope and deduplication |
| I10-03 | Ore grade by commodity | 0 | 0.00 | Diagnostic only |
| I10-04 | Remaining mine life | 2 | 14.29 | Base; confirm target scope and deduplication |
| I10-05 | Mining method / mine stage | 2 | 14.29 | Base; confirm target scope and deduplication |
| I10-06 | Metallurgical recovery | 0 | 0.00 | Diagnostic only |
| I10-07 | Ore-processing capacity | 3 | 21.43 | Base; confirm target scope and deduplication |
| I10-08 | Mining cost / reporting basis | 2 | 14.27 | Base; confirm target scope and deduplication |

<a id="sic-12"></a>

### SIC 12 — Coal Mining

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I12-01 | Coal quality | 2 | 18.18 | Base; confirm target scope and deduplication |
| I12-02 | Mining method | 2 | 18.18 | Base; confirm target scope and deduplication |
| I12-03 | Reserve-supported life | 2 | 18.18 | Base; confirm target scope and deduplication |
| I12-04 | Thermal / metallurgical exposure | 3 | 27.27 | Base; confirm target scope and deduplication |
| I12-05 | Transport / export access | 2 | 18.19 | Base; confirm target scope and deduplication |
| I12-06 | Product specification / wash yield | 0 | 0.00 | Diagnostic only |

<a id="sic-13"></a>

### SIC 13 — Oil & Gas Extraction

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I13-01 | Operating activity | 2 | 100.00 | Base; confirm target scope and deduplication |
| I13-02 | Production mix [E&P] | 4 | 0.00 | Conditional subtype; confirm applicability |
| I13-03 | Basin / field exposure [E&P] | 3 | 0.00 | Conditional subtype; confirm applicability |
| I13-04 | Reserve measure / life [E&P] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I13-05 | Well / field decline [E&P] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I13-06 | Development intensity [E&P] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I13-07 | Production cost / price basis [E&P] | 4 | 0.00 | Conditional subtype; confirm applicability |
| I13-08 | Service line / fleet [oilfield services] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I13-09 | Contract / utilization [oilfield services] | 0 | 0.00 | Diagnostic only |

<a id="sic-14"></a>

### SIC 14 — Nonmetallic Minerals, Except Fuels

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I14-01 | Mineral / product | 4 | 22.22 | Base; confirm target scope and deduplication |
| I14-02 | Extraction route | 2 | 11.11 | Base; confirm target scope and deduplication |
| I14-03 | Reserves / remaining life | 2 | 11.11 | Base; confirm target scope and deduplication |
| I14-04 | Beneficiation / processing | 3 | 16.67 | Base; confirm target scope and deduplication |
| I14-05 | Delivery radius / logistics | 3 | 16.67 | Base; confirm target scope and deduplication |
| I14-06 | Product specification / permits | 4 | 22.22 | Base; confirm target scope and deduplication |

<a id="sic-15"></a>

### SIC 15 — Building Construction Contractors and Operative Builders

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I15-01 | Building-market mix | 3 | 14.29 | Base; confirm target scope and deduplication |
| I15-02 | Project / building type | 4 | 19.05 | Base; confirm target scope and deduplication |
| I15-03 | Contracted backlog | 3 | 14.29 | Base; confirm target scope and deduplication |
| I15-04 | Contract pricing / risk | 3 | 14.29 | Base; confirm target scope and deduplication |
| I15-05 | Self-perform / subcontract scope | 3 | 14.29 | Base; confirm target scope and deduplication |
| I15-06 | Builder / contractor role | 5 | 23.79 | Base; confirm target scope and deduplication |
| I15-07 | Land / inventory exposure [operative builders] | 3 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-16"></a>

### SIC 16 — Heavy Construction

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I16-01 | Infrastructure project type | 4 | 16.67 | Base; confirm target scope and deduplication |
| I16-02 | Public / private client mix | 4 | 16.67 | Base; confirm target scope and deduplication |
| I16-03 | Contracted backlog | 3 | 12.50 | Base; confirm target scope and deduplication |
| I16-04 | Heavy-equipment model | 5 | 20.83 | Base; confirm target scope and deduplication |
| I16-05 | Project delivery duration | 3 | 12.50 | Base; confirm target scope and deduplication |
| I16-06 | Fixed-price / cost-overrun exposure | 3 | 12.50 | Base; confirm target scope and deduplication |
| I16-07 | Concession / operating commitments | 2 | 8.33 | Base; confirm target scope and deduplication |

<a id="sic-17"></a>

### SIC 17 — Special Trade Contractors

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I17-01 | Specialist trade | 4 | 30.77 | Base; confirm target scope and deduplication |
| I17-02 | New-build / service mix | 2 | 15.38 | Base; confirm target scope and deduplication |
| I17-03 | Trade licenses / workforce qualification | 2 | 15.38 | Base; confirm target scope and deduplication |
| I17-04 | Typical contract / job size | 3 | 23.08 | Base; confirm target scope and deduplication |
| I17-05 | Maintenance / emergency recurrence | 2 | 15.39 | Base; confirm target scope and deduplication |

<a id="sic-20"></a>

### SIC 20 — Food & Kindred Products

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I20-01 | Food / beverage category | 4 | 19.05 | Base; confirm target scope and deduplication |
| I20-02 | Brand / private-label manufacturing | 3 | 14.29 | Base; confirm target scope and deduplication |
| I20-03 | Shelf life / storage condition | 2 | 9.52 | Base; confirm target scope and deduplication |
| I20-04 | Processing technology | 3 | 14.29 | Base; confirm target scope and deduplication |
| I20-05 | Temperature-controlled logistics | 2 | 9.52 | Base; confirm target scope and deduplication |
| I20-06 | Customer-channel sales mix | 4 | 19.05 | Base; confirm target scope and deduplication |
| I20-07 | Input / food-safety exposure | 3 | 14.28 | Base; confirm target scope and deduplication |

<a id="sic-21"></a>

### SIC 21 — Tobacco Products

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I21-01 | Tobacco product / manufacturing role | 5 | 27.78 | Base; confirm target scope and deduplication |
| I21-02 | Excise-tax / jurisdiction exposure | 3 | 16.67 | Base; confirm target scope and deduplication |
| I21-03 | Tobacco / nicotine format | 4 | 22.22 | Base; confirm target scope and deduplication |
| I21-04 | Distribution restrictions | 2 | 11.11 | Base; confirm target scope and deduplication |
| I21-05 | Marketing authorization / product status | 4 | 22.22 | Base; confirm target scope and deduplication |

<a id="sic-22"></a>

### SIC 22 — Textile Mill Products

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I22-01 | Fiber composition | 2 | 15.38 | Base; confirm target scope and deduplication |
| I22-02 | Fabric construction | 2 | 15.38 | Base; confirm target scope and deduplication |
| I22-03 | Textile production stages | 4 | 30.77 | Base; confirm target scope and deduplication |
| I22-04 | Mill output capacity | 0 | 0.00 | Diagnostic only |
| I22-05 | Fiber / chemical input exposure | 3 | 23.08 | Base; confirm target scope and deduplication |
| I22-06 | Textile end use | 2 | 15.39 | Base; confirm target scope and deduplication |

<a id="sic-23"></a>

### SIC 23 — Apparel & Finished Textile Products

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I23-01 | Apparel / sewn-product category | 4 | 25.00 | Base; confirm target scope and deduplication |
| I23-02 | Design / fashion cadence | 2 | 12.50 | Base; confirm target scope and deduplication |
| I23-03 | Manufacturing arrangement | 3 | 18.75 | Base; confirm target scope and deduplication |
| I23-04 | Inventory / order seasonality | 2 | 12.50 | Base; confirm target scope and deduplication |
| I23-05 | Brand / contract-production role | 5 | 31.25 | Base; confirm target scope and deduplication |

<a id="sic-24"></a>

### SIC 24 — Lumber and Wood Products, Except Furniture

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I24-01 | Wood species / log input | 4 | 22.22 | Base; confirm target scope and deduplication |
| I24-02 | Product grade / specification | 0 | 0.00 | Diagnostic only |
| I24-03 | Wood-processing activity | 3 | 16.67 | Base; confirm target scope and deduplication |
| I24-04 | Log / timber-supply integration | 5 | 27.78 | Base; confirm target scope and deduplication |
| I24-05 | Construction-demand exposure | 3 | 16.67 | Base; confirm target scope and deduplication |
| I24-06 | Mill / log-processing capacity | 3 | 16.66 | Base; confirm target scope and deduplication |

<a id="sic-25"></a>

### SIC 25 — Furniture & Fixtures

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I25-01 | Furniture market | 3 | 18.75 | Base; confirm target scope and deduplication |
| I25-02 | Furniture / fixture type | 4 | 25.00 | Base; confirm target scope and deduplication |
| I25-03 | Production / customization model | 5 | 31.25 | Base; confirm target scope and deduplication |
| I25-04 | Primary materials | 2 | 12.50 | Base; confirm target scope and deduplication |
| I25-05 | Design / specification differentiation | 2 | 12.50 | Base; confirm target scope and deduplication |

<a id="sic-26"></a>

### SIC 26 — Paper & Allied Products

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I26-01 | Paper / converted-product grade | 0 | 0.00 | Diagnostic only |
| I26-02 | Packaging / tissue / publication mix | 2 | 15.38 | Base; confirm target scope and deduplication |
| I26-03 | Pulp / converting integration | 5 | 38.46 | Base; confirm target scope and deduplication |
| I26-04 | Fiber furnish | 2 | 15.38 | Base; confirm target scope and deduplication |
| I26-05 | Mill / converting capacity | 2 | 15.38 | Base; confirm target scope and deduplication |
| I26-06 | Energy / water requirements | 2 | 15.40 | Base; confirm target scope and deduplication |

<a id="sic-27"></a>

### SIC 27 — Printing, Publishing and Allied Industries

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I27-01 | Printing / publishing activity | 2 | 40.00 | Base; confirm target scope and deduplication |
| I27-02 | Print / digital revenue mix [publishers] | 5 | 0.00 | Conditional subtype; confirm applicability |
| I27-03 | Publication / print market | 3 | 60.00 | Base; confirm target scope and deduplication |
| I27-04 | Advertising / circulation dependence [publishers] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I27-05 | Print output / format [printers] | 0 | 0.00 | Diagnostic only |
| I27-06 | Paid circulation [periodicals] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I27-07 | Rights / distribution [publishers] | 2 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-28"></a>

### SIC 28 — Chemicals & Allied Products

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I28-01 | Chemical / life-science product family | 4 | 22.22 | Base; confirm target scope and deduplication |
| I28-02 | Specialty / commodity positioning | 4 | 22.22 | Base; confirm target scope and deduplication |
| I28-03 | Formulation / synthesis complexity | 2 | 11.11 | Base; confirm target scope and deduplication |
| I28-04 | Patent / exclusivity dependence | 2 | 11.11 | Base; confirm target scope and deduplication |
| I28-05 | Product-specific regulatory route | 4 | 22.22 | Base; confirm target scope and deduplication |
| I28-06 | R&D intensity | 2 | 11.12 | Base; confirm target scope and deduplication |
| I28-07 | Clinical / commercialization stage [pharma] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I28-08 | Biologic / small-molecule platform [pharma] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I28-09 | Manufacturing / supply model [pharma] | 5 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-29"></a>

### SIC 29 — Petroleum Refining and Related Industries

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I29-01 | Refining / related activity | 2 | 22.22 | Base; confirm target scope and deduplication |
| I29-02 | Crude-processing capacity [refineries] | 3 | 0.00 | Conditional subtype; confirm applicability |
| I29-03 | Product yield mix | 0 | 0.00 | Diagnostic only |
| I29-04 | Feedstock specification | 5 | 55.56 | Base; confirm target scope and deduplication |
| I29-05 | Margin / crack-spread exposure | 0 | 0.00 | Diagnostic only |
| I29-06 | Conversion / refinery complexity | 2 | 22.22 | Base; confirm target scope and deduplication |
| I29-07 | Throughput / utilization [refineries] | 0 | 0.00 | Diagnostic only |

<a id="sic-30"></a>

### SIC 30 — Rubber & Miscellaneous Plastics

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I30-01 | Polymer / rubber family | 2 | 12.50 | Base; confirm target scope and deduplication |
| I30-02 | Forming / fabrication process | 3 | 18.75 | Base; confirm target scope and deduplication |
| I30-03 | Component specialization | 4 | 25.00 | Base; confirm target scope and deduplication |
| I30-04 | Mold / tooling requirements | 2 | 12.50 | Base; confirm target scope and deduplication |
| I30-05 | Feedstock / input-price exposure | 5 | 31.25 | Base; confirm target scope and deduplication |

<a id="sic-31"></a>

### SIC 31 — Leather & Leather Products

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I31-01 | Leather / material type | 4 | 21.05 | Base; confirm target scope and deduplication |
| I31-02 | Leather-product category | 4 | 21.05 | Base; confirm target scope and deduplication |
| I31-03 | Tanning / fabrication activity | 2 | 10.53 | Base; confirm target scope and deduplication |
| I31-04 | Material / production sourcing | 4 | 21.05 | Base; confirm target scope and deduplication |
| I31-05 | Brand / manufacturing role | 5 | 26.32 | Base; confirm target scope and deduplication |

<a id="sic-32"></a>

### SIC 32 — Stone, Clay, Glass & Concrete

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I32-01 | Mineral-based product | 4 | 20.00 | Base; confirm target scope and deduplication |
| I32-02 | Thermal-processing dependence | 3 | 15.00 | Base; confirm target scope and deduplication |
| I32-03 | Energy / fuel intensity | 2 | 10.00 | Base; confirm target scope and deduplication |
| I32-04 | Delivery radius / product logistics | 4 | 20.00 | Base; confirm target scope and deduplication |
| I32-05 | Construction end use | 2 | 10.00 | Base; confirm target scope and deduplication |
| I32-06 | Raw-material / integration model | 5 | 25.00 | Base; confirm target scope and deduplication |

<a id="sic-33"></a>

### SIC 33 — Primary Metal Industries

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I33-01 | Metal / alloy family | 2 | 12.50 | Base; confirm target scope and deduplication |
| I33-02 | Primary / secondary processing | 3 | 18.75 | Base; confirm target scope and deduplication |
| I33-03 | Annual production capacity | 4 | 25.00 | Base; confirm target scope and deduplication |
| I33-04 | Raw-material / scrap mix | 2 | 12.50 | Base; confirm target scope and deduplication |
| I33-05 | Process-energy requirement | 3 | 18.75 | Base; confirm target scope and deduplication |
| I33-06 | Metal pricing / realization basis | 2 | 12.50 | Base; confirm target scope and deduplication |

<a id="sic-34"></a>

### SIC 34 — Fabricated Metal Products

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I34-01 | Metal-fabrication process | 3 | 23.08 | Base; confirm target scope and deduplication |
| I34-02 | Precision / tolerance requirement | 2 | 15.38 | Base; confirm target scope and deduplication |
| I34-03 | Custom / standardized component mix | 2 | 15.38 | Base; confirm target scope and deduplication |
| I34-04 | Tooling / equipment capability | 2 | 15.38 | Base; confirm target scope and deduplication |
| I34-05 | End-market qualifications | 4 | 30.78 | Base; confirm target scope and deduplication |

<a id="sic-35"></a>

### SIC 35 — Industrial and Commercial Machinery and Computer Equipment

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I35-01 | Machinery / computer-equipment category | 4 | 26.67 | Base; confirm target scope and deduplication |
| I35-02 | Installed equipment base | 2 | 13.33 | Base; confirm target scope and deduplication |
| I35-03 | Aftermarket sales mix | 3 | 20.00 | Base; confirm target scope and deduplication |
| I35-04 | Equipment replacement cycle | 2 | 13.33 | Base; confirm target scope and deduplication |
| I35-05 | Engineering / customization | 2 | 13.33 | Base; confirm target scope and deduplication |
| I35-06 | Service / maintenance requirement | 2 | 13.34 | Base; confirm target scope and deduplication |

<a id="sic-36"></a>

### SIC 36 — Electronic and Electrical Equipment, Except Computer Equipment

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I36-01 | Electrical / electronic product family | 4 | 22.22 | Base; confirm target scope and deduplication |
| I36-02 | Operating model | 5 | 27.78 | Base; confirm target scope and deduplication |
| I36-03 | Design / fabrication / assembly split | 2 | 11.11 | Base; confirm target scope and deduplication |
| I36-04 | Product / design-in lifecycle | 4 | 22.22 | Base; confirm target scope and deduplication |
| I36-05 | OEM / design-win exposure | 3 | 16.67 | Base; confirm target scope and deduplication |
| I36-06 | Process / technology capability [semiconductors] | 3 | 0.00 | Conditional subtype; confirm applicability |
| I36-07 | Manufacturing / supply capacity [semiconductors] | 3 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-37"></a>

### SIC 37 — Transportation Equipment

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I37-01 | Transport-equipment activity | 2 | 11.11 | Base; confirm target scope and deduplication |
| I37-02 | OEM / supplier role | 5 | 27.78 | Base; confirm target scope and deduplication |
| I37-03 | Platform / program concentration | 2 | 11.11 | Base; confirm target scope and deduplication |
| I37-04 | Product / production qualification | 4 | 22.22 | Base; confirm target scope and deduplication |
| I37-05 | Program backlog | 2 | 11.11 | Base; confirm target scope and deduplication |
| I37-06 | Aftermarket / original-equipment mix | 3 | 16.67 | Base; confirm target scope and deduplication |

<a id="sic-38"></a>

### SIC 38 — Measuring, Medical, Optical and Related Instruments

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I38-01 | Instrument / device family | 2 | 14.29 | Base; confirm target scope and deduplication |
| I38-02 | Measurement / performance specification | 2 | 14.29 | Base; confirm target scope and deduplication |
| I38-03 | Clinical / industrial / research use | 2 | 14.29 | Base; confirm target scope and deduplication |
| I38-04 | Product-specific regulatory status | 4 | 28.57 | Base; confirm target scope and deduplication |
| I38-05 | Consumables / service attachment | 2 | 14.29 | Base; confirm target scope and deduplication |
| I38-06 | Calibration / qualification requirement | 2 | 14.27 | Base; confirm target scope and deduplication |

<a id="sic-39"></a>

### SIC 39 — Miscellaneous Manufacturing

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I39-01 | Manufactured-product niche | 4 | 17.39 | Base; confirm target scope and deduplication |
| I39-02 | Production process | 4 | 17.39 | Base; confirm target scope and deduplication |
| I39-03 | Customization / batch model | 5 | 21.74 | Base; confirm target scope and deduplication |
| I39-04 | Brand / licensing economics | 2 | 8.70 | Base; confirm target scope and deduplication |
| I39-05 | Operating production scale | 4 | 17.39 | Base; confirm target scope and deduplication |
| I39-06 | Product / demand cycle | 4 | 17.39 | Base; confirm target scope and deduplication |

<a id="sic-40"></a>

### SIC 40 — Railroad Transportation

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I40-01 | Rail service | 2 | 20.00 | Base; confirm target scope and deduplication |
| I40-02 | Network reach / route measure | 2 | 20.00 | Base; confirm target scope and deduplication |
| I40-03 | Track / infrastructure control | 2 | 20.00 | Base; confirm target scope and deduplication |
| I40-04 | Fleet / carrying capacity | 2 | 20.00 | Base; confirm target scope and deduplication |
| I40-05 | Freight commodity mix | 2 | 20.00 | Base; confirm target scope and deduplication |
| I40-06 | Operating ratio | 0 | 0.00 | Diagnostic only |
| I40-07 | Service / network productivity | 0 | 0.00 | Diagnostic only |

<a id="sic-41"></a>

### SIC 41 — Local, Suburban and Interurban Passenger Transportation

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I41-01 | Passenger transport mode | 2 | 15.38 | Base; confirm target scope and deduplication |
| I41-02 | Operating fleet | 2 | 15.38 | Base; confirm target scope and deduplication |
| I41-03 | Route / service density | 2 | 15.38 | Base; confirm target scope and deduplication |
| I41-04 | Fare / payment structure | 2 | 15.38 | Base; confirm target scope and deduplication |
| I41-05 | Public-service contract model | 5 | 38.48 | Base; confirm target scope and deduplication |
| I41-06 | Passenger utilization | 0 | 0.00 | Diagnostic only |

<a id="sic-42"></a>

### SIC 42 — Motor Freight Transportation and Warehousing

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I42-01 | Freight / storage service | 2 | 9.09 | Base; confirm target scope and deduplication |
| I42-02 | Transport asset model | 5 | 22.73 | Base; confirm target scope and deduplication |
| I42-03 | Warehouse footprint / capacity | 2 | 9.09 | Base; confirm target scope and deduplication |
| I42-04 | Freight specialization | 4 | 18.18 | Base; confirm target scope and deduplication |
| I42-05 | Network / lane structure | 2 | 9.09 | Base; confirm target scope and deduplication |
| I42-06 | Asset-based / intermediary role | 5 | 22.73 | Base; confirm target scope and deduplication |
| I42-07 | Freight operating drivers | 2 | 9.09 | Base; confirm target scope and deduplication |

<a id="sic-43"></a>

### SIC 43 — U.S. Postal Service

Reference/classification only; no public-comp scoring weights assigned.

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I43-01 | Postal service / product mix | 0 | 0.00 | Reference only |
| I43-02 | Postal network | 0 | 0.00 | Reference only |
| I43-03 | Delivery coverage / density | 0 | 0.00 | Reference only |
| I43-04 | Delivered item volume | 0 | 0.00 | Reference only |
| I43-05 | Universal-service mandate | 0 | 0.00 | Reference only |

<a id="sic-44"></a>

### SIC 44 — Water Transportation

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I44-01 | Vessel / marine service | 2 | 13.33 | Base; confirm target scope and deduplication |
| I44-02 | Fleet carrying capacity | 2 | 13.33 | Base; confirm target scope and deduplication |
| I44-03 | Trade / shipping lanes | 2 | 13.33 | Base; confirm target scope and deduplication |
| I44-04 | Charter / deployment arrangement | 2 | 13.33 | Base; confirm target scope and deduplication |
| I44-05 | Freight pricing / spot exposure | 3 | 20.00 | Base; confirm target scope and deduplication |
| I44-06 | Port / terminal access | 2 | 13.33 | Base; confirm target scope and deduplication |
| I44-07 | Fleet renewal / specification | 2 | 13.35 | Base; confirm target scope and deduplication |

<a id="sic-45"></a>

### SIC 45 — Air Transportation

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I45-01 | Air service | 2 | 12.50 | Base; confirm target scope and deduplication |
| I45-02 | Route / network model | 5 | 31.25 | Base; confirm target scope and deduplication |
| I45-03 | Fleet / aircraft mix | 2 | 12.50 | Base; confirm target scope and deduplication |
| I45-04 | Load factor by service | 2 | 12.50 | Base; confirm target scope and deduplication |
| I45-05 | Yield / unit revenue | 0 | 0.00 | Diagnostic only |
| I45-06 | Fuel / fleet-cost exposure | 3 | 18.75 | Base; confirm target scope and deduplication |
| I45-07 | Service / traffic mix | 2 | 12.50 | Base; confirm target scope and deduplication |

<a id="sic-46"></a>

### SIC 46 — Pipelines, Except Natural Gas

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I46-01 | Pipeline commodity | 2 | 14.29 | Base; confirm target scope and deduplication |
| I46-02 | Pipeline network length | 2 | 14.29 | Base; confirm target scope and deduplication |
| I46-03 | Throughput capacity | 0 | 0.00 | Diagnostic only |
| I46-04 | Tariff / fee structure | 5 | 35.71 | Base; confirm target scope and deduplication |
| I46-05 | Committed contract coverage | 3 | 21.43 | Base; confirm target scope and deduplication |
| I46-06 | Network connectivity | 2 | 14.28 | Base; confirm target scope and deduplication |

<a id="sic-47"></a>

### SIC 47 — Transportation Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I47-01 | Transport-intermediary service | 2 | 10.00 | Base; confirm target scope and deduplication |
| I47-02 | Transport / booking specialization | 4 | 20.00 | Base; confirm target scope and deduplication |
| I47-03 | Asset ownership / control | 5 | 25.00 | Base; confirm target scope and deduplication |
| I47-04 | Activity-volume unit | 2 | 10.00 | Base; confirm target scope and deduplication |
| I47-05 | Customs / border responsibilities | 2 | 10.00 | Base; confirm target scope and deduplication |
| I47-06 | Gross / net revenue presentation | 5 | 25.00 | Base; confirm target scope and deduplication |

<a id="sic-48"></a>

### SIC 48 — Communications

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I48-01 | Communications activity | 2 | 18.18 | Base; confirm target scope and deduplication |
| I48-02 | Network / distribution assets | 3 | 27.27 | Base; confirm target scope and deduplication |
| I48-03 | Subscriber / audience measure | 2 | 18.18 | Base; confirm target scope and deduplication |
| I48-04 | License / spectrum rights | 2 | 18.18 | Base; confirm target scope and deduplication |
| I48-05 | ARPU / ARPA [subscription telecom] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I48-06 | Customer churn [subscription telecom] | 0 | 0.00 | Diagnostic only |
| I48-07 | Coverage / distribution reach | 2 | 18.19 | Base; confirm target scope and deduplication |
| I48-08 | Advertising / carriage economics [broadcasting] | 2 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-49"></a>

### SIC 49 — Electric, Gas & Sanitary Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I49-01 | Utility / environmental service | 2 | 10.00 | Base; confirm target scope and deduplication |
| I49-02 | Regulated / competitive operating model | 5 | 25.00 | Base; confirm target scope and deduplication |
| I49-03 | Generation fuel / technology mix [electric generators] | 3 | 0.00 | Conditional subtype; confirm applicability |
| I49-04 | Approved regulatory rate base [regulated utilities] | 3 | 0.00 | Conditional subtype; confirm applicability |
| I49-05 | Connections / service accounts | 2 | 10.00 | Base; confirm target scope and deduplication |
| I49-06 | Service-specific rated capacity | 2 | 10.00 | Base; confirm target scope and deduplication |
| I49-07 | Regulatory jurisdiction | 3 | 15.00 | Base; confirm target scope and deduplication |
| I49-08 | Electricity output [generators] | 0 | 0.00 | Diagnostic only |
| I49-09 | Generator capacity factor [generators] | 0 | 0.00 | Diagnostic only |
| I49-10 | System peak demand [electric networks] | 0 | 0.00 | Diagnostic only |
| I49-11 | Gas network / delivery [gas utilities] | 3 | 0.00 | Conditional subtype; confirm applicability |
| I49-12 | Water / wastewater operations | 2 | 10.00 | Base; confirm target scope and deduplication |
| I49-13 | Water-system performance | 2 | 10.00 | Base; confirm target scope and deduplication |
| I49-14 | Waste / disposal economics [sanitary services] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I49-15 | Remaining landfill airspace [landfills] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I49-16 | Waste accepted [disposal] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I49-17 | Steam / irrigation service | 2 | 10.00 | Base; confirm target scope and deduplication |

<a id="sic-50"></a>

### SIC 50 — Wholesale Trade — Durable Goods

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I50-01 | Durable-goods distribution specialty | 4 | 28.57 | Base; confirm target scope and deduplication |
| I50-02 | Distribution authorization | 2 | 14.29 | Base; confirm target scope and deduplication |
| I50-03 | Inventory turnover | 0 | 0.00 | Diagnostic only |
| I50-04 | Manufacturer / supplier relationship | 3 | 21.43 | Base; confirm target scope and deduplication |
| I50-05 | Technical / value-added services | 2 | 14.29 | Base; confirm target scope and deduplication |
| I50-06 | Aftermarket sales exposure | 3 | 21.42 | Base; confirm target scope and deduplication |

<a id="sic-51"></a>

### SIC 51 — Wholesale Trade — Nondurable Goods

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I51-01 | Nondurable-goods distribution specialty | 4 | 23.53 | Base; confirm target scope and deduplication |
| I51-02 | Shelf-life / handling exposure | 3 | 17.65 | Base; confirm target scope and deduplication |
| I51-03 | Cold-chain requirement | 2 | 11.76 | Base; confirm target scope and deduplication |
| I51-04 | Commodity / purchase-price exposure | 3 | 17.65 | Base; confirm target scope and deduplication |
| I51-05 | Delivery frequency | 3 | 17.65 | Base; confirm target scope and deduplication |
| I51-06 | Saleable shelf life | 2 | 11.76 | Base; confirm target scope and deduplication |

<a id="sic-52"></a>

### SIC 52 — Building Materials, Hardware, Garden Supply and Mobile Home Dealers

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I52-01 | Professional / DIY customer mix | 4 | 28.57 | Base; confirm target scope and deduplication |
| I52-02 | Building / garden assortment | 2 | 14.29 | Base; confirm target scope and deduplication |
| I52-03 | Retail format | 4 | 28.57 | Base; confirm target scope and deduplication |
| I52-04 | Construction / renovation demand | 2 | 14.29 | Base; confirm target scope and deduplication |
| I52-05 | Installation / project services | 2 | 14.28 | Base; confirm target scope and deduplication |

<a id="sic-53"></a>

### SIC 53 — General Merchandise Stores

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I53-01 | General-merchandise retail format | 4 | 40.00 | Base; confirm target scope and deduplication |
| I53-02 | Merchandise category mix | 4 | 40.00 | Base; confirm target scope and deduplication |
| I53-03 | Private-label sales share | 0 | 0.00 | Diagnostic only |
| I53-04 | Store sales productivity | 0 | 0.00 | Diagnostic only |
| I53-05 | Inventory turnover | 0 | 0.00 | Diagnostic only |
| I53-06 | Comparable-store sales | 2 | 20.00 | Base; confirm target scope and deduplication |

<a id="sic-54"></a>

### SIC 54 — Food Stores

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I54-01 | Food retail format | 4 | 33.33 | Base; confirm target scope and deduplication |
| I54-02 | Fresh / packaged food mix | 2 | 16.67 | Base; confirm target scope and deduplication |
| I54-03 | Private-label sales share | 0 | 0.00 | Diagnostic only |
| I54-04 | Fresh-food waste / perishability | 2 | 16.67 | Base; confirm target scope and deduplication |
| I54-05 | Store network density | 2 | 16.67 | Base; confirm target scope and deduplication |
| I54-06 | Average transaction basket | 2 | 16.66 | Base; confirm target scope and deduplication |
| I54-07 | Customer traffic / comparable growth | 0 | 0.00 | Diagnostic only |

<a id="sic-55"></a>

### SIC 55 — Automotive Dealers and Gasoline Service Stations

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I55-01 | Dealer / fuel-retail activity | 2 | 100.00 | Base; confirm target scope and deduplication |
| I55-02 | Vehicle sales mix [dealers] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I55-03 | Vehicle brand / franchise mix [dealers] | 5 | 0.00 | Conditional subtype; confirm applicability |
| I55-04 | F&I economics [dealers] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I55-05 | Parts / service economics [dealers] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I55-06 | Dealership authorization [dealers] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I55-07 | Fuel / convenience-store economics [stations] | 2 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-56"></a>

### SIC 56 — Apparel & Accessory Stores

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I56-01 | Apparel-store niche | 2 | 12.50 | Base; confirm target scope and deduplication |
| I56-02 | Fashion / assortment cadence | 2 | 12.50 | Base; confirm target scope and deduplication |
| I56-03 | Brand assortment | 2 | 12.50 | Base; confirm target scope and deduplication |
| I56-04 | Full-price / off-price mix | 2 | 12.50 | Base; confirm target scope and deduplication |
| I56-05 | Markdown / inventory exposure | 3 | 18.75 | Base; confirm target scope and deduplication |
| I56-06 | Store / online channel integration | 5 | 31.25 | Base; confirm target scope and deduplication |

<a id="sic-57"></a>

### SIC 57 — Home Furniture & Equipment Stores

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I57-01 | Home-goods retail category | 4 | 22.22 | Base; confirm target scope and deduplication |
| I57-02 | Delivery / installation proposition | 3 | 16.67 | Base; confirm target scope and deduplication |
| I57-03 | Customer-financing penetration | 4 | 22.22 | Base; confirm target scope and deduplication |
| I57-04 | Transaction size / replacement demand | 2 | 11.11 | Base; confirm target scope and deduplication |
| I57-05 | Inventory / fulfillment model | 5 | 27.78 | Base; confirm target scope and deduplication |

<a id="sic-58"></a>

### SIC 58 — Eating & Drinking Places

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I58-01 | Restaurant / drinking-place format | 25 | 25.00 | Base; confirm target scope and deduplication |
| I58-02 | Franchise / company-operated footprint | 35 | 35.00 | Base; confirm target scope and deduplication |
| I58-03 | Comparable-unit sales growth | 0 | 0.00 | Diagnostic only |
| I58-04 | Comparable traffic / average check | 0 | 0.00 | Diagnostic only |
| I58-05 | Average unit volume [defined cohort] | 0 | 0.00 | Diagnostic only |
| I58-06 | System / operated unit counts | 0 | 0.00 | Diagnostic only |
| I58-07 | Menu / beverage focus | 25 | 25.00 | Base; confirm target scope and deduplication |
| I58-08 | Ordering / delivery sales mix | 15 | 15.00 | Base; confirm target scope and deduplication |
| I58-09 | Store-level economics [company-operated] | 0 | 0.00 | Diagnostic only |

<a id="sic-59"></a>

### SIC 59 — Miscellaneous Retail

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I59-01 | Specialty retail niche | 4 | 20.00 | Base; confirm target scope and deduplication |
| I59-02 | Merchandise specialization | 4 | 20.00 | Base; confirm target scope and deduplication |
| I59-03 | Retail / selling format | 4 | 20.00 | Base; confirm target scope and deduplication |
| I59-04 | Purchase / refill cadence | 2 | 10.00 | Base; confirm target scope and deduplication |
| I59-05 | Online sales penetration | 2 | 10.00 | Base; confirm target scope and deduplication |
| I59-06 | Product-specific regulatory exposure | 4 | 20.00 | Base; confirm target scope and deduplication |

<a id="sic-60"></a>

### SIC 60 — Depository Institutions

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I60-01 | Deposit composition | 5 | 50.00 | Base; confirm target scope and deduplication |
| I60-02 | Lending composition | 5 | 50.00 | Base; confirm target scope and deduplication |
| I60-03 | Net interest margin | 0 | 0.00 | Diagnostic only |
| I60-04 | Deposit interest cost | 0 | 0.00 | Diagnostic only |
| I60-05 | Nonperforming-loan measure | 0 | 0.00 | Diagnostic only |
| I60-06 | Regulatory capital measure | 0 | 0.00 | Diagnostic only |
| I60-07 | Liquidity / deposit concentration | 0 | 0.00 | Diagnostic only |

<a id="sic-61"></a>

### SIC 61 — Nondepository Credit Institutions

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I61-01 | Credit / lending product | 5 | 29.41 | Base; confirm target scope and deduplication |
| I61-02 | Origination channel | 3 | 17.65 | Base; confirm target scope and deduplication |
| I61-03 | Funding / balance-sheet model | 5 | 29.41 | Base; confirm target scope and deduplication |
| I61-04 | Loan portfolio yield | 0 | 0.00 | Diagnostic only |
| I61-05 | Delinquency by aging bucket | 0 | 0.00 | Diagnostic only |
| I61-06 | Securitization / retained exposure | 4 | 23.53 | Base; confirm target scope and deduplication |
| I61-07 | Credit-loss measure | 0 | 0.00 | Diagnostic only |

<a id="sic-62"></a>

### SIC 62 — Security and Commodity Brokers, Dealers, Exchanges and Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I62-01 | Financial-market service | 5 | 35.71 | Base; confirm target scope and deduplication |
| I62-02 | Client / instrument exposure | 4 | 28.57 | Base; confirm target scope and deduplication |
| I62-03 | Assets under management [asset managers] | 0 | 0.00 | Diagnostic only |
| I62-04 | Assets under administration / custody [platforms] | 0 | 0.00 | Diagnostic only |
| I62-05 | Revenue / fee economics | 5 | 35.72 | Base; confirm target scope and deduplication |
| I62-06 | Client trading activity | 0 | 0.00 | Diagnostic only |

<a id="sic-63"></a>

### SIC 63 — Insurance Carriers

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I63-01 | Insurance business line | 5 | 25.00 | Base; confirm target scope and deduplication |
| I63-02 | Risk underwriting / distribution model | 5 | 25.00 | Base; confirm target scope and deduplication |
| I63-03 | Premium / exposure mix | 3 | 15.00 | Base; confirm target scope and deduplication |
| I63-04 | Combined ratio [P&C underwriting] | 0 | 0.00 | Diagnostic only |
| I63-05 | Loss / LAE ratio [P&C underwriting] | 0 | 0.00 | Diagnostic only |
| I63-06 | Medical benefit ratio [health insurers] | 0 | 0.00 | Diagnostic only |
| I63-07 | Reinsurance / catastrophe protection | 3 | 15.00 | Base; confirm target scope and deduplication |
| I63-08 | Liability duration / guarantees [life and annuity] | 4 | 0.00 | Conditional subtype; confirm applicability |
| I63-09 | Investment / liability matching | 4 | 20.00 | Base; confirm target scope and deduplication |
| I63-10 | Regime-specific solvency measure | 0 | 0.00 | Diagnostic only |

<a id="sic-64"></a>

### SIC 64 — Insurance Agents, Brokers & Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I64-01 | Insurance intermediary role | 5 | 35.71 | Base; confirm target scope and deduplication |
| I64-02 | Insurance placement niche | 2 | 14.29 | Base; confirm target scope and deduplication |
| I64-03 | Intermediary compensation | 2 | 14.29 | Base; confirm target scope and deduplication |
| I64-04 | Policy / account renewal | 2 | 14.29 | Base; confirm target scope and deduplication |
| I64-05 | Carrier / market access | 3 | 21.42 | Base; confirm target scope and deduplication |
| I64-06 | Client retention by measure | 0 | 0.00 | Diagnostic only |

<a id="sic-65"></a>

### SIC 65 — Real Estate

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I65-01 | Property / real-estate service type | 5 | 26.32 | Base; confirm target scope and deduplication |
| I65-02 | Ownership / operating role | 5 | 26.32 | Base; confirm target scope and deduplication |
| I65-03 | Occupancy by basis [owners] | 0 | 0.00 | Diagnostic only |
| I65-04 | Lease term [owners] | 3 | 0.00 | Conditional subtype; confirm applicability |
| I65-05 | Rent by property unit [owners] | 0 | 0.00 | Diagnostic only |
| I65-06 | Property market | 4 | 21.05 | Base; confirm target scope and deduplication |
| I65-07 | Property-income / fee model | 5 | 26.31 | Base; confirm target scope and deduplication |

<a id="sic-67"></a>

### SIC 67 — Holding & Other Investment Offices

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I67-01 | Holding / investment-office structure | 5 | 23.81 | Base; confirm target scope and deduplication |
| I67-02 | Investment / operating asset mix | 5 | 23.81 | Base; confirm target scope and deduplication |
| I67-03 | Control / look-through ownership | 4 | 19.05 | Base; confirm target scope and deduplication |
| I67-04 | Portfolio concentration | 3 | 14.29 | Base; confirm target scope and deduplication |
| I67-05 | Management / incentive fees [externally managed vehicles] | 3 | 0.00 | Conditional subtype; confirm applicability |
| I67-06 | NAV basis [investment vehicles] | 0 | 0.00 | Diagnostic only |
| I67-07 | Parent funding / subsidiary recourse | 4 | 19.04 | Base; confirm target scope and deduplication |
| I67-08 | Market discount [listed investment vehicles] | 0 | 0.00 | Diagnostic only |
| I67-09 | REIT business model [6798] | 5 | 0.00 | Conditional subtype; confirm applicability |
| I67-10 | Property portfolio [equity REITs] | 4 | 0.00 | Conditional subtype; confirm applicability |
| I67-11 | Property occupancy [equity REITs] | 0 | 0.00 | Diagnostic only |
| I67-12 | Same-property NOI growth [equity REITs] | 0 | 0.00 | Diagnostic only |
| I67-13 | Lease expiry [equity REITs] | 3 | 0.00 | Conditional subtype; confirm applicability |
| I67-14 | Mortgage asset mix [mortgage REITs] | 5 | 0.00 | Conditional subtype; confirm applicability |
| I67-15 | Financing / hedge model [mortgage REITs] | 4 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-70"></a>

### SIC 70 — Hotels and Other Lodging Places

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I70-01 | Lodging / operating format | 4 | 25.00 | Base; confirm target scope and deduplication |
| I70-02 | Room inventory / ownership scope | 5 | 31.25 | Base; confirm target scope and deduplication |
| I70-03 | ADR [room operators] | 0 | 0.00 | Diagnostic only |
| I70-04 | RevPAR [room operators] | 0 | 0.00 | Diagnostic only |
| I70-05 | Room occupancy [room operators] | 0 | 0.00 | Diagnostic only |
| I70-06 | Ownership / management / franchising | 5 | 31.25 | Base; confirm target scope and deduplication |
| I70-07 | Hotel demand / seasonality | 2 | 12.50 | Base; confirm target scope and deduplication |
| I70-08 | Brand fee / contract economics [asset-light operators] | 5 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-72"></a>

### SIC 72 — Personal Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I72-01 | Personal-service specialty | 4 | 28.57 | Base; confirm target scope and deduplication |
| I72-02 | Purchase / service cadence | 2 | 14.29 | Base; confirm target scope and deduplication |
| I72-03 | Outlet / catchment concentration | 2 | 14.29 | Base; confirm target scope and deduplication |
| I72-04 | Service-specific labor qualification | 2 | 14.29 | Base; confirm target scope and deduplication |
| I72-05 | Repeat-customer measure | 4 | 28.56 | Base; confirm target scope and deduplication |
| I72-06 | Appointment rebooking [appointment businesses] | 2 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-73"></a>

### SIC 73 — Business Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I73-01 | Business-service specialization | 5 | 20.83 | Base; confirm target scope and deduplication |
| I73-02 | Service operating model | 5 | 20.83 | Base; confirm target scope and deduplication |
| I73-03 | Charging unit | 3 | 12.50 | Base; confirm target scope and deduplication |
| I73-04 | Customer contract term | 3 | 12.50 | Base; confirm target scope and deduplication |
| I73-05 | Contracted / repeat revenue | 4 | 16.67 | Base; confirm target scope and deduplication |
| I73-06 | Implementation / transition work | 4 | 16.67 | Base; confirm target scope and deduplication |
| I73-07 | Client-count retention | 0 | 0.00 | Diagnostic only |
| I73-08 | Software deployment [737 software/services] | 4 | 0.00 | Conditional subtype; confirm applicability |
| I73-09 | Software functional scope [737] | 5 | 0.00 | Conditional subtype; confirm applicability |
| I73-10 | Net revenue retention [subscription software] | 0 | 0.00 | Diagnostic only |
| I73-11 | ARR / recurring-base definition [subscription software] | 0 | 0.00 | Diagnostic only |
| I73-12 | Processing / transaction platform [7374] | 4 | 0.00 | Conditional subtype; confirm applicability |
| I73-13 | Staffing / placement model [736] | 5 | 0.00 | Conditional subtype; confirm applicability |
| I73-14 | Temporary staffing activity [temporary staffing] | 0 | 0.00 | Diagnostic only |
| I73-15 | Permanent placement volume [employment agencies] | 0 | 0.00 | Diagnostic only |
| I73-16 | Temporary labor billing economics [temporary staffing] | 0 | 0.00 | Diagnostic only |
| I73-17 | Advertising / agency economics [731] | 4 | 0.00 | Conditional subtype; confirm applicability |
| I73-18 | Building / security service model [734, 7381–7382] | 4 | 0.00 | Conditional subtype; confirm applicability |
| I73-19 | Rental fleet / utilization [735] | 0 | 0.00 | Diagnostic only |

<a id="sic-75"></a>

### SIC 75 — Automotive Repair, Services & Parking

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I75-01 | Automotive-service activity | 2 | 22.22 | Base; confirm target scope and deduplication |
| I75-02 | Rental fleet [rental businesses] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I75-03 | Workshop / bay capacity [repair businesses] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I75-04 | Operating utilization by activity | 0 | 0.00 | Diagnostic only |
| I75-05 | Service / maintenance cycle | 2 | 22.22 | Base; confirm target scope and deduplication |
| I75-06 | Parking / rental revenue unit | 5 | 55.56 | Base; confirm target scope and deduplication |

<a id="sic-76"></a>

### SIC 76 — Miscellaneous Repair Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I76-01 | Repair equipment / product niche | 4 | 26.67 | Base; confirm target scope and deduplication |
| I76-02 | Repair technical scope | 2 | 13.33 | Base; confirm target scope and deduplication |
| I76-03 | Warranty / customer-pay mix | 4 | 26.67 | Base; confirm target scope and deduplication |
| I76-04 | Replacement-parts requirement | 2 | 13.33 | Base; confirm target scope and deduplication |
| I76-05 | Service-contract coverage | 3 | 20.00 | Base; confirm target scope and deduplication |

<a id="sic-78"></a>

### SIC 78 — Motion Pictures

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I78-01 | Film / video value-chain role | 5 | 35.71 | Base; confirm target scope and deduplication |
| I78-02 | Content-library rights | 2 | 14.29 | Base; confirm target scope and deduplication |
| I78-03 | Licensed-rights scope | 2 | 14.29 | Base; confirm target scope and deduplication |
| I78-04 | Revenue / release window | 5 | 35.71 | Base; confirm target scope and deduplication |
| I78-05 | Project / acquisition commitment [producers/distributors] | 2 | 0.00 | Conditional subtype; confirm applicability |
| I78-06 | Exhibition footprint [cinemas] | 2 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-79"></a>

### SIC 79 — Amusement & Recreation

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I79-01 | Recreation / entertainment activity | 2 | 25.00 | Base; confirm target scope and deduplication |
| I79-02 | Venue / service capacity | 2 | 25.00 | Base; confirm target scope and deduplication |
| I79-03 | Visits / event attendance | 2 | 25.00 | Base; confirm target scope and deduplication |
| I79-04 | Admission yield | 0 | 0.00 | Diagnostic only |
| I79-05 | Pass / membership mix | 2 | 25.00 | Base; confirm target scope and deduplication |
| I79-06 | Seasonality / utilization | 0 | 0.00 | Diagnostic only |
| I79-07 | Gaming economics [gaming businesses] | 2 | 0.00 | Conditional subtype; confirm applicability |

<a id="sic-80"></a>

### SIC 80 — Health Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I80-01 | Healthcare-provider setting | 2 | 8.33 | Base; confirm target scope and deduplication |
| I80-02 | Clinical specialty | 4 | 16.67 | Base; confirm target scope and deduplication |
| I80-03 | Patient activity / volume | 2 | 8.33 | Base; confirm target scope and deduplication |
| I80-04 | Payer revenue mix | 5 | 20.83 | Base; confirm target scope and deduplication |
| I80-05 | Payment / reimbursement model | 5 | 20.83 | Base; confirm target scope and deduplication |
| I80-06 | Setting-specific capacity | 2 | 8.33 | Base; confirm target scope and deduplication |
| I80-07 | Patient acuity / case mix | 2 | 8.33 | Base; confirm target scope and deduplication |
| I80-08 | Clinical operating quality | 2 | 8.35 | Base; confirm target scope and deduplication |

<a id="sic-81"></a>

### SIC 81 — Legal Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I81-01 | Legal practice specialty | 4 | 21.05 | Base; confirm target scope and deduplication |
| I81-02 | Matter / case mix | 2 | 10.53 | Base; confirm target scope and deduplication |
| I81-03 | Billing / realization model | 5 | 26.32 | Base; confirm target scope and deduplication |
| I81-04 | Professional leverage | 2 | 10.53 | Base; confirm target scope and deduplication |
| I81-05 | Client / engagement type | 4 | 21.05 | Base; confirm target scope and deduplication |
| I81-06 | Engagement duration | 2 | 10.52 | Base; confirm target scope and deduplication |

<a id="sic-82"></a>

### SIC 82 — Educational Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I82-01 | Education level / institution type | 4 | 18.18 | Base; confirm target scope and deduplication |
| I82-02 | Program / qualification | 2 | 9.09 | Base; confirm target scope and deduplication |
| I82-03 | Enrollment by measure | 2 | 9.09 | Base; confirm target scope and deduplication |
| I82-04 | Tuition / payment model | 5 | 22.73 | Base; confirm target scope and deduplication |
| I82-05 | Accreditation / authorization | 2 | 9.09 | Base; confirm target scope and deduplication |
| I82-06 | Completion / student outcomes | 2 | 9.09 | Base; confirm target scope and deduplication |
| I82-07 | Delivery / campus model | 5 | 22.73 | Base; confirm target scope and deduplication |

<a id="sic-83"></a>

### SIC 83 — Social Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I83-01 | Social-service program | 2 | 15.38 | Base; confirm target scope and deduplication |
| I83-02 | Beneficiary / service population | 2 | 15.38 | Base; confirm target scope and deduplication |
| I83-03 | Public / grant funding exposure | 5 | 38.46 | Base; confirm target scope and deduplication |
| I83-04 | Payment / reimbursement unit | 2 | 15.38 | Base; confirm target scope and deduplication |
| I83-05 | Program capacity / caseload | 2 | 15.40 | Base; confirm target scope and deduplication |

<a id="sic-84"></a>

### SIC 84 — Museums, Art Galleries, Botanical and Zoological Gardens

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I84-01 | Institution / attraction type | 4 | 20.00 | Base; confirm target scope and deduplication |
| I84-02 | Collection / exhibit focus | 2 | 10.00 | Base; confirm target scope and deduplication |
| I84-03 | Operating funding mix | 5 | 25.00 | Base; confirm target scope and deduplication |
| I84-04 | Visitor attendance | 2 | 10.00 | Base; confirm target scope and deduplication |
| I84-05 | Membership economics | 2 | 10.00 | Base; confirm target scope and deduplication |
| I84-06 | Endowment / restricted funding | 5 | 25.00 | Base; confirm target scope and deduplication |

<a id="sic-86"></a>

### SIC 86 — Membership Organizations

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I86-01 | Membership-organization type | 4 | 26.67 | Base; confirm target scope and deduplication |
| I86-02 | Member base / counting unit | 2 | 13.33 | Base; confirm target scope and deduplication |
| I86-03 | Dues / contribution model | 5 | 33.33 | Base; confirm target scope and deduplication |
| I86-04 | Member retention | 0 | 0.00 | Diagnostic only |
| I86-05 | Event / sponsorship income | 2 | 13.33 | Base; confirm target scope and deduplication |
| I86-06 | Representation / mission activity | 2 | 13.34 | Base; confirm target scope and deduplication |

<a id="sic-87"></a>

### SIC 87 — Engineering, Accounting, Research & Management Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I87-01 | Professional-service specialty | 4 | 20.00 | Base; confirm target scope and deduplication |
| I87-02 | Engagement / delivery model | 5 | 25.00 | Base; confirm target scope and deduplication |
| I87-03 | Billable utilization | 0 | 0.00 | Diagnostic only |
| I87-04 | Workforce / expertise mix | 2 | 10.00 | Base; confirm target scope and deduplication |
| I87-05 | Client industry / project domain | 4 | 20.00 | Base; confirm target scope and deduplication |
| I87-06 | Contracted work backlog | 3 | 15.00 | Base; confirm target scope and deduplication |
| I87-07 | Professional liability / accreditation | 2 | 10.00 | Base; confirm target scope and deduplication |

<a id="sic-88"></a>

### SIC 88 — Private Households

Reference/classification only; no public-comp scoring weights assigned.

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I88-01 | Household employment activity | 0 | 0.00 | Reference only |
| I88-02 | Employment arrangement | 0 | 0.00 | Reference only |
| I88-03 | Domestic staffing scale | 0 | 0.00 | Reference only |
| I88-04 | Service / working schedule | 0 | 0.00 | Reference only |
| I88-05 | Occupation-specific requirements | 0 | 0.00 | Reference only |

<a id="sic-89"></a>

### SIC 89 — Miscellaneous Services

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I89-01 | Miscellaneous-service specialty | 4 | 30.77 | Base; confirm target scope and deduplication |
| I89-02 | Work / delivery form | 3 | 23.08 | Base; confirm target scope and deduplication |
| I89-03 | Engagement / payment structure | 2 | 15.38 | Base; confirm target scope and deduplication |
| I89-04 | Creator / professional dependence | 2 | 15.38 | Base; confirm target scope and deduplication |
| I89-05 | Rights / professional constraints | 2 | 15.39 | Base; confirm target scope and deduplication |

<a id="sic-91"></a>

### SIC 91 — Executive, Legislative and General Government, Except Finance

Reference/classification only; no public-comp scoring weights assigned.

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I91-01 | Government level | 0 | 0.00 | Reference only |
| I91-02 | Public administrative function | 0 | 0.00 | Reference only |
| I91-03 | Budget / funding source | 0 | 0.00 | Reference only |
| I91-04 | Administrative jurisdiction | 0 | 0.00 | Reference only |

<a id="sic-92"></a>

### SIC 92 — Justice, Public Order & Safety

Reference/classification only; no public-comp scoring weights assigned.

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I92-01 | Justice / public-safety function | 0 | 0.00 | Reference only |
| I92-02 | Service jurisdiction | 0 | 0.00 | Reference only |
| I92-03 | Relevant public-service capacity | 0 | 0.00 | Reference only |
| I92-04 | Government funding | 0 | 0.00 | Reference only |

<a id="sic-93"></a>

### SIC 93 — Public Finance, Taxation & Monetary Policy

Reference/classification only; no public-comp scoring weights assigned.

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I93-01 | Public-finance / monetary function | 0 | 0.00 | Reference only |
| I93-02 | Public revenue / funding mechanism | 0 | 0.00 | Reference only |
| I93-03 | Budget / fiscal authority | 0 | 0.00 | Reference only |
| I93-04 | Monetary / fiscal responsibility | 0 | 0.00 | Reference only |

<a id="sic-94"></a>

### SIC 94 — Administration of Human Resource Programs

Reference/classification only; no public-comp scoring weights assigned.

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I94-01 | Human-resource program administration | 0 | 0.00 | Reference only |
| I94-02 | Covered population | 0 | 0.00 | Reference only |
| I94-03 | Public-program funding | 0 | 0.00 | Reference only |
| I94-04 | Eligibility / administrative mandate | 0 | 0.00 | Reference only |

<a id="sic-95"></a>

### SIC 95 — Administration of Environmental Quality and Housing Programs

Reference/classification only; no public-comp scoring weights assigned.

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I95-01 | Environmental / housing administrative function | 0 | 0.00 | Reference only |
| I95-02 | Public program / mandate | 0 | 0.00 | Reference only |
| I95-03 | Administrative jurisdiction | 0 | 0.00 | Reference only |
| I95-04 | Program funding source | 0 | 0.00 | Reference only |

<a id="sic-96"></a>

### SIC 96 — Administration of Economic Programs

Reference/classification only; no public-comp scoring weights assigned.

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I96-01 | Economic-program administration | 0 | 0.00 | Reference only |
| I96-02 | Industry / program coverage | 0 | 0.00 | Reference only |
| I96-03 | Grant / loan / permit authority | 0 | 0.00 | Reference only |
| I96-04 | Public regulatory mandate | 0 | 0.00 | Reference only |

<a id="sic-97"></a>

### SIC 97 — National Security & International Affairs

Reference/classification only; no public-comp scoring weights assigned.

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I97-01 | National-security / international function | 0 | 0.00 | Reference only |
| I97-02 | Government jurisdiction | 0 | 0.00 | Reference only |
| I97-03 | Procurement / operating responsibilities | 0 | 0.00 | Reference only |
| I97-04 | Public budget source | 0 | 0.00 | Reference only |

<a id="sic-99"></a>

### SIC 99 — Nonclassifiable Establishments

Reference/classification only; no public-comp scoring weights assigned.

| ID | Industry facet | Points | Base % | Activation / use |
|---|---|---:|---:|---|
| I99-01 | Source classification status | 0 | 0.00 | Reference only |
| I99-02 | Reason classification is unresolved | 0 | 0.00 | Reference only |
| I99-03 | Proposed industry hypothesis | 0 | 0.00 | Reference only |
| I99-04 | Classification review disposition | 0 | 0.00 | Reference only |

## Legacy industry templates — historical score provenance

The existing website pairs use these older template weights inside a 40% industry block, with target-level duplicate exclusions. The new SIC appendix above has not replaced those calculations.

### Legacy: Technology / SaaS

| Facet | Within-block weight % |
|---|---:|
| Software Category | 18 |
| Deployment Model | 5 |
| Customer Size | 14 |
| Pricing Metric | 5 |
| Revenue Composition | 8 |
| Product Architecture | 10 |
| Implementation Complexity | 10 |
| Integration Dependence | 12 |
| Customer Retention Model | 16 |
| AI Exposure | 2 |

### Legacy: Manufacturing / Industrials

| Facet | Within-block weight % |
|---|---:|
| Manufacturing Type | 12 |
| Material Type | 6 |
| Production Model | 12 |
| Product Complexity | 14 |
| Production Role | 12 |
| Automation Level | 5 |
| End-Market Exposure | 16 |
| Capacity Sensitivity | 10 |
| Supply Chain Position | 7 |
| Raw Material Exposure | 6 |

### Legacy: Financial Services

| Facet | Within-block weight % |
|---|---:|
| Financial Business Type | 18 |
| Revenue Driver | 14 |
| Customer Type | 8 |
| Balance Sheet Dependence | 14 |
| Credit Exposure | 10 |
| Asset Class Focus | 6 |
| Regulatory Regime | 10 |
| Distribution Model | 4 |
| Risk Underwriting Model | 10 |
| Funding Model | 6 |

### Legacy: Healthcare / Life Sciences

| Facet | Within-block weight % |
|---|---:|
| Healthcare Segment | 16 |
| Product Stage | 16 |
| Therapeutic Area | 12 |
| Revenue Source | 10 |
| Customer / Payer | 10 |
| Regulatory Approval | 12 |
| IP / Patent Dependence | 8 |
| Manufacturing Model | 4 |
| Reimbursement Exposure | 8 |
| R&D Intensity | 4 |

### Legacy: Consumer / Retail

| Facet | Within-block weight % |
|---|---:|
| Product Category | 18 |
| Market Position | 12 |
| Distribution Model | 18 |
| Store Footprint | 8 |
| Brand Strength | 8 |
| Purchase Frequency | 10 |
| Customer Demographics | 6 |
| Inventory Model | 8 |
| Geographic Footprint | 6 |
| Pricing Power | 6 |

### Legacy: Energy / Utilities / Materials

| Facet | Within-block weight % |
|---|---:|
| Industry Position | 14 |
| Commodity Exposure | 16 |
| Revenue Structure | 14 |
| Asset Ownership | 10 |
| Geographic Resource Exposure | 10 |
| Capital Intensity | 8 |
| Regulatory Structure | 10 |
| Reserve / Resource Profile | 6 |
| Energy Transition Exposure | 4 |
| Commodity Price Sensitivity | 8 |

### Legacy: Business / Professional Services

| Facet | Within-block weight % |
|---|---:|
| Service Category | 18 |
| Engagement Model | 14 |
| Billing Structure | 10 |
| Labor Specialization | 10 |
| Client Segment | 12 |
| Contract Duration | 10 |
| Geographic Delivery | 6 |
| Technology Enablement | 6 |
| Revenue Recurrence | 8 |
| Scalability | 6 |

### Legacy: Restaurants

| Facet | Within-block weight % |
|---|---:|
| Restaurant format | 12 |
| Franchise vs company-operated economics | 22 |
| Unit format / operating footprint | 8 |
| Menu / cuisine / customer need | 12 |
| Dayparts / occasions | 8 |
| Price point / value proposition | 8 |
| Ordering / delivery channel mix | 8 |
| Geographic operating mix | 5 |
| Purchase frequency | 5 |
| Supply chain / menu input exposure | 4 |
| Brand / loyalty dependence | 4 |
| Competitive positioning within QSR | 4 |

