import json,csv,re
from pathlib import Path
p=Path('outputs/wendys_segment_facets'); d=json.loads((p/'Wendys_Segment_Facets.json').read_text())
sources={s['id']:s for s in d['sources']}
for id,form,period,date in [('K25','10-K','FY2025 ended 2025-12-28','2026-02-23'),('Q26','10-Q','Q2 / six months ended 2026-06-28','2026-08-07')]:
 sources[id].update(kind='SEC '+form,date=date,period=period,filing_year=2026,document_type=form,origin='Wendy’s issuer filing hosted by SEC EDGAR')
new=[('BECOME','Wendy’s — Becoming a franchisee','https://www.wendys.com/franchising/becoming-a-franchisee','Official website','UNKNOWN — undated','Current page reviewed 2026-10-29','Franchise requirements, royalty and development support','Royalty 4–6% gross sales varies by asset type/country; development and technology support. Website applicant thresholds differ from FAQ.'),('BLOG','Wendy’s — Why become a franchisee','https://www.wendys.com/blog/wendysr-square-deal-blog/why-you-should-become-wendys-franchisee','Official company blog','UNKNOWN — publication date not verified','Historical / effective date unknown','Build-to-Suit / franchise terms','Build-to-Suit allows franchisees to lease or sublease directly from Wendy’s; historical marketing terms are not current portfolio counts.'),('CALL','Q2 2026 earnings-call transcript — Motley Fool','https://www.fool.com/earnings/call-transcripts/2026/08/14/wendys-wen-q2-2026-earnings-call-transcript/','Hosted earnings-call transcript','2026-08-14 (URL date; publication date not separately verified)','Call 2026-08-07; Q2 ended 2026-06-28','Management remarks and CFO discussion','US same-restaurant sales -7%; traffic -12.5%; average check +5.6%. Management discusses food-quality execution, value and breakfast flexibility.'),('CALL2','Q2 2026 earnings-call transcript — Investing.com','https://www.investing.com/news/transcripts/earnings-call-transcript-wendys-posts-q2-2026-beat-as-traffic-slump-deepens-93CH-4846773','Hosted earnings-call transcript','2026-08-07','Same call 2026-08-07','CFO remarks','Selected traffic/check and same-sales figures agree with the other transcript host. Same underlying call, not independent corporate evidence.'),('SUPPLY','Wendy’s — Responsible sourcing','https://www.wendys.com/csr-what-we-value/food/responsible-sourcing','Official website','UNKNOWN — undated','Current page reviewed 2026-10-29','Food sourcing and supplier standards','Supplier audits and ingredient sourcing; geographic qualifications apply. Does not establish identical sourcing in all countries.')]
for id,name,url,kind,date,period,section,text in new:
 sources[id]=dict(id=id,name=name,url=url,kind=kind,date=date,period=period,section=section,text=text,method='Read original page / transcript body; search used only for discovery',retrieved_or_reviewed_at='2026-10-29',origin='Wendy’s management; publisher-hosted transcription' if id.startswith('CALL') else 'Wendy’s issuer website',independent_confirmation=False)
d['sources']=list(sources.values())
core=[
('Primary Products','汉堡为核心的快餐食品：鸡肉三明治和鸡块、辣肉酱、薯条、烤土豆、沙拉、饮料、Frosty 冰品和儿童餐；美国和加拿大另提供早餐。产品清单是餐饮菜单，不能把物业出租或加盟服务当成食品产品。','Q26;K25','MD&A — Introduction / Item 1 — Business'),
('Primary Services','餐厅自营、加盟品牌及运营支持、餐饮物业出租与转租、开发及咨询服务。按餐饮消费者、加盟商和物业承租方分别理解，避免把全部业务写成纯餐厅销售。','Q26;K25;BECOME','MD&A — Introduction; segment descriptions / franchise support'),
('Core Business Activity','开发、经营及特许加盟 Wendy’s 快餐餐厅，并通过 Global Real Estate & Development 提供餐饮物业及开发支持。美国、国际属于两个地域餐饮分部，物业开发是第三个披露分部。','Q26;K25','MD&A — Introduction / reportable segments'),
('Customer Segment','B2C：餐厅用餐消费者；B2B：加盟经营者及加盟商物业承租方。不同客户关系不能混用。未找到可采纳的终端消费者年龄、收入或客群占比，因此不推定其人口结构。','K25;BECOME','Item 1 — Franchise operations / franchising'),
('End Markets','快餐餐饮消费及餐厅加盟、餐饮物业服务。FY2025 系统覆盖美国和国际市场；餐饮需求、加盟商经营表现与租赁关系分别影响各收入流。','K25;Q26','Business overview / segment information'),
('Business Model','加盟主导的快餐品牌，同时保留公司自营餐厅和物业出租、转租业务。FY2025 美国 5,969 家中 5,546 家加盟；国际 1,428 家中 1,417 家加盟。门店比例不是收入或利润比例，也不代表集团完全轻资产。','K25;Q26','Restaurant counts / segment information'),
('Revenue Model','收入包括自营餐厅销售、加盟销售相关的 royalties、加盟及开发费、广告基金收入以及租金。广告基金收入有对应成本，不等同高毛利品牌许可收入；TimWen 权益收益不应重复加入集团收入。','K25;Q26','Revenue disaggregation / segment information'),
('Value Chain Position','品牌及加盟体系管理者、部分餐厅经营者、餐饮物业出租及转租方；食品供应链依赖外部采购和分销伙伴。并非食品制造商，也非纯物业 REIT。','K25;SUPPLY','Item 1 — Operations / sourcing'),
('Geography Served','FY2025 美国及国际市场；国际分部包括加拿大、英国及其他国家。2026 Q2 期末美国 5,724 家、国际 1,456 家；这是 2026-06-28 的时点，不应与 FY2025 门店数直接视为冲突。','Q26;K25','MD&A — Restaurant counts'),
('Company Size Category','分析归类：大型连锁快餐体系。FY2025 全球 7,397 家餐厅、公司约 14,900 名员工；员工数主要为公司自营业务，不包含所有加盟商员工。规模标签是分析判断，数字为当期披露。','K25','Item 1 — Restaurant counts / Human capital'),
('Product Specialization','以汉堡快餐为核心，扩展到鸡肉、配餐、早餐和 Frosty。早餐及鲜牛肉承诺的适用市场有差异，不应把美国产品供应推定为所有国际市场一致。','Q26;K25;BEEF','MD&A — Introduction / product geographic qualifications'),
('Customer Concentration',None,'K25','Item 1 — Franchise operations'),
('Distribution Channels','自营和加盟餐厅、堂食、外带、得来速及数字化配送。配送可经官网/应用及第三方合作伙伴，菜单、价格、供应及参与门店因地点与渠道而异。','K25;DELIVERY','Item 1 — Restaurant operations / delivery page'),
('Delivery Model','现场制作并经堂食、外带、得来速及配送完成餐饮交付；加盟支持与物业服务属于另一类 B2B 持续关系。不能把线上下单误认成软件订阅交付。','K25;DELIVERY;BECOME','Business / delivery / franchise support'),
('Pricing Structure','餐厅菜单定价、加盟 royalty/fees 及物业租金是不同定价层。FY2025 10-K 描述多数标准美国加盟协议 royalty 为定义销售额的 4%；当前 FAQ 写 NET sales 4–6%，另一加盟页写 GROSS sales 4–6%。口径差异未解决，不能合成统一费率。','K25;FAQ;BECOME','Franchise agreements / franchise royalty FAQ'),
('Recurring Revenue Profile','Royalties 与租金具有持续性，但 royalties 受餐厅销售影响，租赁亦有履约风险；加盟费、广告基金及自营销售应分开。持续收入不等于固定、无风险或全集团订阅收入。','K25;Q26','Revenue recognition / segment information'),
('Capital Intensity','混合模式：加盟品牌部分较少直接承担餐厅投资，自营餐厅、信息系统及自有/承租物业仍需资本。电话会披露开发与技术投入，不能据加盟占比直接断定集团资本密集度低。','K25;CALL','Properties / capital expenditures; CFO remarks'),
('Labor Intensity','餐厅现场运营依赖员工与排班。FY2025 约 14,900 名公司员工，约三分之一全职、三分之二兼职；这不是整个加盟系统员工数，未据此计算统一人效。','K25','Item 1 — Human capital'),
('Regulatory Exposure','食品安全、用工、加盟经营、数据及信息安全等规则影响运营。供应商审查和员工食品安全培训用于控制风险；不同市场法规不同，未量化统一监管风险分值。','K25;SUPPLY','Business — Quality assurance / Item 1A risks'),
('Competitive Positioning','公司以品质与价值主张定位快餐。2026 Q2 电话会管理层承认食品品质执行和价值感出现问题；因此不能仅凭官网营销文字认定竞争优势已获验证。市场份额与品牌强度分数未量化。','K25;BECOME;CALL','Competition / brand positioning; CEO remarks'),
('Product Differentiation','鲜牛肉、现制产品及 Frosty 等属于品牌差异化主张；鲜牛肉存在地区适用限制。管理层在 2026 Q2 指出质量差异化执行下滑，故区分品牌承诺与实际兑现，未将宣传直接当成已验证优势。','K25;BEEF;CALL','Product quality / geographic scope; CEO remarks'),
('Customer Switching Costs',None,'K25','Franchise agreements / consumer relationship'),
('Revenue Cyclicality','年报披露餐厅业务具有温和季节性，通常夏季高于冬季，并受消费者可支配支出及经济环境影响。季节性与经济周期不是同一指标；没有据单季同店销售推算长期周期弹性。','K25;CALL','Seasonality / consumer spending risks; Q2 results'),
('Company Maturity','成熟连锁品牌：首家 Wendy’s 餐厅于 1969 年开业。品牌创立、公司法律实体成立与重组年份不同，不能用前身法律年份替代餐厅品牌历史。','K25','Item 1 — Overview'),
('Technology Dependence','POS、餐厅及厨房系统、数字订单、应用、忠诚度和客户管理支撑运营；技术是餐饮与加盟业务基础设施。电话会提到数字化提升购买频次属于计划，不能当作已实现频次。','K25;BECOME;CALL','Information technology / franchise technology; management remarks'),
('Geographic Concentration','按 FY2025 披露分部收入，美国约占 82.00%、国际约 7.03%、全球物业及开发约 10.97%。物业分部跨地域，不能把后两项全部当海外；这不是系统销售或客户地区占比。','K25;LSEG','FY2025 segment revenue; existing LSEG snapshot'),
('Supply Chain Complexity','依赖采购合作组织、食品加工商及分销网络；鲜牛肉与冷链管理、供应商审核和食品质量控制增加协调要求。FY2025 年报披露主要供应商/分销商集中情况；不将美国供应结构扩展为所有国际市场。','K25;SUPPLY;BEEF','Supply chain / quality assurance; sourcing pages'),
('Contract Duration','FY2025 标准美国加盟初始期通常 20 年，满足条件可延长 10 年，也有 25 年初始期选项；国际安排随市场而异。物业租约期限与加盟协议、集团承租租约剩余期限不能混用。','K25;BECOME','Franchise agreements / leases'),
('IP Dependence','品牌经营依赖 Wendy’s 等注册商标、服务标识及相关版权、域名和商业秘密。未发现支持专利驱动型商业模式的证据；知识产权依赖主要体现为品牌及经营体系保护。','K25','Trademarks and service marks / IP risks'),
('Brand Dependence','公司及加盟商依赖 Wendy’s 品牌声誉、食品质量与消费者认知。年报明确品牌声誉风险；2026 Q2 管理层讨论质量及价值感问题。品牌依赖可支持，但不能因此断言品牌当前强度高。','K25;CALL','Brand reputation risks / CEO remarks')]
rows=[]
for facet,value,ids,section in core:
 ss=[sources[i] for i in ids.split(';')]
 status='SOURCE_SUPPORTED' if value else 'UNKNOWN_NOT_QUANTIFIED'
 limitation='当前所读材料不足以给出该项统一、可量化结论。加盟商数量或合同期限不能替代消费者集中度/转换成本。' if value is None else '跨来源支持不等于独立验证；不同范围、日期及营销主张分别保留。'
 rows.append({'Company ID':'IQ23557','Company Name':"The Wendy’s Company",'Facet':facet,'Value Text':value,'Evidence Status':status,'Evidence Summary':value or limitation,'Source IDs':ids,'Source Links':'; '.join(s['url'] for s in ss),'Source Locations':section,'Document Provenance':'; '.join(f"{s['id']}: {s['kind']}; published/filed {s['date']}; fact period {s['period']}; {s['url']}" for s in ss),'Fact Period':'; '.join(dict.fromkeys(s['period'] for s in ss)),'Limitations':limitation,'Historical Fallback':'FY2025 annual business disclosure used where quarterly detail is limited. No IPO registration relied on; IPO search not needed for these populated claims.','Included In Current Comp Score':False})
d['core_facets']=rows
for r in d['facets']:
 if r['Segment ID']=='RE' and r['Facet'] in ['Ownership / Operating Role','Development / Advisory Services']:
  r['Source IDs']+=';BLOG;BECOME'
  r['Evidence Summary']+=' 官网加盟开发页补充开发支持；历史官方博客明确 Build-to-Suit 可由 Wendy’s 直接出租或转租。博客未核实发布日期，不用于证明当前物业数量。'
 if r['Facet'] in ['Brand Strength','Pricing Power','Recent Operating Demand Signal']:
  r['Source IDs']+=';CALL;CALL2'
  r['Evidence Summary']+=' 2026-08-07 电话会两份转载正文均给出美国客流 -12.5%、平均客单 +5.6%；同一电话会不是两份独立事实来源。客单变化包含折扣、早餐时段和产品组合，不能证明纯定价权。'
 if r['Facet']=='Franchise Royalty / Fee Terms':
  r['Source IDs']+=';BECOME'
  r['Limitations']+=' 官网 FAQ 使用 NET sales，另一加盟页使用 GROSS sales；均无可验证生效日期，分母差异保留为未解决，不强行统一。'
 r['Source IDs']=';'.join(dict.fromkeys(x.strip() for x in r['Source IDs'].split(';')))
 ss=[sources[i] for i in r['Source IDs'].split(';')]
 r['Document Provenance']='; '.join(f"{s['id']}: {s['kind']}; published/filed {s['date']}; fact period {s['period']}; {s['url']}" for s in ss)
 r['Source Links']='; '.join(s['url'] for s in ss)
for r in rows+d['facets']:
 ids=r['Source IDs'].split(';')
 if r['Value Text'] is None: verdict='证据不足：未填值；不能将未披露当作不存在。'
 elif r['Facet'] in ['Pricing Structure','Franchise Royalty / Fee Terms']: verdict='发现口径差异：SEC 标准协议与网站范围不同；网站 NET / GROSS 分母冲突尚未解决。'
 elif len(ids)==1: verdict='仅一个来源：尚未构成跨来源验证。'
 else: verdict='人工范围核对：相互补充；年度与季度时点分开。同一发行人的披露不构成独立事实验证。'
 r['Cross-source Assessment']=verdict
 r['Source Independence']='SEC filings, official website and management call originate from same issuer; LSEG lineage not independently established; transcript hosts share same call.'
 r['Source Claims']=[{'source_id':i,'document_type':sources[i]['kind'],'publication_or_filing_date':sources[i]['date'],'fact_period':sources[i]['period'],'url':sources[i]['url'],'review_scope':r.get('Source Locations',''),'claim_summary':sources[i]['text'] if i in ['CALL','CALL2','BLOG','BECOME'] else r['Evidence Summary'],'claim_note':'Facet evidence summary, not verbatim quotation; source-specific scope must be read with limitations.'} for i in ids]
d['notes'].append({'topic':'来源时点与历史资料','text':'每个 facet 显示具体来源文件类型、提交/发布日期、事实期和链接。FY2025 10-K 于 2026-02-23 提交，Q2 2026 10-Q 于 2026-08-07 提交；历史博客日期未核实。没有依赖 IPO 注册材料，不声称已穷尽历史文件。','sources':['K25','Q26','BLOG']})
(p/'Wendys_Segment_Facets.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
combined=[dict({'Record Type':'CORE'},**r) for r in rows]+[dict({'Record Type':'SEGMENT'},**r) for r in d['facets']]
keys=list(dict.fromkeys(k for r in combined for k in r))
with (p/'Wendys_Company_and_Segment_Facets.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in combined)
h=Path('outputs/company_research_viewer/index.html'); t=h.read_text(); t=re.sub(r'const wendyPilot=.*?;\n',lambda m:'const wendyPilot='+json.dumps(d,ensure_ascii=False)+';\n',t,count=1)
t=t.replace('function showFacets(){','function showFacets(){if(isWendy())return showWendyCore();',1)
t=t.replace('本轮 9 项证据来源','本轮 '+str(len(d['sources']))+' 项证据来源').replace('没有使用或声称核对 earnings-call 逐字稿。','已读两站转载的同一场 2026 Q2 earnings-call 正文；未核对官方音频，不算两份独立证据。')
t=t.replace('${selected.filled}/30','${isWendy()?28:selected.filled}/30').replace('${selected.total-selected.filled}</b>通用项暂无值','${isWendy()?2:selected.total-selected.filled}</b>通用项暂无值')
t += '''\n<script>
function auditDetails(r){return `<p class="notice">${esc(r['Cross-source Assessment'])}</p><details><summary>文件类型、年份、报告期与来源链接</summary>${(r['Source Claims']||[]).map(s=>`<p><strong>${esc(s.source_id)} · ${esc(s.document_type)}</strong><br>提交/发布：${esc(s.publication_or_filing_date)}<br>事实期：${esc(s.fact_period)}<br>${links(s.url)}<br>核对位置：${esc(s.review_scope)}</p>`).join('')}<p>${esc(r['Source Independence'])}</p></details>`}
function showWendyCore(){let a=wendyPilot.core_facets;$('content').innerHTML='<h2>Wendy’s · 公司通用 Facet · 28 / 30 已填</h2><p class="notice">扩展来源研究档案：不进入现有官网限定的 Target 评分。最新季度缺少细节时引用 FY2025 年报并标明日期；未依赖 IPO 文件。未知不强行填值。</p>'+a.map(r=>`<article class="card"><h3>${esc(labels[r.Facet]||r.Facet)} <small>${esc(r.Facet)}</small></h3><div class="value">${esc(r['Value Text']||'未找到足够支持统一结论的证据，保留未知。')}</div><p class="small">原文位置：${esc(r['Source Locations'])}</p>${auditDetails(r)}<p class="small">${esc(r.Limitations)}</p></article>`).join('')}
const originalShowWendyIndustry=showWendyIndustry;
showWendyIndustry=function(){originalShowWendyIndustry();const cards=$('content').querySelectorAll('article.card');let a=wendyPilot.facets.filter(x=>(pilotSegment==='ALL'||x['Segment ID']===pilotSegment)&&(pilotStatus==='ALL'||(pilotStatus==='FILLED'?x['Value Text']!=null:pilotStatus==='UNKNOWN'?x['Value Text']==null:true)));cards.forEach((c,i)=>{if(a[i])c.insertAdjacentHTML('beforeend',auditDetails(a[i]))})};
</script>\n'''
h.write_text(t)
assert len(rows)==30 and len(combined)==72 and sum(r['Value Text'] is not None for r in rows)==28
print({'core_filled':28,'core_total':30,'segment_rows':42,'sources':len(d['sources']),'csv_rows':len(combined)})
