import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.dirname(new URL(import.meta.url).pathname);
const dataDir=path.join(root,'prepared');
const read=async n=>JSON.parse(await fs.readFile(path.join(dataDir,n+'.json'),'utf8'));
const wb=Workbook.create();
const specs=[];
function letter(n){let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
function table(name,rows,cols=null){
 const sh=wb.worksheets.add(name);sh.showGridLines=false;
 cols=cols||Object.keys(rows[0]||{});
 if(!cols.length)cols=['Status'];
 sh.getRangeByIndexes(0,0,1,cols.length).values=[cols];
 for(let start=0;start<rows.length;start+=1000){
  const part=rows.slice(start,start+1000).map(r=>cols.map(k=>{
   const v=r[k]??null;
   return typeof v==='string'&&v.startsWith('=')?"'"+v:v;
  }));
  sh.getRangeByIndexes(start+1,0,part.length,cols.length).values=part;
 }
 const used=sh.getRangeByIndexes(0,0,rows.length+1,cols.length);
 used.format.font={name:'Arial',size:10};used.format.rowHeight=20;
 used.format.verticalAlignment='center';used.format.columnWidth=20;
 const head=sh.getRangeByIndexes(0,0,1,cols.length);
 head.format.fill='#243746';head.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};
 head.format.wrapText=true;head.format.rowHeight=45;
 sh.freezePanes.freezeRows(1);sh.freezePanes.freezeColumns(Math.min(cols.length,3));
 for(let i=0;i<cols.length;i++){
  const key=cols[i];const col=sh.getRangeByIndexes(0,i,rows.length+1,1);
  if(/company_name|Company Name|name_original/.test(key))col.format.columnWidth=32;
  if(/description|excerpt|note|status|reason|suggested_query|note|source_location/i.test(key))col.format.columnWidth=48;
  if(/url/i.test(key))col.format.columnWidth=52;
  if(/^(proposed_weight)$/.test(key)&&rows.length)sh.getRangeByIndexes(1,i,rows.length,1).setNumberFormat('0%');
  if(/(Margin|Growth|CAGR|Beta|Revenue|EBITDA|Median|difference|value)/.test(key)&&!/(description|excerpt|status|location)/i.test(key)&&rows.length)
   sh.getRangeByIndexes(1,i,rows.length,1).setNumberFormat('#,##0.00;(#,##0.00);0.00');
 }
 // Large raw source tables are intentionally scrollable; fields retain full values.
 specs.push({name,rows:rows.length,columns:cols.length});return sh;
}
if(process.argv.includes('--lseg-560')){
 const dir=path.join(root,'../lseg_downloads/delivery');
 const get=async n=>JSON.parse(await fs.readFile(path.join(dir,n+'.json'),'utf8'));
 const summary=await get('download_summary');
 const labels={targets:'Original targets',business_summaries:'Business summaries',employees_available:'Employee counts',annual_companies_with_revenue:'Companies with annual revenue',annual_companies_with_five_revenue_years:'Companies with five revenue years',latest_quarter_companies_with_revenue:'Companies with quarterly revenue',ltm_companies_with_revenue:'Companies with LTM revenue',market_caps_available:'Company market caps',business_segment_companies:'Companies with segment revenue',geographic_segment_companies:'Companies with geographic revenue',identity_review_companies:'Name or entity review required',annual_rows:'Annual observation slots',source_evidence_records:'Evidence records'};
 const stat=Object.entries(labels).map(([k,v])=>({Metric:v,Value:summary[k]}));
 stat.push({Metric:'Scope',Value:'Original 560 only. Data collection; no comps, scores or sample split.'});
 const overview=table('Download Summary',stat);overview.getRange('A1:A15').format.columnWidth=55;overview.getRange('B1:B15').format.columnWidth=90;
 const definitions=[['Companies 560','Companies_560'],['Coverage 560','Coverage_560'],['Annual Financials','annual_five_years'],['Latest Quarter','latest_quarter'],['LTM','ltm'],['Market Snapshot','market'],['Business Segments','business_segments'],['Geographic Segments','geographic_segments'],['Evidence','Evidence'],['Field Guide','Field_Guide']];
 for(const [sheet,file] of definitions){
  const rows=await get(file);const cols=Object.keys(rows[0]||{});
  for(const row of rows)for(const key of cols){
   const val=row[key];
   if(typeof val==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(val)&&(key.endsWith('.DATE')||key.endsWith('.CALCDATE')||key.includes('Employees Date')||key.includes('Incorporation Date')))row[key]=new Date(val+'T00:00:00Z');
  }
  const sh=table(sheet,rows);
  for(let i=0;i<cols.length;i++){
   const col=sh.getRangeByIndexes(0,i,rows.length+1,1),key=cols[i];
   if(/Company Name|Name$|Description/.test(key))col.format.columnWidth=34;
   if(key.startsWith('TR.')&&!key.endsWith('.DATE')&&!key.endsWith('.CALCDATE'))col.format.columnWidth=23;
   if(key.endsWith('.DATE')||key.endsWith('.CALCDATE')||key.includes('Employees Date')||key.includes('Incorporation Date')){
    if(rows.length)sh.getRangeByIndexes(1,i,rows.length,1).setNumberFormat('yyyy-mm-dd');
   }
   if(key==='LSEG Business Summary'||key==='Source Text'){
    col.format.columnWidth=100;col.format.wrapText=true;
    sh.getRangeByIndexes(1,0,rows.length,cols.length).format.rowHeight=150;
   }
   if(/Identity Status|Source Location|Notes|Unit \/ Data Type/.test(key)){col.format.columnWidth=52;col.format.wrapText=true;}
   if(key==='TR.EFFECTIVETAXRATE'&&rows.length)sh.getRangeByIndexes(1,i,rows.length,1).setNumberFormat('0.00"%"');
  }
 }
 wb.recalculate();
 console.log((await wb.inspect({kind:'table',range:"'Download Summary'!A1:B14",tableMaxRows:14,tableMaxCols:2,maxChars:2200})).ndjson);
 console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:10},maxChars:600})).ndjson);
 if(process.argv.includes('--export-only')){
  await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(dir,'560_Company_Data.xlsx'));
  console.log('Exported 560-company workbook without rendering cache');process.exit(0);
 }
 await fs.mkdir(path.join(dir,'previews'),{recursive:true});
 for(const {name} of specs){
  const range=name==='Download Summary'?'A1:B8':name==='Evidence'?'D1:F3':name==='Field Guide'?'A1:D5':`A1:F5`;
  const blob=await wb.render({sheetName:name,range,scale:1,format:'png'});
  await fs.writeFile(path.join(dir,'previews',name.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));
 }
 await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(dir,'560_Company_Data.xlsx'));
 console.log('Exported 560-company workbook');process.exit(0);
}
if(process.argv.includes('--download-index')){
 const get=async n=>JSON.parse(await fs.readFile(path.join(root,'download_delivery',n+'.json'),'utf8'));
 const s=table('Download Status',await get('Status'));
 s.getRange('C1:C11').format.columnWidth=100;s.getRange('A1:C11').format.wrapText=true;s.getRange('A2:C11').format.rowHeight=45;
 const evidence=await get('Evidence_Index');
 // One source row per record in Excel. The full corpus is in Evidence_FULL.csv.
 // Limit financial index rows to one record per entity/table. Full time series stay in CSV.
 const seen=new Set();const selected=evidence.filter(r=>{
  if(r.source_type!=='WRDS_API_FUNDAMENTALS')return true;
  const k=r.company_id+'|'+r.section;if(seen.has(k))return false;seen.add(k);return true;
 });
 for(const r of selected)for(const k in r)if(typeof r[k]==='string')r[k]=r[k].replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g,'');
 const e=table('Evidence',selected);
 e.getRangeByIndexes(0,4,selected.length+1,1).format.columnWidth=105;
 e.getRangeByIndexes(1,4,selected.length,2).format.wrapText=true;
 e.getRangeByIndexes(1,0,selected.length,Object.keys(selected[0]).length).format.rowHeight=165;
 e.getRangeByIndexes(0,5,selected.length+1,1).format.columnWidth=55;
 const match=JSON.parse(await fs.readFile(path.join(root,'web_evidence/wrds_api/target_reference_matches.json'),'utf8'));
 table('Entity Matches',match.map(r=>({...r,gvkeys:r.gvkeys.join(', ')})));
 const vars=await get('Variables');if(vars.length)table('Variable Names',vars);
 wb.recalculate();
 console.log((await wb.inspect({kind:'table',range:"'Download Status'!A1:C5",tableMaxRows:5,tableMaxCols:3,maxChars:1200})).ndjson);
 await fs.mkdir(path.join(root,'download_delivery/previews'),{recursive:true});
 for(const {name} of specs){
  const range=name==='Evidence'?'D1:F3':name==='Download Status'?'A1:C5':name==='Entity Matches'?'A1:D5':'A1:E5';
  const blob=await wb.render({sheetName:name,range,scale:1,format:'png'});
  await fs.writeFile(path.join(root,'download_delivery/previews',name.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));
 }
 await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'download_delivery/Public_Company_Source_Index.xlsx'));
 console.log('Exported data-only source index',selected.length,'source records');process.exit(0);
}
if(process.argv.includes('--blinded')){
 const readAt=async p=>JSON.parse(await fs.readFile(path.join(root,p),'utf8'));
 const status=table('Status',await readAt('web_evidence/Status.json'));
 status.getRange('C1:C13').format.columnWidth=105;
 status.getRange('A2:C13').format.rowHeight=40;
 status.getRange('A1:C13').format.wrapText=true;
 table('Candidate Retrieval',await readAt('blinded/retrieved_candidates.json'));
 const inputs=table('Allowed Target Inputs',await readAt('blinded/target_inputs.json'));
 inputs.getRange('D2:F561').setNumberFormat('#,##0.00');
 table('Split and Coverage',await readAt('blinded/retrieval_coverage.json'));
 const evidence=await readAt('web_evidence/Evidence.json');
 const ev=table('Evidence',evidence);
 ev.getRangeByIndexes(1,0,evidence.length,Object.keys(evidence[0]).length).format.rowHeight=350;
 ev.getRangeByIndexes(0,7,evidence.length+1,1).format.columnWidth=120;
 ev.getRangeByIndexes(1,7,evidence.length,2).format.wrapText=true;
 ev.getRangeByIndexes(0,8,evidence.length+1,1).format.columnWidth=65;
 table('Proposed Weights',await read('Scoring_Weights'));
 wb.recalculate();
 console.log((await wb.inspect({kind:'table',range:"'Allowed Target Inputs'!A1:F4",tableMaxRows:4,tableMaxCols:6,maxChars:1400})).ndjson);
 await fs.mkdir(path.join(root,'previews_blinded'),{recursive:true});
 for(const {name} of specs){
  const range=name==='Evidence'?'F1:I3':name==='Status'?'A1:C6':`A1:${letter(Math.min(5,specs.find(x=>x.name===name).columns-1))}5`;
  const blob=await wb.render({sheetName:name,range,scale:1,format:'png'});
  await fs.writeFile(path.join(root,'previews_blinded',name.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));
 }
 console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:10},maxChars:600})).ndjson);
 await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'Global_Comps_Evidence_and_Blinded_Inputs.xlsx'));
 console.log('Exported blinded evidence workbook');
 process.exit(0);
}
const progress=JSON.parse(await fs.readFile(path.join(dataDir,'progress.json'),'utf8'));
const summary=[
 {Item:'Deliverable status',Value:'DATA PREPARATION ONLY',Detail:'Global public-comps discovery and final pair scoring remain unfinished.'},
 {Item:'Target universe',Value:560,Detail:'All original target IDs retained; no 3–30x EV/EBITDA exclusion.'},
 {Item:'Candidate search scope',Value:'Global public companies',Detail:'Allowed scope, not an exhaustive or completed search.'},
 {Item:'FF49 mapped targets',Value:progress.ff49_mapped_targets,Detail:'Official SIC-to-FF49 mapping; does not describe segment revenue weights.'},
 {Item:'Industry benchmark date',Value:progress.ff49_latest_date,Detail:'Latest available month in supplied WRDS FF49 file; all 49 industries retained.'},
 {Item:'WRDS conservative matches',Value:progress.wrds_unambiguous_ticker_name_matches,Detail:'One historical GVKEY and normalized ticker/name consistency. Not a full identifier audit.'},
 {Item:'WRDS unresolved targets',Value:101,Detail:'70 without exact ticker; 31 ambiguous/name mismatch. Never filled from a different entity.'},
 {Item:'Facet records',Value:progress.facet_records,Detail:'Source excerpts and explicit UNKNOWN values; not final web-verified semantic extraction.'},
 {Item:'Aligned ratio comparisons',Value:progress.date_aligned_comparison_values,Detail:'Company and FF49 industry values from the same monthly Date; duplicate metric labels withheld.'},
 {Item:'Final scored targets',Value:0,Detail:'No invented rankings or percentages presented as completed research.'},
 {Item:'Source units',Value:'Preserved as provided',Detail:'CapIQ amount headers do not specify currency/scale. Do not assume USD millions.'},
 {Item:'Date handling',Value:'Source dates retained',Detail:'Latest CapIQ market as-of date is not specified. CY2025 labels may have non-December period-end values.'},
 {Item:'Forecast columns',Value:'Capital IQ estimates',Detail:'FY2026/NTM estimates remain source estimates; they are not model predictions or realized outcomes.'},
 {Item:'Weights',Value:'Proposed, not calibrated',Detail:'Edit only after human calibration. Pair scores unavailable until evidence-supported global matching is performed.'},
 {Item:'Source registry',Value:'Source Manifest',Detail:'Original files kept unchanged; raw field locations available in accompanying provenance CSV.'}
];
table('Status',summary);wb.worksheets.getItem('Status').getRange('C1:C16').format.columnWidth=100;
const targets=await read('Targets_560');
const mainCols=['company_id','ticker','company_name','capiq_display_name','website','exchange','sic4','ff49','ff49_name','capiq_identity_status','wrds_match_status','wrds_ratio_date','ff49_latest_date','global_comp_research_status','facet_status','source_url','source_location'];
table('Targets 560',targets,mainCols);
table('FF49 per Target',await read('FF49_Benchmarks_560'));
table('Facet Evidence',await read('Target_Facet_Evidence'));
table('Scoring Weights',await read('Scoring_Weights'));
table('Review Queue',await read('Review_Queue'));
const keyMetrics=new Set(['Enterprise Value Multiple','Gross Profit Margin','Net Profit Margin',
 'Operating Profit Margin Before Depreciation','Total Debt/EBITDA','Current Ratio','Research and Development/Sales']);
table('Aligned Ratios',(await read('Date_Aligned_Comparisons')).filter(r=>keyMetrics.has(r.metric)));
table('WRDS Latest Matched',await read('WRDS_Matched_Latest'));
table('FF49 Industry Medians',await read('FF49_Latest_49'));
for(const [name,file] of [
 ['CapIQ Key Financials','CapIQ_Key_Financials'],['CapIQ Financial Data','CapIQ_Financial_Data'],
 ['CapIQ Multiples','CapIQ_Trading_Multiples'],['CapIQ Operating Stats','CapIQ_Operating_Statistics'],
 ['CapIQ Business Descriptions','CapIQ_Business_Description'],['CapIQ Credit Health','CapIQ_Credit_Health_Panel'],
 ['CapIQ Match Notes','CapIQ_Match_notes']]){
 const rows=await read(file);
 for(const r of rows)r.source_url='https://drive.google.com/file/d/1cJwV_NyfypLGy59GsNmKSjj0XhYJQs13/view';
 table(name,rows);
}
table('Source Manifest',await read('Source_Manifest'));
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:"'Targets 560'!A1:I5",tableMaxRows:5,tableMaxCols:9,maxChars:1800})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:10},maxChars:1200})).ndjson);
await fs.mkdir(path.join(root,'previews'),{recursive:true});
for(const {name} of specs){
 const blob=await wb.render({sheetName:name,range:`A1:${letter(Math.min(7,specs.find(x=>x.name===name).columns-1))}6`,scale:1.3,format:'png'});
 await fs.writeFile(path.join(root,'previews',name.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(root,'560_Targets_Source_and_FF49_Preparation.xlsx'));
await fs.writeFile(path.join(root,'workbook_tables.json'),JSON.stringify(specs,null,2));
console.log('Exported workbook:',specs.length,'sheets');
