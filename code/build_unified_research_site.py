from pathlib import Path
import gzip,json,re,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[1];D=ROOT/'outputs/public_research_website'
old=(D/'index.html').read_text();backup=P/'unified_research/previous_role_based_site.html'
if not backup.exists():backup.parent.mkdir(exist_ok=True);backup.write_text(old)
css=re.search(r'<style[^>]*>(.*?)</style>',old,re.S).group(1)
css+='\n.comparison-table{min-width:1500px}.comparison-table td:nth-child(2),.comparison-table td:nth-child(3){min-width:300px}.evidence{border-left:3px solid #d2e4e4;padding:0 14px;margin:16px 0}.evidence .value{margin-bottom:8px}.source{line-height:1.6}.source-discrepancy-note{font-size:13px;color:#59676d}#researchNote{margin-top:8px;line-height:1.6}#universeNote{margin-top:8px;line-height:1.5;color:#e0efee}\n'
match_groups={}
for path in (D/'data/matches').glob('*.json.gz'):
 with gzip.open(path,'rt') as f:rows=json.load(f)
 for tid in rows:match_groups[tid]='matches/'+path.name.replace('.json.gz','')
summary=json.loads((P/'entity_identity_review/summary.json').read_text())
head=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Barbara069 / Private Company Comparables Research</title><style>{css}</style></head><body>
<header><select id="languageSwitch" aria-label="Language / 语言" style="float:right"><option value="en">English</option><option value="zh">中文</option></select><h1>Barbara069 / Private Company Comparables Research</h1><p id="repositoryLink" style="margin:10px 0"><a href="https://github.com/Barbara069/Private-Company-Public-Comparables-Search" target="_blank" rel="noopener noreferrer" style="color:#fff;text-decoration:underline;font-weight:600">GitHub · Research code &amp; methodology</a></p><p id="researchNote"></p><p id="universeNote">Universe snapshot: {summary['economic_company_groups_including_unresolved']:,} public economic groups, including 3 unresolved issuer IDs. Original input files and complete CSVs are stored separately from this public viewer.</p></header>
<div class="layout"><aside><strong id="findCompanyLabel">Find a company</strong><input id="companySearch" aria-label="Search companies" placeholder="Company name, ticker or ID"><select id="role" aria-label="Company list"><option value="TARGET">Original 560 companies</option><option value="PUBLIC">Global public universe</option><option value="ALL">All research companies</option></select><span id="companyCount" class="small"></span><div id="companies" class="companies"></div><button id="moreCompanies" hidden>Show 100 more</button></aside>
<section class="main"><nav>'''+''.join(f'<button data-tab="{tab}">{label}</button>' for tab,label in [('comps','Public Comps'),('facets','General facet'),('industry','Industry facets'),('segments','Business segments'),('growth','Growth &amp; Revenue Forecast'),('sources','Evidence sources')])+'''</nav><div id="companyTitle"></div><div id="content"><p>Loading company research…</p></div></section></div>'''
js='const COMPARISON_GROUPS='+json.dumps(match_groups)+';\n'+(P/'unified_research_app.js').read_text()
html=head+'<script>\n'+js+'\n</script></body></html>';(D/'index.html').write_text(html)
temp=Path('/tmp/unified_research_app_check.js');temp.write_text(js);subprocess.run(['node','--check',str(temp)],check=True)
print('Unified site: one profile and one research view per company; restriction is confined to Public Comps.')
