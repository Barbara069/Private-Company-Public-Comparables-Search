import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const p=new URL('.',import.meta.url).pathname;
const d=JSON.parse(await fs.readFile(p+'prepared.json','utf8'));
const input=JSON.parse(await fs.readFile(p+'input_companies.json','utf8'));
const history=JSON.parse(await fs.readFile(p+'history_2010_2025.json','utf8'));
const sourceMetadata=Object.fromEntries((await fs.readFile(p+'variable_metadata.tsv','utf8')).trim().split('\n').map(line=>{const [code,type,description]=line.split('\t');return [code,{type,description}];}));
const localMetadata={
 company_id:['Char','Company ID from original Excel'],company_name:['Char','Company full name from original Excel'],input_ticker:['Char','Ticker from original Excel'],exchange:['Char','Exchange from original Excel'],
 website:['Char','Company website from original Excel'],country_name:['Char','Country name from original Excel'],country_iso3:['Char','Country ISO3 code from original Excel'],sic2_code:['Char','2-digit SIC code from original Excel'],sic3_code:['Char','3-digit SIC code from original Excel'],sic4_code:['Char','4-digit SIC code from original Excel'],primary_sic_industry:['Char','Primary SIC industry description from original Excel'],
 status:['Char','Ratio coverage status'],public_date:['Date','WRDS ratio observation date'],adate:['Date','Annual accounting date'],qdate:['Date','Quarterly accounting date'],available_ratios:['Int','Number of nonmissing ratio fields in this observation'],mapping_method:['Char','Company matching method'],warnings:['Char','Mapping and comparability warnings'],wrds_ticker:['Char','Ticker returned by WRDS'],first_month:['Date','Earliest matched historical month'],last_month:['Date','Latest matched historical month'],history_rows:['Int','Number of matched historical records'],history_rows_10y:['Int','Ratio observations during 2016-2025'],first_month_10y:['Date','First ratio month during 2016-2025'],last_month_10y:['Date','Last ratio month during 2016-2025']
};
const inputMap=new Map(input.map(r=>[r.IQ_COMPANY_ID,r]));
const addedKeys=['website','country_name','country_iso3','sic2_code','sic3_code','sic4_code','primary_sic_industry'];
for(const rows of [d.latest,d.coverage])for(const row of rows){
 const r=inputMap.get(row.company_id);
 for(const k of addedKeys){const value=r['target_'+(k==='website'?'ciq_website':k)];row[k]=k.startsWith('sic')?String(Math.trunc(value)).padStart(k==='sic2_code'?2:k==='sic3_code'?3:4,'0'):value;}
}
function metadata(k){return sourceMetadata[k.toLowerCase()]??{type:localMetadata[k]?.[0]??'Char',description:localMetadata[k]?.[1]??k};}
const historyById=new Map();
for(const r of history){const a=historyById.get(r.input_company_id)??[];a.push(r);historyById.set(r.input_company_id,a);}
for(const r of d.coverage){const a=historyById.get(r.company_id)??[];r.history_rows_2010_2025=a.length;r.first_month_2010_2025=a[0]?.public_date??null;r.last_month_2010_2025=a.at(-1)?.public_date??null;}
localMetadata.history_rows_2010_2025=['Int','Ratio observations during 2010-2025'];
localMetadata.first_month_2010_2025=['Date','First ratio month during 2010-2025'];
localMetadata.last_month_2010_2025=['Date','Last ratio month during 2010-2025'];
for(const rows of [d.latest,d.coverage])for(const r of rows){
 if(r.mapping_method==='No returned match')r.mapping_method='No ratio record returned; does not mean company is absent from Compustat';
 if(r.input_ticker==='DOX'){r.mapping_method='Company verified: GVKEY 111880; ratio query returned zero rows';r.warnings='DOX found in Compustat company lookup. Separate Financial Ratios query 11811675 returned No Results for 2016-2025.';}
 if(r.status==='NOT RETURNED / UNRESOLVED'){r.status='NA';if(rows===d.latest)for(const k of d.ratios)r[k]='NA';}
}
const w=Workbook.create();
function table(name,rows,headers){
 const s=w.worksheets.add(name);s.showGridLines=false;
 const enriched=name!=='ReadMe';
 const large=name==='History2010_2025';
 const dateKeys=['public_date','adate','qdate','first_month','last_month','first_month_2010_2025','last_month_2010_2025'];
 const offset=enriched?3:1;
 const vals=[...(enriched?[headers.map(k=>metadata(k).description),headers.map(k=>metadata(k).type),headers]:[headers]),...rows.map(r=>headers.map(k=>dateKeys.includes(k)&&r[k]?new Date(r[k]+'T00:00:00Z'):r[k]??null))];
 s.getRangeByIndexes(0,0,vals.length,headers.length).values=vals;
 const all=s.getRangeByIndexes(0,0,large?3:vals.length,headers.length);all.format.font={name:'Arial',size:10};all.format.columnWidth=16;if(!large)all.format.rowHeight=21;
 const h=s.getRangeByIndexes(0,0,offset,headers.length);h.format.fill='#17365D';h.format.font={name:'Arial',bold:true,color:'#FFFFFF'};h.format.wrapText=true;h.format.verticalAlignment='center';
 s.getRangeByIndexes(0,0,1,headers.length).format.rowHeight=enriched?100:38;
 if(enriched){s.getRangeByIndexes(1,0,1,headers.length).format.rowHeight=24;s.getRangeByIndexes(1,0,1,headers.length).format.fill='#DCE6F1';s.getRangeByIndexes(1,0,1,headers.length).format.font.color='#17365D';s.getRangeByIndexes(2,0,1,headers.length).format.rowHeight=32;}
 if(!large)s.tables.add(s.getRangeByIndexes(offset-1,0,rows.length+1,headers.length),true,name+'Table');
 s.freezePanes.freezeRows(offset);s.freezePanes.freezeColumns(3);
 s.getRange('B:B').format.columnWidth=38;
 for(const k of dateKeys){if(headers.includes(k))s.getRangeByIndexes(offset,headers.indexOf(k),rows.length,1).setNumberFormat('yyyy-mm-dd');}
 if(!large)for(const k of ['gvkey','CUSIP','permno','sic2_code','sic3_code','sic4_code']){if(headers.includes(k))s.getRangeByIndexes(offset,headers.indexOf(k),rows.length,1).setNumberFormat('@');}
 if(enriched)for(const k of ['primary_sic_industry','website'])if(headers.includes(k))s.getRangeByIndexes(0,headers.indexOf(k),rows.length+offset,1).format.columnWidth=k==='website'?30:48;
 return s;
}
const notes=[
 ['WRDS financial ratios — 560-company coverage','Retrieved 2026-10-20; original workbook unchanged.'],
 ['Latest source month','2025-12-31; requested through 2026-10-20. No 2026 records returned.'],
 ['Companies at latest month',d.summary.status_counts['LATEST SOURCE MONTH']],
 ['Companies with historical-only observations',d.summary.status_counts['HISTORICAL ONLY']],
 ['Not returned / unresolved',d.summary.status_counts['NOT RETURNED / UNRESOLVED']],
 ['Ratio fields',69],['Matched historical rows',d.summary.historical_rows],
 ['History range','History2010_2025 contains all 73,299 matched monthly observations from 2010-01-31 through 2025-12-31, covering 501 companies. Earlier records are retained as requested.'],
 ['Matching','Exact ticker unless company-name/GVKEY lookup is indicated. Exact ticker matches are not independent company-name validation.'],
 ['Unresolved rows','NA means no accepted ratio records returned. Missing ratio observations are not treated as zero. A missing record does not establish that the company is delisted.'],
 ['Snapshot timing','One latest available firm observation per company, not a mixture of dates. Historical-only rows are explicitly flagged.'],
 ['Share classes','CRD.B mapped to firm primary CRD.A. Per-share valuation ratios can differ by class; see warnings.'],
 ['Dividend yield','divyield converted from WRDS percent text to decimal fraction; displayed as percentage. Other ratios retain source units.'],
 ['Source fields','WRDS codes preserved. adate = annual accounting date; qdate = quarterly accounting date; public_date = ratio observation date. Do not assume this is a fully point-in-time archive.'],
 ['EV multiple','evm is the WRDS enterprise multiple field. It is not labeled or substituted as vendor-adjusted EBITDA.'],
 ['Raw source queries','11811611, 11811637, 11811640, 11811642; raw CSV exports retained beside this file.'],
 ['Excluded supplemental export','WRDS_ratios_supplement_raw.csv contains class-symbol parsing candidates; not blindly merged.'],
 ['WRDS source','https://wrds-www.wharton.upenn.edu/pages/get-data/financial-ratios-suite-wrds/financial-ratios/financial-ratios-firm-level-by-wrds-beta/'],
 ['Input','company list for interns.xlsx — 560 company rows.'],
 ['Caution','Source rounding and missing fields are preserved; 69 requested ratios does not mean every firm has all 69 values.'],
 ['Company metadata','Company names, SIC 2/3/4, SIC industry, country, website and exchange: all 560 populated from the original company Excel. This is an undated input snapshot, not historical WRDS industry classification.'],
 ['Column headers','Row 1: description. Row 2: data type. Row 3: original variable name. Row 4 onward: data. WRDS source types retained for 73 fields. Local metadata types assigned by preparer. Identifier values stored as text to preserve leading zeros.'],
 ['Official variable dictionary','WRDS Financial Ratios Firm Level, Variable Descriptions tab. finratiofirm. Updated 2026-02-16. Dates are formatted as Excel dates. Float means a decimal numeric value; Char means text; Int means integer.'],
 ['Saved Codes','EBITDA Interns 560 - Original Tickers - 20261020. WRDS confirmed successful creation on 2026-10-20. Contains the original 560 ticker entries, not company-name strings.'],
 ['Missing ratio record vs missing company','A missing ratio row does not establish that a company cannot be found in Compustat. DOX/Amdocs lookup verified GVKEY 111880. Separate ratio query 11811675 for 2016-2025 returned No Results Found.'],
 ['Published sample filters','WRDS published SAS program uses security/country filters and CRSP/Compustat links. It includes a USA primary-security restriction and a CRSP common-share-code filter (10,11). These can restrict coverage relative to the full company lookup. Specific causes for remaining missing firms have not been individually established.'],
 ['Official methodology','https://wrds-www.wharton.upenn.edu/pages/support/manuals-and-overviews/wrds-financial-ratios/financial-ratios-sas-code/'],
 ['Historical deduplication','18 duplicate company-month rows differed only in whether the ticker was populated. Ratios and other identifiers were identical. Kept the row with the ticker.'],
 ['Historical coverage','501 companies have at least one matched ratio observation in 2010-2025. 59 have no accepted ratio match and are marked NA. Coverage tab shows record counts and date ranges. Original current company names and SIC are static input metadata. Historical identity has not been independently verified for exact-ticker matches.']
];
const n=table('ReadMe',notes.map(r=>({Topic:r[0],Details:r[1]})),['Topic','Details']);n.freezePanes.unfreeze();n.getRange('A:A').format.columnWidth=43;n.getRange('B:B').format.columnWidth=105;n.getRange(`B2:B${notes.length+1}`).format.wrapText=true;n.getRange(`A2:B${notes.length+1}`).format.rowHeight=42;
const keys=['company_id','company_name','input_ticker','exchange',...addedKeys,'status','public_date','Ticker','gvkey','permno','CUSIP','adate','qdate','available_ratios',...d.ratios,'mapping_method','warnings'];
const s=table('LatestRatios',d.latest,keys);
for(const k of d.ratios){const c=keys.indexOf(k);s.getRangeByIndexes(3,c,560,1).setNumberFormat(k==='divyield'?'0.00%':'0.000');}
s.getRangeByIndexes(0,keys.indexOf('status'),561,1).format.columnWidth=30;
const coverageKeys=['company_id','company_name','input_ticker','exchange',...addedKeys,...Object.keys(d.coverage[0]).filter(k=>!['company_id','company_name','input_ticker','exchange',...addedKeys].includes(k))];
const c=table('Coverage',d.coverage,coverageKeys);c.getRangeByIndexes(0,coverageKeys.indexOf('status'),561,1).format.columnWidth=30;
console.log('Building 2010-2025 history',history.length);
const histRows=history.map(r=>({company_id:r.input_company_id,company_name:inputMap.get(r.input_company_id).target_company_name,input_ticker:r.input_ticker,...r}));
const histKeys=['company_id','company_name','input_ticker','public_date','gvkey','permno','Ticker','CUSIP','adate','qdate',...d.ratios];
const hs=table('History2010_2025',histRows,histKeys);
hs.getRangeByIndexes(3,histKeys.indexOf('divyield'),history.length,1).setNumberFormat('0.00%');
console.log('History built. Exporting.');
w.recalculate();
console.log((await w.inspect({kind:'region',sheetId:'LatestRatios',range:'A1:H5',maxChars:1800,tableMaxCols:8})).ndjson);
await (await SpreadsheetFile.exportXlsx(w)).save(p+'WRDS_Financial_Ratios_560.xlsx');
for(const name of ['ReadMe','LatestRatios','Coverage','History2010_2025']){
 const b=await w.render({sheetName:name,range:name==='ReadMe'?'A1:B9':'A1:H10',scale:1,format:'png'});
 await fs.writeFile(p+name+'_preview.png',new Uint8Array(await b.arrayBuffer()));
}
console.log('Exported and rendered 3 sheets.');
