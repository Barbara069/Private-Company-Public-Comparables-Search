# Similarity Scoring Standard — Proposed v3

Version: 2026-11-11. Status: proposed research protocol, not a calibrated prediction model. Historical website scores still use the legacy v2 method; they have not been recomputed under this standard or the new SIC dictionary.

## Are all companies scored the same way?

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

Proposed economic-dimension budget: product/service/application 25%; operating/revenue model 30%; customer/channel/market 15%; assets/delivery/process 20%; regulation/input/cycle exposure 10%. Allocate each dimension to the applicable SIC/segment fields before running comparisons. This budget is a design proposal: the 546-field dictionary does not yet have validated, field-level scoring weights. Do not equally weight all fields or treat all dictionary fields as applicable. Performance KPIs and facts unavailable to the pseudo-private target remain diagnostic, not matching inputs.

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
