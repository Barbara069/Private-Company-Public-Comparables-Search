import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';
const root=path.dirname(new URL(import.meta.url).pathname),dir=path.join(root,'semantic_validation_20261028');
const read=async n=>JSON.parse(await fs.readFile(path.join(dir,n+'.json'),'utf8'));
const summary=await read('summary');
if(summary.pending_source_pairs)throw Error('Semantic inference is not complete.');
const wb=Workbook.create(),manifest=[];
function table(name,rows,cols=Object.keys(rows[0]||{}),height=42){
 const s=wb.worksheets.add(name);s.showGridLines=false;
 s.getRangeByIndexes(0,0,1,cols.length).values=[cols];
 for(let i=0;i<rows.length;i+=1000)s.getRangeByIndexes(i+1,0,Math.min(1000,rows.length-i),cols.length).values=rows.slice(i,i+1000).map(r=>cols.map(k=>{const v=r[k]??null;return typeof v==='string'?v.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g,'').slice(0,32000):v;}));
 const u=s.getRangeByIndexes(0,0,rows.length+1,cols.length);u.format.font={name:'Arial',size:10};u.format.verticalAlignment='top';u.format.rowHeight=height;u.format.columnWidth=20;
 const h=s.getRangeByIndexes(0,0,1,cols.length);h.format.fill='#293D55';h.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};h.format.rowHeight=62;h.format.wrapText=true;h.format.horizontalAlignment='center';
 for(const [i,k]of cols.entries()){const c=s.getRangeByIndexes(0,i,rows.length+1,1);if(/Name|Facet/.test(k))c.format.columnWidth=30;if(/Status|Verdict/.test(k)){c.format.columnWidth=48;c.format.wrapText=true;}if(/Text|Reason|Interpretation|Disposition|Value|Detail|Problem/.test(k)){c.format.columnWidth=80;c.format.wrapText=true;}if(/Boundary|Relevant Pair IDs/.test(k)){c.format.columnWidth=65;c.format.wrapText=true;}if(/Link|Source$|Verification Source/.test(k)){c.format.columnWidth=58;c.format.wrapText=true;}}
 if(height>=100)for(let i=0;i<rows.length;i++){const longest=Math.max(...cols.filter(k=>/Text|Reason|Detail|Value|Suggested Qualified/.test(k)).map(k=>String(rows[i][k]??'').length),0);s.getRangeByIndexes(i+1,0,1,cols.length).format.rowHeight=Math.min(409,Math.max(height,Math.ceil(longest/72)*13+14));}
 s.freezePanes.freezeRows(1);s.freezePanes.freezeColumns(Math.min(3,cols.length));
 if(rows.length)s.tables.add(s.getRangeByIndexes(0,0,rows.length+1,cols.length),true,name.replace(/[^A-Za-z]/g,'')+'Table');
 manifest.push({name,rows:rows.length,columns:cols.length});console.log('Prepared',name,rows.length);return s;
}
const overview=[
 {Item:'Scope',Value:'Source-to-source comparison of company facets. This does not evaluate target-to-comparable business similarity.'},
 ...Object.entries(summary).filter(([k,v])=>typeof v!=='object').map(([Item,Value])=>({Item,Value})),
 ...Object.entries(summary.pair_verdict_counts).map(([k,v])=>({Item:'Pair result: '+k,Value:v})),
 ...Object.entries(summary.facet_status_counts).map(([k,v])=>({Item:'Facet result: '+k,Value:v})),
 {Item:'Human review boundary',Value:'Selected high-priority cases were manually reviewed. Model conflict flags and unreviewed text pairs are not verified factual contradictions.'}
];
const ov=table('Summary',overview,['Item','Value'],46);ov.getRangeByIndexes(0,0,overview.length+1,1).format.columnWidth=65;ov.getRangeByIndexes(0,1,overview.length+1,1).format.columnWidth=110;
const manual=await read('Manual_Adjudications'),excluded=await read('Statement_Adjudications'),pairs=await read('Pair_Semantic_Results'),pby=new Map(pairs.map(x=>[x['Pair ID'],x])),statements=await read('Source_Statements'),sby=new Map(statements.map(x=>[x['Statement ID'],x]));
const reviewed=[...excluded.filter(x=>x.Verdict.startsWith('REVIEWED_')).map(x=>{const s=sby.get(x['Statement ID']);return {'Company Name':x['Company Name'],Facet:s.Facet,Status:x.Verdict,'Text A':s['Statement Text'],'Source A Link':s['Source Link'],'Text B':null,'Source B Link':null,Reason:x.Reason,Disposition:x.Disposition,'Record ID':x['Statement ID']};}),...manual.map(x=>{const p=pby.get(x['Pair ID']);return {'Company Name':p['Company Name'],Facet:p.Facet,Status:x.Verdict,'Text A':p['Text A'],'Source A Link':p['Source A Link'],'Text B':p['Text B'],'Source B Link':p['Source B Link'],Reason:x.Reason,Disposition:'Preserve qualified definitions. Do not overwrite original source data or rankings.','Record ID':x['Pair ID'],'Verification Source':x['Verification Source']};})];
table('Reviewed Cases',reviewed,Array.from(new Set(reviewed.flatMap(Object.keys))),150);
table('Proposed Corrections',await read('Proposed_Corrections'),undefined,130);
table('Company Coverage',await read('Company_Validation_Coverage'));
const facets=await read('Company_Facet_Validation'),cols=['Entity ID','Company Name','Facet','Validation Status','Interpretation','Usable Source Documents','Excluded Or Adjudicated Statements','Admissible Source Statements After Review','Source Pairs','Completed Pair Comparisons','Unresolved Pair Comparisons','Possible Conflict Pairs','Unavailable Original Evidence Documents','Relevant Pair IDs','Target Boundary'];
table('Target Facets',facets.filter(x=>x['Entity Role']==='TARGET'),cols,58);
table('Public Facets',facets.filter(x=>x['Entity Role']==='PUBLIC'),cols,58);
const queue=await read('Conflict_Review_Queue');table('Review Queue',queue,['Pair ID','Company Name','Facet','Verdict','Reason','Source A','Text A','Source A Link','Source A Date','Source B','Text B','Source B Link','Source B Date','Date Alignment','Event Year Difference','Shared Upstream Vendor','Manual Adjudication','Evidence A ID','Evidence B ID'],140);
const notes=[
 {Topic:'Method',Detail:'Complete keyword-retrieved source sentences were compared in both directions with cross-encoder/nli-MiniLM2-L6-H768. Original FP32 checkpoint. Labels: contradiction, entailment, neutral. This model is not trained as a financial fact verifier. Facet assignment can itself be wrong.',Source:'https://huggingface.co/cross-encoder/nli-MiniLM2-L6-H768'},
 {Topic:'Interpretation',Detail:'Entailment indicates text support. Neutral may mean complementary details or different claims. Contradiction is a review flag until entity, segment, event, dates and source context are checked. Model scores are not calibrated factual probabilities.'},
 {Topic:'Selected text coverage',Detail:'At most two complete matching sentences per source document and facet, from the first 50,000 source characters or extracted annual-report business section. This is not an every-line comparison of entire documents. Missing facet evidence remains explicit.'},
 {Topic:'Context',Detail:'Pairs beyond 384 model tokens are flagged for context review, not asserted as complete semantic verification. Non-English, blocked and missing text are not silently treated as consistent.'},
 {Topic:'Source identity and independence',Detail:'Website identity is not manually verified for every page. Repeated official pages and WRDS/Capital IQ shared upstream descriptions do not provide independent confirmation.'},
 {Topic:'Human corrections',Detail:'Wrong-subject sentences were excluded only from their affected company facet. Raw documents remain unchanged. Taxonomy markup is excluded from prose comparisons. Brand, predecessor, clinic and legal incorporation dates require separate event definitions.'},
 {Topic:'Pseudo-private targets',Detail:'Nonwebsite target source data in this audit is diagnostic only. The original selector inputs and all target/comparable scores are unchanged. No forecasting has started in this validation step.'},
 {Topic:'Detailed evidence',Detail:'The accompanying CSV ZIP includes every source statement, every pair with both selected texts and source links, facet statuses, exclusion records and manual adjudications. Evidence IDs connect to the earlier full source register. Local LSEG snapshot references identify actual API records.'}
];table('Method',notes,['Topic','Detail','Source'],110);
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Reviewed Cases!A1:F3',tableMaxRows:3,tableMaxCols:6,maxChars:1400})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:10},maxChars:800})).ndjson);
await fs.mkdir(path.join(dir,'previews'),{recursive:true});
for(const {name}of manifest){const range=name==='Summary'?'A1:B7':name==='Reviewed Cases'?'A1:E3':name==='Method'?'A1:B4':name==='Review Queue'?'B1:G3':'A1:E4';const blob=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(path.join(dir,'previews',name.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));console.log('Rendered',name);}
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(dir,'Company_Facet_Source_Validation.xlsx'));
await fs.writeFile(path.join(dir,'workbook_manifest.json'),JSON.stringify(manifest,null,2));console.log('Saved workbook');
