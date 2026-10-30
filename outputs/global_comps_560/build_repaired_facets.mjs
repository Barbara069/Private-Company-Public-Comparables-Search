import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.dirname(new URL(import.meta.url).pathname),dir=path.join(root,'repaired_facets_20261028');
const read=async n=>JSON.parse(await fs.readFile(path.join(dir,n+'.json'),'utf8')),summary=await read('repair_summary');
const wb=Workbook.create(),manifest=[];
function table(name,rows,cols=Object.keys(rows[0]||{}),height=42){
 const s=wb.worksheets.add(name);s.showGridLines=false;
 s.getRangeByIndexes(0,0,1,cols.length).values=[cols];
 for(let i=0;i<rows.length;i+=2000)s.getRangeByIndexes(i+1,0,Math.min(2000,rows.length-i),cols.length).values=rows.slice(i,i+2000).map(r=>cols.map(k=>{const v=r[k]??null;return typeof v==='string'?v.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g,'').slice(0,32000):v;}));
 const u=s.getRangeByIndexes(0,0,rows.length+1,cols.length);u.format.font={name:'Arial',size:10};u.format.verticalAlignment='top';u.format.rowHeight=height;u.format.columnWidth=19;
 for(const [i,k] of cols.entries()){
  const c=s.getRangeByIndexes(0,i,rows.length+1,1);
  if(/Name|Facet/.test(k))c.format.columnWidth=29;
  if(/Action|Status|Scope/.test(k)){c.format.columnWidth=45;c.format.wrapText=true;}
  if(/Value|Reason|Text|Meaning|Detail|Observation/.test(k)){c.format.columnWidth=75;c.format.wrapText=true;}
  if(/Link|Evidence IDs|Source Field/.test(k)){c.format.columnWidth=55;c.format.wrapText=true;}
  if(/Similarity|Coverage|Contribution/.test(k))c.setNumberFormat('0.00');
  if(/Source Date|Fact As Of Date/.test(k)){c.format.columnWidth=35;c.format.wrapText=true;}
 }
 const header=s.getRangeByIndexes(0,0,1,cols.length);header.format.fill='#263C54';header.format.font={name:'Arial',size:10,color:'#FFFFFF',bold:true};header.format.wrapText=true;header.format.horizontalAlignment='center';header.format.rowHeight=66;
 s.freezePanes.freezeRows(1);s.freezePanes.freezeColumns(Math.min(3,cols.length));
 if(rows.length)s.tables.add(s.getRangeByIndexes(0,0,rows.length+1,cols.length),true,name.replace(/[^A-Za-z]/g,'')+'Table');
 if(height>=80||cols.includes('Corrected Value'))for(let i=0;i<rows.length;i++){const longest=Math.max(...cols.filter(k=>/Value|Reason|Text|Detail|Observation/.test(k)).map(k=>String(rows[i][k]??'').length),0);const needed=Math.min(409,Math.max(height,Math.ceil(longest/70)*13+12));if(needed>height)s.getRangeByIndexes(i+1,0,1,cols.length).format.rowHeight=needed;}
 manifest.push({name,rows:rows.length,columns:cols.length});console.log('Prepared',name,rows.length);return s;
}
const human=[
 {Item:'Delivery',Value:'Applied source/facet repairs and recalculated scores. Original files are preserved.'},
 {Item:'Original conflict facets processed',Value:summary.flagged_facets_processed},
 ...Object.entries(summary.flagged_dispositions).map(([k,v])=>({Item:k,Value:v})),
 {Item:'Still unresolved',Value:'Quarantined values are NULL and excluded from scoring. Processing every flag does not mean every disagreement has been factually resolved.'},
 {Item:'Automatic re-extraction',Value:'Re-extracted excerpts pass sharper text checks, but are not individually verified facts. See Human Reviewed Fact for the limited primary-source review subset.'},
 {Item:'Existing pairs recalculated',Value:summary.rescored_existing_pairs},
 {Item:'Pair scores changed',Value:summary.pairs_with_changed_scores},
 {Item:'Pairs withheld for missing/conflicted core evidence',Value:summary.pairs_withheld_due_to_core_evidence},
 {Item:'Ranking scope',Value:summary.ranking_scope},
 {Item:'Target restriction',Value:'Website evidence only. External target references remain diagnostic. No hidden target SIC or financial descriptions are used.'},
 {Item:'Whole-company eligibility',Value:'Repaired scores are uncalibrated draft similarity. Segment revenue shares and whole-company comparable eligibility are still not validated. No forecasts or automatic valuation aggregation.'}
];const summarySheet=table('Summary',human,['Item','Value'],55);summarySheet.getRangeByIndexes(0,0,human.length+1,1).format.columnWidth=65;summarySheet.getRangeByIndexes(0,0,human.length+1,1).format.wrapText=true;summarySheet.getRangeByIndexes(0,1,human.length+1,1).format.columnWidth=110;
const comps=await read('Corrected_Comp_Results');
table('Updated Comps',comps,['Target ID','Target Name','Rank','Candidate RIC','Candidate Name','Similarity Percent','Prior Similarity Percent','Prior Rank','Weighted Evidence Coverage','Prior Weighted Evidence Coverage','Scored Facets','Status','Repaired Facet Score Rows','Ranking Scope','Candidate Source','Source Text','Source Link','Segment Warning'],66);
const all=await read('Corrected_Facets'),cols=['Entity ID','Company Name','Facet','Corrected Value','Eligible For Scoring','Repair Action','Repair Reason','Source Type','Source Link','Source Date','Fact As Of Date','Scope','Evidence IDs','Human Reviewed Fact','Unresolved Conflict Pair IDs'];
table('Target Facets',all.filter(x=>x['Entity Role']==='TARGET'),cols,72);
table('Public Facets',all.filter(x=>x['Entity Role']==='PUBLIC'),cols,72);
const conflict=await read('Conflict_Dispositions');
table('Conflict Repairs',conflict,['Entity Role','Entity ID','Company Name','Facet','Before Value','Before Source Link','Corrected Value','Source Observation Not Admitted','Observation Source Link','Repair Action','Repair Reason','Eligible For Scoring','Source Type','Source Link','Source Date','Fact As Of Date','Scope','Human Reviewed Fact','Unresolved Conflict Pair IDs'],100);
const reviewed=all.filter(x=>x['Human Reviewed Fact']);
table('Verified Corrections',reviewed,['Company Name','Facet','Before Value','Before Source Link','Corrected Value','Source Type','Source Link','Source Date','Fact As Of Date','Scope','Repair Reason','Reviewed At'],100);
const method=[
 {Topic:'What changed',Detail:'Known subject and facet-assignment errors are replaced or removed. Sharper matching removes feedback/fee confusion, privacy-consent text, biographies, navigation and financial taxonomy markup. Invalid replacements are withdrawn; a valid original excerpt can be restored.'},
 {Topic:'Unresolved conflicts',Detail:'A source preference or high NLI score is not proof of truth. Remaining unresolved fields are NULL in Corrected Value, with their source observations and pair IDs retained for review. Missing is not a zero or a perfect match.'},
 {Topic:'Scope and time',Detail:'Customer stories are not parent-company attributes. Business origin, legal incorporation and reincorporation are separate events. Source publication dates, fact periods and review dates remain separate. Multi-business firms require segment-level eligibility review.'},
 {Topic:'Scores',Detail:'Original proposed weights are retained. Changed supported text/category facets are recalculated; quarantined values have no score or weight contribution. Missing core business evidence withholds the pair total. Partial observed-facet scores are diagnostic only.'},
 {Topic:'Reranking',Detail:'Reordering is within each target’s previous ten candidates only. This repair is not a rerun of global candidate discovery. Similarity percentages are uncalibrated model scores, not probabilities or valuation accuracy.'},
 {Topic:'Complete data',Detail:'The CSV package contains all corrected facets, before/after repair records, all 87,840 score contributions, source excerpts and conflict dispositions. The Excel displays the updated results and review views.'},
 {Topic:'Unchanged baseline',Detail:'RETAINED_BASELINE_NOT_REVERIFIED means the original observation remains as an unverified baseline. It does not mean the company/facet was independently fact-checked.'}
];table('Method',method,['Topic','Detail'],100);
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Verified Corrections!A1:F3',tableMaxRows:3,tableMaxCols:6,maxChars:1600})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:10},maxChars:700})).ndjson);
await fs.mkdir(path.join(dir,'previews'),{recursive:true});
for(const {name}of manifest){const range=name==='Summary'?'A1:B6':name==='Verified Corrections'?'A1:D3':name==='Conflict Repairs'?'C1:G3':name==='Method'?'A1:B4':name==='Updated Comps'?'A1:H4':'A1:F4';const b=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(path.join(dir,'previews',name.replaceAll(' ','_')+'.png'),new Uint8Array(await b.arrayBuffer()));console.log('Rendered',name);}
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(dir,'Repaired_Facets_and_Updated_Comps.xlsx'));
await fs.writeFile(path.join(dir,'workbook_manifest.json'),JSON.stringify(manifest,null,2));console.log('Saved repaired workbook');
