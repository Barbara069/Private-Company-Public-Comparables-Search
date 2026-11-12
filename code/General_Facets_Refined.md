# General Facet Dictionary

**Version: 2026-11-04 · 32 facets · English**

P0 = essential business identification; P1 = important comparability refinement; P2 = supporting context; P3 = optional, judgment-sensitive context. Priorities guide extraction/review order, not similarity weights or verified importance coefficients. Within a priority, IDs provide a consistent display order. IDs remain stable when evidence or priority changes.

Extract all applicable fields for every company. Multi-select and `Other: specify` are allowed. Examples are hypothetical, not company facts. `Unknown` means missing evidence; `Not applicable` requires an evidenced reason. Financial size and concentration values need a date, scope, currency/unit and denominator. Qualitative labels require evidence or an explicit analyst-inference label.

Keep exact source text, URL/provider record, source type, document date, fact period and company/segment scope. Keep normalized interpretation separate. Cross-check entity, meaning, scope, time and measurement basis across sources before flagging a contradiction; repeated issuer text is not independent confirmation. Preserve unresolved differences.

For diversified companies, retain company-wide context and segment-level observations separately. General and industry facets may reference the same evidence, but must not receive duplicate scoring weight for the same economic fact. For pseudo-private matching, use only approved official business-website text and instructor Revenue/EBITDA/Debt; other research remains excluded. Display priority never expands matching permission.

| ID | General facet | What to extract / format | Example values | Priority |
|---|---|---|---|---|
| G01 | Primary Products | Named product categories and concrete examples; multi-select. | Payroll software; industrial pumps; hamburgers | P0 |
| G02 | Primary Services | Services sold to customers; distinguish services from internal support functions. | Payroll processing; equipment maintenance; freight forwarding | P0 |
| G03 | Core Business Activity | Precise operating verb + output; distinguish ownership, manufacturing, distribution and licensing. | Manufactures pumps; licenses software; operates restaurants | P0 |
| G04 | Customer Type | B2B / B2C / B2G / mixed; identify the paying customer separately from the end user. | B2B employers; B2C diners; B2G agencies | P0 |
| G05 | Customer Segment | Specific buyer/user populations and roles; do not substitute an industry or a customer-size claim. | HR administrators; franchise operators; hospital procurement teams | P0 |
| G06 | End Markets | Customer verticals or product applications; not the supplier’s own industry classification. | Healthcare providers; automotive production; consumer dining | P0 |
| G07 | Customer Size | SMB / mid-market / enterprise / government / consumer / mixed; retain issuer definitions. | SMB employers; large enterprises; individual consumers | P0 |
| G08 | Business Model | How operations are organized and value is delivered; distinguish from billing. | Franchisor; vertically integrated manufacturer; marketplace operator | P0 |
| G09 | Revenue Model | What customers pay for and how revenue is earned; preserve multiple streams. | Subscription fees; product sales; transaction commissions | P0 |
| G10 | Value Chain Position | Position in the supply/value chain and role relative to customers and suppliers. | Component supplier; OEM; wholesale distributor | P0 |
| G11 | Geography Served | Markets actually served; distinguish customers/operations from headquarters. | U.S. customers; Europe and Asia; domestic-only operations | P0 |
| G12 | Product Specialization | Breadth and focus of offerings, distinct from a product list or an unverified superiority claim. | Single therapeutic area; broad HCM suite; application-specific components | P1 |
| G13 | Distribution Channels | How customers are reached and sales/orders acquired. | Direct sales; independent distributors; e-commerce | P1 |
| G14 | Delivery Model | How the product/service is provided or deployed; distinguish from acquisition channel. | Cloud SaaS; on-premise installation; on-site managed service | P1 |
| G15 | Pricing Structure | Charging unit and contractual pricing mechanism; avoid securities/debt pricing. | Per employee/month; fixed project fee; cost-plus contract | P1 |
| G16 | Recurring Revenue Profile | Nature of repeat revenue; distinguish contracted recurrence from habitual repeat purchases. | Renewable subscriptions; usage-based recurring fees; repeat noncontractual purchases | P1 |
| G17 | Customer Concentration | Named large-customer dependence or disclosed concentration; include period and denominator for figures. | Largest customer: 15% of annual revenue; diversified customer base | P1 |
| G18 | Contract Duration | Customer/service/franchise contract term and renewal structure; exclude financing maturities. | Annual auto-renewal; three-year service term; month-to-month | P1 |
| G19 | Capital Intensity | Owned/leased productive assets and investment needs; distinguish issuer assets from franchisee/supplier assets. | Owned factories; leased retail sites; outsourced production | P1 |
| G20 | Regulatory Exposure | Applicable operating licenses, approvals and regulatory regimes; identify jurisdiction. | FDA device clearance; banking supervision; food-safety regulation | P1 |
| G21 | Customer Switching Costs | Cited operational, contractual or integration barriers; do not assume high costs from tenure alone. | Data migration; workflow retraining; contractual termination fees | P1 |
| G22 | Company Size Category | Supplier operating scale with dated evidence and units; not customer size or an unsupported size label. | 2,000 employees; 300 operated stores; annual revenue in stated currency | P2 |
| G23 | Labor Intensity | Dependence on labor, specialist personnel or billable capacity. | Clinician-led care; technician-intensive service; automated production | P2 |
| G24 | Revenue Cyclicality | Documented demand sensitivity, seasonality or cycle exposure; distinguish observed history from inference. | Construction-cycle demand; holiday seasonality; commodity-linked demand | P2 |
| G25 | Supply Chain Complexity | Sourcing dependencies, concentration, lead times and procurement structure. | Single-source component; global supplier network; cooperative purchasing | P2 |
| G26 | Technology Dependence | Operational reliance on technology/platforms; being in technology is not proof of a specific dependency. | Third-party cloud infrastructure; proprietary transaction platform | P2 |
| G27 | Geographic Concentration | Dependence on particular markets; distinguish from the list of countries served. | 80% of annual revenue in the U.S.; concentrated in one state | P2 |
| G28 | Product Differentiation | Specific product/service differences with evidence; label issuer marketing claims. | Patented process; industry-specific workflow; custom-engineered design | P2 |
| G29 | IP Dependence | Material dependence on patents, licenses, proprietary technology or other protected rights. | Licensed drug rights; patent-protected process; proprietary software | P2 |
| G30 | Brand Dependence | Role of brand, trademark, licensing and customer recognition; distinguish documented model from assumed brand strength. | Licensed consumer brand; branded franchise system; private-label supplier | P2 |
| G31 | Competitive Positioning | Attributable positioning/share claims with date, geography and market definition; label self-descriptions. | Issuer-described niche leader; independently measured category share | P3 |
| G32 | Company Maturity | Operating stage and relevant business history; incorporation date alone does not establish maturity. | Commercial-stage business; pre-revenue development; established operating platform | P3 |

## Refinements from the existing website

The 30 existing field keys and their source evidence are retained. Customer Type and Customer Size are new, separately defined fields; existing customer-segment passages are not automatically copied into them without semantic review. A new field remains unfilled until suitable evidence is assigned. Customer Segment captures specific buyer populations; End Markets captures verticals/applications; Company Size Category describes the supplier, not its customers. Business Model, Revenue Model, Pricing Structure and Recurring Revenue Profile represent different dimensions. Specialization, differentiation and competitive positioning must not become three scores for one marketing statement.

P3 does not mean universally unimportant: sector-specific changes can be justified in a separate scoring protocol. No historical matching scores or restricted target snapshots are changed by this dictionary/display revision.

