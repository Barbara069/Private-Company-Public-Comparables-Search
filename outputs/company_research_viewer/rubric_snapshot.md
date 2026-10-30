**Comprehensive Company Facet Framework**

1. **<!-- gdoc_comment_begin: c1 -->**Core Facets: Applicable to nearly every company, for initial comparable-company matching.<!-- gdoc_comment_end: c1 -->  
2. Sector-Specific Facets: Capture differences within manufacturing, software, financial services, healthcare, etc.

3. Growth & Risk Facets: Capture forward-looking qualitative signals that may help forecast revenue growth and valuation multiples.

## 1\. Core company facets

Priority: P0 \= essential; P1 \= important; P2 \= optional.&nbsp;

| Facet | What it captures | Example values | Priority |
| :---- | :---- | :---- | :---- |
| <!-- gdoc_comment_begin: c2 -->Primary Products<!-- gdoc_comment_end: c2 --> | Main products sold | HR software, medical devices | P0 |
| <!-- gdoc_comment_begin: c2 -->Primary Services<!-- gdoc_comment_end: c2 --> | Main services delivered | Consulting, logistics, payroll | P0 |
| <!-- gdoc_comment_begin: c3 -->Core Business Activity \*too broad<!-- gdoc_comment_end: c3 --> | What the company actually does | Develops enterprise software | P0 |
| <!-- gdoc_comment_begin: c4 -->Customer Segment<!-- gdoc_comment_end: c4 --> | Who buys its products | B2B, B2C, B2G | P0 |
| <!-- gdoc_comment_begin: c5 -->End Markets<!-- gdoc_comment_end: c5 --> | Industries served | Healthcare, retail, manufacturing | P0 |
| Business Model \*too broad&nbsp;&nbsp; | How it operates commercially | SaaS, marketplace, manufacturer | P0 |
| <!-- gdoc_comment_begin: c6 -->Revenue Model<!-- gdoc_comment_end: c6 --> | How it earns revenue | Subscription, transaction, licensing | P0 |
| <!-- gdoc_comment_begin: c7 -->Value Chain Position<!-- gdoc_comment_end: c7 --> | Role in the industry | OEM, distributor, retailer | P0 |
| <!-- gdoc_comment_begin: c8 -->Geography Served<!-- gdoc_comment_end: c8 --> | Markets of operation | US, North America, global | P0 |
| <!-- gdoc_comment_begin: c9 -->Company Size Category<!-- gdoc_comment_end: c9 --> | Operating scale | SMB, mid-market, enterprise | P1 |
| <!-- gdoc_comment_begin: c10 -->Product Specialization<!-- gdoc_comment_end: c10 --> | Breadth of offerings | Niche specialist, diversified | P1 |
| Customer Concentration | Dependence on key customers | Diversified, concentrated | P1 |
| <!-- gdoc_comment_begin: c11 -->Distribution Channels<!-- gdoc_comment_end: c11 --> | How products reach customers | Direct sales, partners, online | P1 |
| Delivery Model | How offerings are delivered | Cloud, on-premise, physical | P1 |
| Pricing Structure | How customers are charged | Per user, fixed fee, usage-based | P1 |
| Recurring Revenue Profile | Repeatability of revenue | High, medium, low | P1 |
| <!-- gdoc_comment_begin: c12 -->Capital Intensity<!-- gdoc_comment_end: c12 --> | Need for physical capital | Asset-light, asset-heavy | P1 |
| Labor Intensity | Dependence on human labor | Low, medium, high | P1 |
| <!-- gdoc_comment_begin: c13 -->Regulatory Exposure<!-- gdoc_comment_end: c13 --> | Importance of regulation | High, medium, low | P1 |
| Competitive Positioning | Main competitive advantage | Cost leader, premium specialist | P1 |
| **Product Differentiation** | Degree of differentiation | Commodity, specialized, proprietary | P1 |
| Customer Switching Costs | Difficulty of changing provider | High, medium, low | P1 |
| Revenue Cyclicality | Sensitivity to economic cycles | Defensive, cyclical | P1 |
| Company Maturity | Stage of business development | Emerging, mature, declining | P1 |
| Technology Dependence | Importance of technology | Tech-native, tech-enabled, traditional | P2 |
| Geographic Concentration | Exposure to a single region | Domestic, diversified | P2 |
| Supply Chain Complexity | Dependence on suppliers | Low, medium, high | P2 |
| Contract Duration | Typical customer contract length | Monthly, annual, multiyear | P2 |
| IP Dependence | Reliance on patents or proprietary IP | High, medium, low | P2 |
| Brand Dependence | Importance of brand reputation | High, medium, low | P2 |

Initial P0 subset: Products, Services, Core Business Activity, Customer Segment, End Markets, Business Model, Revenue Model, Value Chain Position, and Geography.&nbsp;

Company size should also be used as an initial numerical filter when reliable financial data is available.

These 9 qualitative dimensions are broad enough to cover multiple sectors without requiring hundreds of custom prompts.

## 2\. Sector-specific facets

Useful after you have identified a company's broad business category.

### Technology / SaaS

| Facet | Example values |
| :---- | :---- |
| Software Category | ERP, CRM, cybersecurity, HRTech |
| Deployment Model | SaaS, on-premise, hybrid |
| Customer Size | SMB, mid-market, enterprise |
| Pricing Metric | Per seat, usage-based, enterprise license |
| Revenue Composition | Subscription, services, licensing |
| Product Architecture | Platform, point solution, API |
| Implementation Complexity | Self-service, enterprise implementation |
| Integration Dependence | Standalone, ecosystem-integrated |
| Customer Retention Model | Mission-critical, discretionary |
| AI Exposure | AI-native, AI-enabled, limited |

### Manufacturing / Industrials

| Facet | Example values |
| :---- | :---- |
| Manufacturing Type | Discrete, process, assembly |
| Material Type | Metal, plastic, chemical, composite |
| Production Model | Make-to-order, make-to-stock |
| Product Complexity | Commodity, engineered, precision |
| Production Role | OEM, contract manufacturer, supplier |
| Automation Level | Manual, semi-automated, automated |
| End-Market Exposure | Aerospace, automotive, industrial |
| Capacity Sensitivity | High fixed-cost, flexible capacity |
| Supply Chain Position | Tier 1, Tier 2, final manufacturer |
| Raw Material Exposure | Steel, energy, semiconductors |

### Financial Services

| Facet | Example values |
| :---- | :---- |
| Financial Business Type | Banking, insurance, asset management |
| Revenue Driver | Net interest income, fees, premiums |
| Customer Type | Retail, institutional, corporate |
| Balance Sheet Dependence | Balance-sheet intensive, fee-based |
| Credit Exposure | Consumer, commercial, mortgage |
| Asset Class Focus | Equity, credit, real estate |
| Regulatory Regime | Banking, insurance, securities |
| Distribution Model | Branch, advisor, digital |
| Risk Underwriting Model | Direct lender, broker, insurer |
| Funding Model | Deposits, wholesale funding, AUM |

### Healthcare / Life Sciences

| Facet | Example values |
| :---- | :---- |
| Healthcare Segment | Pharma, biotech, medtech, services |
| Product Stage | Research, clinical, commercial |
| Therapeutic Area | Oncology, cardiovascular, neurology |
| Revenue Source | Product sales, reimbursement, licensing |
| Customer / Payer | Hospital, insurer, patient |
| Regulatory Approval | FDA-approved, clinical-stage |
| IP / Patent Dependence | High, medium, low |
| Manufacturing Model | In-house, outsourced |
| Reimbursement Exposure | Medicare, Medicaid, private insurance |
| R\&D Intensity | High, medium, low |

### Consumer / Retail

| Facet | Example values |
| :---- | :---- |
| Product Category | Apparel, food, electronics |
| Market Position | Luxury, premium, mass-market |
| Distribution Model | DTC, wholesale, franchise |
| Store Footprint | Online-only, physical, omnichannel |
| Brand Strength | Established, emerging, private label |
| Purchase Frequency | Daily, periodic, discretionary |
| Customer Demographics | Age, income, lifestyle |
| Inventory Model | Perishable, seasonal, evergreen |
| Geographic Footprint | Regional, national, global |
| Pricing Power | Low, medium, high |

### Energy / Utilities / Materials

| Facet | Example values |
| :---- | :---- |
| Industry Position | Upstream, midstream, downstream |
| Commodity Exposure | Oil, gas, copper, electricity |
| Revenue Structure | Spot, contracted, regulated |
| Asset Ownership | Asset owner, operator, service provider |
| Geographic Resource Exposure | US shale, offshore, international |
| Capital Intensity | Low, medium, high |
| Regulatory Structure | Regulated utility, merchant |
| Reserve / Resource Profile | Long-life, short-life assets |
| Energy Transition Exposure | Renewables, fossil fuels, mixed |
| Commodity Price Sensitivity | High, medium, low |

### Business / Professional Services

| Facet | Example values |
| :---- | :---- |
| Service Category | Consulting, outsourcing, staffing |
| Engagement Model | Project, retainer, managed service |
| Billing Structure | Hourly, fixed fee, outcome-based |
| Labor Specialization | Generalist, specialist |
| Client Segment | SMB, enterprise, government |
| Contract Duration | Short-term, multiyear |
| Geographic Delivery | Onshore, offshore, hybrid |
| Technology Enablement | Human-led, automated, AI-enabled |
| Revenue Recurrence | One-off, recurring |
| Scalability | Headcount-driven, platform-enabled |

## 3\. Growth and forward-looking signal facets

Relevant to the revenue forecasting component

Unlike static business characteristics, these should be time-stamped, because they can change every quarter.

| Facet | What to look for | Potential implication | Priority |
| :---- | :---- | :---- | :---- |
| Hiring Momentum | Increasing or decreasing job openings | Expansion or contraction | P0 |
| New Customer Wins | Announced client contracts | Potential revenue growth | P0 |
| Product Launches | New commercial products | New revenue opportunities | P0 |
| Geographic Expansion | New offices, regions, countries | Addressable market growth | P0 |
| Customer Churn Signals | Lost clients, contract cancellations | Revenue downside | P0 |
| Layoffs / Restructuring | Workforce reductions | Possible demand weakness or efficiency improvement | P0 |
| Strategic Partnerships | New distribution or commercial agreements | Market access | P1 |
| Pricing Changes | Price increases, discounts | Revenue and margin effects | P1 |
| Capacity Expansion | New factories, facilities | Future output capacity | P1 |
| M\&A Activity | Acquisitions, divestitures | Inorganic growth | P1 |
| Funding Events | Equity raises, new financing | Expansion capacity or liquidity needs | P1 |
| Management Guidance | Revenue outlook, qualitative forecasts | Expected growth | P1 |
| Order Backlog | Rising or falling orders | Future demand | P1 |
| Customer Demand Trends | Increased usage, bookings, traffic | Growth momentum | P1 |
| R\&D / Innovation | New patents, product development | Potential future differentiation | P2 |
| Regulatory Developments | Approvals, restrictions | Market opportunities or constraints | P2 |
| Competitive Developments | New entrants, lost market share | Competitive pressure | P2 |
| Credit Stress | Covenant issues, missed payments | Financial distress | P2 |
| Management Changes | New CEO, CFO, executives | Potential strategic change | P2 |
| Reputation / Sentiment | Customer reviews, negative publicity | Demand or retention risk | P2 |

Important: These are candidate predictive signals, not proven predictors. For example, hiring increases could indicate growth, but layoffs could also reflect automation and margin improvement. You should test whether each signal actually improves out-of-sample forecasting.

## 4\. Financial and valuation facets

| Metric | Matching or forecasting purpose |
| :---- | :---- |
| Revenue / LTM Revenue | Company scale |
| Revenue Growth (YoY) | Historical growth profile |
| EBITDA / EBITDA Margin | Profitability |
| Gross Margin | Business economics |
| Operating Margin | Operational profitability |
| Total Assets | Asset intensity |
| Debt / EBITDA | Financial leverage |
| CapEx / Revenue | Capital intensity |
| R\&D / Revenue | Innovation intensity |
| Working Capital / Revenue | Operating model |
| Recurring Revenue % | Revenue quality |
| EV / Revenue | Valuation benchmark |
| EV / EBITDA | Valuation benchmark |

&nbsp;

&nbsp;

# CapIQ, Alt Data, and Report SubTeam

Facet List

1\. Core Offering

* Allowed values: Free text, one sentence  
* Driver proxies: Baseline similarity

2\. Customer Type

* Allowed values: B2B, B2C, B2G, mixed  
* Driver proxies: Sales cost, churn, pricing power

3\.<!-- gdoc_comment_begin: c14 --> End Market

* Allowed values: Fixed list of approximately 20 sectors  
* Driver proxies: Demand drivers, cyclicality, regulation<!-- gdoc_comment_end: c14 -->

4\. Revenue Model

* Allowed values:  
  * Transactional  
  * Recurring subscription  
  * Usage  
  * Royalty or franchise  
  * Project or contract  
  * Advertising  
* Driver proxies: Revenue quality; biggest text-visible driver

5\. Value-Chain Role

* Allowed values:  
  * Maker  
  * Distributor  
  * Retailer  
  * Platform  
  * Service provider  
  * Contractor  
  * Franchisor  
* Driver proxies: Margin structure; distinguishes businesses with similar descriptions

**6\. Capital Intensity**

* **Allowed values: Asset-heavy, asset-light, mixed**  
* **Driver proxies: Depreciation share, reinvestment needs**

7\. Geography

* Allowed values: US-only, North America, global  
* Driver proxies: Risk and growth exposure

8\. Scale

* Allowed values: Small, mid, large (based on stated employees or locations)  
* Driver proxies: Size premium

The following has performed poorly on benchmarks

9\. Ownership Form

* Allowed values: Public, private, PE-backed, subsidiary, franchisor  
* Driver proxies: Explains outliers

10\. Growth Posture

* Allowed values: Expanding, stable, restructuring  
* Driver proxies: Growth&nbsp;

&nbsp;

&nbsp;

