/* Regression checks: company identity must gate embedded forecasts. */
const fs=require('fs'),path=require('path'),zlib=require('zlib'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const bundle=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'website/data/private_forecast_prototype.json.gz'))));
const script=fs.readFileSync(path.join(__dirname,'growth_view_app.js'),'utf8');
const catalog=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'website/data/research_catalog.json.gz'))));
const forecastData=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'website/data/target_growth_forecasts.json.gz'))));
const context={forecastData,sourceHTML:s=>String(s?.url||''),catalog,window:{addEventListener(){}},word:(en)=>en,esc:v=>String(v??''),bundle,assert};
vm.createContext(context);vm.runInContext(script,context);
vm.runInContext(`
targetForecastCache=forecastData;
const wendy=catalog.companies.find(c=>c.id==='IQ23557'),pcty=catalog.companies.find(c=>c.id==='IQ254957567');
for(const company of [wendy,pcty]){
 const html=selectedForecastHTML(company,bundle);
 assert(!html.includes('<iframe'),'Public target received private prototype');
 assert(html.includes('Peer + Website Growth Forecast'),'Missing company-specific forecast');
 assert(html.includes('<svg')&&html.includes('illustrationScenario'),'Interactive chart missing');
 assert(!html.includes('assume 5% annual growth'),'Universal curve still present');
}
for(const company of catalog.companies){assert(!selectedForecastHTML(company,bundle).includes('<iframe'),'Public research company received the private prototype');}
for(const row of bundle.readiness){assert.equal(selectedForecastHTML({key:row.target_id,name:row.company},bundle).includes('<iframe'),row.target_id===bundle.config.target.id,'Private pilot company binding mismatch');}
const f=forecastData.targets.IQ23557,base=forecastScenarioRows(f,'base',.20,12,.10);
assert.equal(base[0].year,2026);assert.equal(base[5].year,2031);
assert.notEqual(base[5].revenue,127.62815625,'Old universal 5% curve retained');
assert.equal(base[0].multiple,10.8);assert.equal(forecastScenarioRows(f,'base')[5].ev,null);
assert.notEqual(peerWebsiteChartHTML(f,'base'),peerWebsiteChartHTML(f,'bull'));
const own=selectedForecastHTML({key:'GC_NETCHEX',name:'Netchex'},bundle);
assert(own.includes('company=GC_NETCHEX')&&own.includes('<iframe'),'Matching forecast not shown inline');
const mixed=JSON.parse(JSON.stringify(bundle));mixed.results.forecasts[0].target_id='WRONG_COMPANY';
assert(!selectedForecastHTML({key:'GC_NETCHEX',name:'Netchex'},mixed).includes('<iframe'),'Mixed-company forecast rows accepted');
`,context);
const app=fs.readFileSync(path.join(__dirname,'website_app.js'),'utf8');
assert.equal((app.match(/async function showGrowth\(/g)||[]).length,1,'Duplicate renderer can override identity checks');
assert(!app.includes('Netchex: executed five-year indexed scenario prototype'),'Unscoped prototype link retained');
assert(app.includes("querySelectorAll?.('details')"),'Expand-by-default handler missing');
const html=fs.readFileSync(path.join(root,'website/index.html'),'utf8');
assert.equal(html.match(/<script>([\s\S]*?)<\/script>/)[1].trim(),app.trim(),'Published HTML uses stale JavaScript');
assert(html.includes('<title>Barbara069 / Private Company Comparables Research</title>'),'Website name changed');
const history=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'website/data/financial_history.json.gz'))));
assert.equal(Object.keys(history.companies).length,560);
for(const [key,rows] of Object.entries(history.companies)){assert(catalog.companies.some(c=>c.key===key),'History issuer absent from catalog');assert(rows.length<=5);assert.equal(new Set(rows.map(r=>r.period_end)).size,rows.length);}
const w=catalog.companies.find(c=>c.id==='IQ23557');assert.equal(history.companies[w.key].at(-1).values.revenue,2176891000);
assert(app.indexOf('+history+selectedForecastHTML')>0,'History must precede scenarios');
console.log('Company binding, mixed-row rejection, single renderer, expanded sections and stable website name: passed.');
