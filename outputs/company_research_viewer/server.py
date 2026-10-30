import csv,json,pathlib,collections,urllib.parse,http.server,itertools
ROOT=pathlib.Path(__file__).resolve().parents[1];BASE=ROOT/'global_comps_560';HERE=pathlib.Path(__file__).resolve().parent
csv.field_size_limit(2**31-1)
def load(p):return json.loads(p.read_text())
facetrows=load(BASE/'repaired_facets_20261028/Corrected_Facets.json');facets=collections.defaultdict(list)
for r in facetrows:facets[(r['Entity Role'],r['Entity ID'])].append(r)
source_rows=load(BASE/'multisource_audit_20261028/Target_Sources.json')+load(BASE/'multisource_audit_20261028/Public_Sources.json');sources=collections.defaultdict(list);evidence={}
for r in source_rows:sources[(r['Entity Role'],r['Entity ID'])].append(r);evidence[r['Evidence ID']]=r
statements=collections.defaultdict(list)
for r in load(BASE/'semantic_validation_20261028/Source_Statements.json'):statements[(r['Entity Role'],r['Entity ID'],r['Facet'])].append(r)
comps=load(BASE/'repaired_facets_20261028/Corrected_Comp_Results.json');compindex=collections.defaultdict(list)
for r in comps:compindex[r['Target ID']].append(r)
companies=[]
for (role,i),rs in facets.items():
 companies.append({'role':role,'id':i,'name':rs[0]['Company Name'],'filled':sum(r['Corrected Value'] is not None for r in rs),'total':len(rs),'eligible':sum(bool(r['Eligible For Scoring']) for r in rs),'reviewed':sum(bool(r['Human Reviewed Fact']) for r in rs),'quarantined':sum(r['Repair Action']=='UNRESOLVED_VALUE_QUARANTINED' for r in rs),'sources':len(sources[role,i])})
companies.sort(key=lambda x:(x['role']!='TARGET',x['name'].lower()))
DESCS={
'Corrected_Facets':'全部公司 × 30 个 facet：原值、修正值、允许打分与否、来源、日期、修复状态。',
'Corrected_Facet_Scores':'每对 target–comp 的逐项相似度、权重与贡献；未知值不计分。',
'Corrected_Comp_Results':'每个目标原有 10 个候选的修复后排名、总分、覆盖率和旧分。',
'Conflict_Dispositions':'3,016 个原始冲突字段的处理结果；未确认字段仍隔离。',
'Conflict_Pair_Dispositions':'来源两两比较的文本、原始模型提示和处理结果。',
'Rejected_Source_Statements':'被排除的来源语句及原因。',
'Final_Quality_Exclusions':'最终质量检查排除的文本，不代表全部历史排除记录。',
'Reextracted_Source_Evidence':'重新从缓存提取的候选语句；不等同于人工核实。',
'Target_Sources':'Target 的官网、LSEG、SEC 等来源记录；非官网仅诊断，不得进入 target 选择评分。',
'Public_Sources':'上市候选公司的多来源文本、链接、缓存位置和获取状态。',
'Target_Status':'560 个 target 的处理状态及未生成候选的原因。',
'Candidate_Data':'已发现上市候选的数据库信息快照；并非全部全球上市公司的完整数据。',
'FF49_Context':'行业分类与行业估值背景，不等同于已验证的 target 行业输入。',
'Weights':'原有的 facet 建议权重。',
 'target_allowed_profiles':'只由官网生成的 target 允许输入资料。',
 'Targets_560':'老师提供的 560 公司目标清单及标识。',
 'Source_Manifest':'原始输入文件及来源登记。',
 'FF49_Benchmarks_560':'每个 target 对应的 FF49 行业背景和基准，供诊断。',
 'FF49_Latest_49':'49 个行业的最新可用基准记录及日期。',
 'FF49_SIC_Mapping':'SIC 与 FF49 行业的映射规则。',
 'Date_Aligned_Comparisons':'按数据日期对齐的财务及行业比较。',
 'WRDS_Matched_Latest':'匹配到目标的 WRDS 最新基本面比率。',
 'annual_five_years':'LSEG 已下载的过去五年年度财务快照。',
 'business_segments':'LSEG 业务分部记录，包括可用的分部财务信息。',
 'geographic_segments':'LSEG 地区分部记录。',
 'company_profiles_raw':'LSEG 原始公司描述、分类和标识快照。',
 'Companies_560':'LSEG 下载用的目标公司标识和匹配信息。',
 'Coverage_560':'字段覆盖率与下载缺失信息。',
 'Evidence':'LSEG 字段值、来源和下载证据记录。',
 'Field_Guide':'字段定义、单位或下载方法说明。',
 'latest_quarter':'最新可用季度财务。',
 'ltm':'最近十二个月财务。',
 'market':'市场价格、资本结构或估值快照。',
 'Scoring_Weights':'前期设定的建议权重，非已校准最优权重。',
 'Review_Queue':'前期标识匹配及数据缺口待审清单。'}
CAT=[];FILES={}
groups=[('修复和评分',BASE/'repaired_facets_20261028',['Corrected_Facets','Corrected_Facet_Scores','Corrected_Comp_Results','Conflict_Dispositions','Conflict_Pair_Dispositions','Rejected_Source_Statements','Final_Quality_Exclusions','Reextracted_Source_Evidence']),('多来源证据',BASE/'multisource_audit_20261028',['Target_Sources','Public_Sources']),('候选与行业背景',BASE/'global_run_20261028',['Target_Status','Candidate_Data','FF49_Context','Weights','target_allowed_profiles'])]
for group,d,names in groups:
 for name in names:FILES[name]=d/(name+'.csv');CAT.append({'dataset':name,'group':group,'description':DESCS.get(name,'原始数据快照，保留原字段。')})
for prefix,group,d in [('Prepared_','老师文件 / WRDS / Capital IQ / FF49',BASE/'prepared'),('LSEG_','LSEG 财务与公司资料',ROOT/'lseg_downloads/delivery')]:
 for p in sorted(d.glob('*.csv')):
  name=prefix+p.stem;FILES[name]=p
  desc=DESCS.get(p.stem)
  if not desc:
   desc=('Capital IQ '+p.stem.removeprefix('CapIQ_').replace('_',' ')+'：提供文件中的原始字段、公司标识及数值。') if p.stem.startswith('CapIQ_') else ('已提供数据库参考记录：'+p.stem.replace('_',' '))
  CAT.append({'dataset':name,'group':group,'description':desc})
for r in CAT:
 with FILES[r['dataset']].open(encoding='utf-8-sig',newline='') as f:
  reader=csv.reader(f);r['columns']=next(reader);r['rows']=sum(1 for _ in reader)
print('READY',len(companies),'companies',len(CAT),'tables',flush=True)
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def send(self,data,kind='application/json; charset=utf-8',code=200):
  b=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False,default=str).encode();self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',len(b));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urllib.parse.urlparse(self.path);q=urllib.parse.parse_qs(u.query);get=lambda k,d='':q.get(k,[d])[0]
  try:
   if u.path=='/':return self.send((HERE/'index.html').read_bytes(),'text/html; charset=utf-8')
   if u.path=='/api/catalog':return self.send(CAT)
   if u.path=='/api/companies':return self.send(companies)
   if u.path=='/api/company':
    k=(get('role'),get('id'));return self.send({'facets':facets.get(k,[]),'sources':sources.get(k,[]),'comps':compindex.get(k[1],[]) if k[0]=='TARGET' else []})
   if u.path=='/api/facet_sources':return self.send(statements.get((get('role'),get('id'),get('facet')),[]))
   if u.path=='/api/source':
    r=evidence.get(get('id'))
    if not r:return self.send({'error':'无此来源'},code=404)
    p=pathlib.Path(r.get('Full Text or Snapshot Path') or '/not-present')
    offset=max(0,int(get('offset','0')));limit=50000
    if p.is_file():
     with p.open(errors='replace') as h:
      if offset:h.read(offset)
      chunk=h.read(limit+1)
    else:chunk=r['Source Text'][offset:offset+limit+1]
    return self.send({'text':chunk[:limit],'offset':offset,'has_more':len(chunk)>limit,'cached':p.is_file(),'record':r})
   if u.path=='/api/table':
    name=get('name');p=FILES.get(name)
    if not p:return self.send({'error':'无此数据表'},code=404)
    offset=max(0,int(get('offset','0')));search=get('search').lower();rows=[];matched=0
    with p.open(encoding='utf-8-sig',newline='') as f:
     for row in csv.DictReader(f):
      if search and search not in ' '.join(str(v) for v in row.values()).lower():continue
      if matched>=offset and len(rows)<30:rows.append(row)
      matched+=1
      if not search and len(rows)==30:break
    return self.send({'rows':rows,'offset':offset,'has_more':len(rows)==30})
   return self.send({'error':'not found'},code=404)
  except Exception as e:return self.send({'error':str(e)},code=500)
http.server.ThreadingHTTPServer(('127.0.0.1',8768),Handler).serve_forever()
