import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.dirname(new URL(import.meta.url).pathname),dir=path.join(root,'global_run_20261028');
const read=async n=>JSON.parse(await fs.readFile(path.join(dir,n+'.json'),'utf8'));
const wb=Workbook.create(),specs=[];
const sanitize=v=>typeof v==='string'?v.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g,'').slice(0,32000):v??null;
function table(name,rows,cols=Object.keys(rows[0]||{})){
 const s=wb.worksheets.add(name);s.showGridLines=false;
 s.getRangeByIndexes(0,0,1,cols.length).values=[cols];
 for(let i=0;i<rows.length;i+=1000)s.getRangeByIndexes(i+1,0,Math.min(1000,rows.length-i),cols.length).values=rows.slice(i,i+1000).map(r=>cols.map(k=>sanitize(r[k])));
 const u=s.getRangeByIndexes(0,0,rows.length+1,cols.length);u.format.font={name:'Arial',size:10};u.format.rowHeight=22;u.format.verticalAlignment='top';u.format.columnWidth=20;
 const h=s.getRangeByIndexes(0,0,1,cols.length);h.format.fill='#173E50';h.format.font={name:'Arial',size:10,color:'#FFFFFF',bold:true};h.format.wrapText=true;h.format.rowHeight=50;
 s.freezePanes.freezeRows(1);s.freezePanes.freezeColumns(Math.min(2,cols.length));
 for(let i=0;i<cols.length;i++){
  const k=cols[i],c=s.getRangeByIndexes(0,i,rows.length+1,1);
  if(/Name|name/.test(k))c.format.columnWidth=32;
  if(/Source Text|Description|description$/.test(k)){c.format.columnWidth=76;c.format.wrapText=true;}
  if(/Link|link|urls|website/i.test(k))c.format.columnWidth=53;
  if(/Status|Meaning|Note|Method|Extraction|Reason|Field|source_locator|source_location/i.test(k)){c.format.columnWidth=44;c.format.wrapText=true;}
  if(/Weight|Coverage/.test(k)&&rows.length)s.getRangeByIndexes(1,i,rows.length,1).setNumberFormat('0.0%');
  if(/Percent|Cosine|^Score \||^Contribution \||Ranking Index/.test(k)&&rows.length)s.getRangeByIndexes(1,i,rows.length,1).setNumberFormat('0.00');
 }
 specs.push({name,rows:rows.length,cols:cols.length});console.log('Prepared sheet',name,rows.length);return s;
}
const stats=await read('stats');
const overview=[
 {Item:'Deliverable',Value:'GLOBAL COMPS — AUTOMATED RESEARCH DRAFT'},
 ...Object.entries(stats).map(([Item,Value])=>({Item,Value})),
 {Item:'Target boundary',Value:'Only instructor name/website, official business-page text, instructor Revenue/EBITDA/Debt. No target public descriptions, SIC, true multiple, analyst estimates, SEC or database financials used in matching.'},
 {Item:'Allowed finances',Value:'Instructor amounts retained, but unit and period undocumented. Debt derived from Revenue × Debt/Revenue. Numeric size is not scored.'},
 {Item:'Global discovery scope',Value:'LSEG listed ordinary primary-issue shares with a reported market cap. Five capitalization bands; 10,000-hit caps in three bands. No claim of exhaustive coverage of every listed company, ADR, microcap or missing-market-cap issuer.'},
 {Item:'Retrieval',Value:'Global LSEG listing identifiers joined to WRDS company descriptions, plus available LSEG summaries. 40 candidates per readable target using 55% semantic cosine + 45% within-target normalized TF-IDF cosine. Self issuer and aliases excluded by identifier/name/website.'},
 {Item:'Facet scoring',Value:'16 proposed weighted facets; continuous text cosine or explicit-category Jaccard ×100. Other rubric facets remain context. Cosine model: all-MiniLM-L6-v2. Scores are similarity indexes, not probabilities or valuation accuracy.'},
 {Item:'Total formula',Value:'SUM(weight × facet score) / SUM(observed weights). UNKNOWN excluded, not a shared-none bonus. Contribution columns sum to overall percent; coverage shown separately. Ranking index = similarity × sqrt(coverage), to avoid a hard coverage cutoff.'},
 {Item:'FF49',Value:'2% proposed soft feature. Target label inferred from website keywords only; public SIC mapped where available. Industry benchmark snapshot 2025-12-31 is context, not target valuation. Uninferred labels stay blank.'},
 {Item:'Human review',Value:'All pairs remain unvalidated. Check actual products, customer type, revenue model, geography, segment exposure, source currency/date and current entity identity before accepting comps.'},
 {Item:'Known limitations',Value:'Website marketing can distort text matching. Keyword-selected sentences are evidence excerpts, not confirmed structured facts. Similarity weights overlap and are uncalibrated. Parent/subsidiary and diversified-segment eligibility still need review.'},
 {Item:'Financial context',Value:'Public-candidate LSEG FY0 figures are USD base units, not necessarily LTM. WRDS/CapIQ snapshots retain their own dates. Do not combine these amounts or multiples without aligning periods and definitions.'},
 {Item:'Forecast stage',Value:'NOT STARTED. Show this comp output to user before revenue/EBITDA forecasting. No training/validation/holdout split created in this run.'},
 {Item:'How to trace a facet',Value:'Comp Results has a score and contribution column for every weighted facet. Match Target ID + facet in Target Facets, and Candidate RIC + facet in Public Facets, for values, source excerpts and links. Full pair-by-facet long table is supplied as Facet_Scores.csv.'},
 {Item:'Editable score mechanics',Value:'Weights sheet feeds observed weights and contributions. Similarity totals recalculate. Rank and candidate membership are a frozen research snapshot and do not automatically rerank after edits.'}
];
const cover=table('Read Me',overview);cover.getRangeByIndexes(0,0,overview.length+1,1).format.columnWidth=38;cover.getRangeByIndexes(0,1,overview.length+1,1).format.columnWidth=125;cover.getRangeByIndexes(1,1,overview.length,1).format.wrapText=true;cover.getRangeByIndexes(1,0,overview.length,2).format.rowHeight=56;
const status=await read('Target_Status');table('Target Status',status);
table('Analyst QA',await read('Analyst_QA'));
const weights=await read('Weights'),positive=weights.filter(w=>w.proposed_weight>0),details=await read('Facet_Scores');
const pairDetails=new Map();for(const r of details){const k=r['Target ID']+'|'+r['Candidate RIC'];if(!pairDetails.has(k))pairDetails.set(k,new Map());pairDetails.get(k).set(r.Facet,r);}
const results=await read('Comp_Results'),baseCols=Object.keys(results[0]);
const wide=results.map(r=>{const ds=pairDetails.get(r['Target ID']+'|'+r['Candidate RIC']);const row={...r};for(const w of positive)row['Score | '+w.facet]=ds.get(w.facet)?.['Facet Similarity Percent']??null;for(const w of positive)row['Contribution | '+w.facet]=ds.get(w.facet)?.['Contribution Percent Points']??null;return row;});
const resultSheet=table('Comp Results',wide);resultSheet.getRangeByIndexes(1,0,results.length,Object.keys(wide[0]).length).format.rowHeight=64;
const targetFacets=await read('Target_Facets');const tf=table('Target Facets',targetFacets);tf.getRangeByIndexes(1,0,targetFacets.length,10).format.rowHeight=76;
const targets=await read('target_allowed_profiles');table('Allowed Target Inputs',targets.map(t=>({'Target ID':t.target_id,'Target Name':t.target_name,'Official Website':t.website,'Instructor Revenue':t.revenue,'Instructor EBITDA':t.ebitda,'Instructor Debt Derived':t.debt,'Debt Derivation':t.debt_basis,'Financial Unit and Period':t.financial_unit,'Source':'Original company list for interns; cached input_companies.json','Source Link':'https://docs.google.com/spreadsheets/d/1hhacI53Ya8af_PFjpP7Nqf77SgGDy6Lyu9WqMT8HH-s/edit','Website Evidence Status':t.status})));
const candidates=await read('Candidate_Data');
function dateValue(v){return typeof v==='number'&&v>1e11?new Date(v).toISOString().slice(0,10):v;}
table('Public Candidate Data',candidates.map(c=>({'Candidate RIC':c.candidate_ric,'Candidate Name':c.candidate_name,'Issuer ID':c.issuer_id,'ISIN':c.isin,'Listing Country':c.listing_country,'Exchange':c.exchange,'Listing Status':c.listing_status,'Business Description':c.description,'Source Link':c.source_link,'Source Field':c.source_locator,'Description Provider':c.description_source,'Website':c.candidate_website,'WRDS GVKEY':c.wrds_gvkey,'WRDS SIC':c.wrds_sic,'WRDS Business Description':c['WRDS Description'],'WRDS Description Link':c['WRDS Description Link'],'CapIQ Business Description':c['Provided CapIQ Description'],'CapIQ Source Link':c['CapIQ Source Link'],'CapIQ Source Location':c['CapIQ Source Location'],'LSEG Industry':c.public_TRBC_industry,'LSEG Annual Revenue USD':c.public_revenue_usd,'LSEG Annual EBITDA USD':c.public_ebitda_usd,'LSEG Annual Total Debt USD':c.public_debt_usd,'LSEG Fiscal Period End':dateValue(c.financial_period_end),'LSEG Fiscal Period':c.financial_period,'LSEG Currency':c.financial_currency,'WRDS Ratio Date':c['Provided WRDS Ratio Date'],'WRDS EV Multiple':c['Provided WRDS EV Multiple'],'WRDS Net Margin':c['Provided WRDS Net Margin'],'WRDS Ratio Source Link':c['WRDS Source Link'],'Financial Use Note':c['Financial Use Note']})));
table('FF49 Context',await read('FF49_Context'));table('Weights',weights);
const pf=(await read('Public_Facets')).filter(r=>r['Evidence Status']!=='UNKNOWN');const ps=table('Public Facets',pf);ps.getRangeByIndexes(1,0,pf.length,8).format.rowHeight=76;
function letter(i){let s='';for(i++;i;i=Math.floor((i-1)/26))s=String.fromCharCode(65+(i-1)%26)+s;return s;}
const wrow=new Map(weights.map((r,i)=>[r.facet,i+2])),scoreStart=baseCols.length,contribStart=scoreStart+positive.length;
for(let start=0;start<results.length;start+=1000){
 const chunk=results.slice(start,start+1000);
 const contrib=chunk.map((r,i)=>positive.map((w,j)=>{const row=start+i+2,score=letter(scoreStart+j)+row;return `=IF(ISNUMBER(${score}),IFERROR(${score}*'Weights'!B${wrow.get(w.facet)}/$G${row},""),"")`;}));resultSheet.getRangeByIndexes(start+1,contribStart,contrib.length,positive.length).formulas=contrib;
 const f=chunk.map((r,i)=>{const row=start+i+2,terms=positive.map((w,j)=>`IF(ISNUMBER(${letter(scoreStart+j)}${row}),'Weights'!B${wrow.get(w.facet)},0)`).join(',');return [`=SUM(${letter(contribStart)}${row}:${letter(contribStart+positive.length-1)}${row})`,`=SUM(${terms})`,`=COUNT(${letter(scoreStart)}${row}:${letter(scoreStart+positive.length-1)}${row})`];});resultSheet.getRangeByIndexes(start+1,5,f.length,3).formulas=f;
}
console.log('Recalculating contribution formulas');wb.recalculate();
console.log((await wb.inspect({kind:'table',range:"'Comp Results'!A1:H4",tableMaxRows:4,tableMaxCols:8,maxChars:1500})).ndjson);
await fs.mkdir(path.join(dir,'previews'),{recursive:true});
for(const {name} of specs){const range=name==='Read Me'?'A1:B7':name==='Public Facets'?'C1:G3':name==='Target Facets'?'C1:G3':name==='Public Candidate Data'?'A1:G4':name==='Comp Results'?'A1:I4':name==='Weights'?'A1:D4':'A1:F4';const img=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(path.join(dir,'previews',name.replaceAll(' ','_')+'.png'),new Uint8Array(await img.arrayBuffer()));console.log('Rendered',name);}
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(dir,'Global_Public_Comps_560_DRAFT.xlsx'));console.log('SAVED',JSON.stringify(specs));
