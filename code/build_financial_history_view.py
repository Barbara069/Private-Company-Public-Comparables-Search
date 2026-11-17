"""Build exact-identifier history view from existing permitted-source master CSV.
No forecast consumes this full-public research history.
"""
import csv,gzip,json,math
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT.parent/'Research_Data.csv.gz'
csv.field_size_limit(100_000_000)
catalog=json.load(gzip.open(ROOT/'website/data/research_catalog.json.gz','rt'))
by_id={i:c['key'] for c in catalog['companies'] for i in [c.get('id'),*c.get('original_target_ids',[])] if i}
fields={'revenue':'TR.TOTALREVENUE','ebitda':'TR.EBITDA','ebit':'TR.EBIT','net_income':'TR.NETINCOME','debt':'TR.TOTALDEBT','cash':'TR.CASHANDSTINVESTMENTS','operating_cash_flow':'TR.CASHFROMOPERATINGACTIVITIES','capex':'TR.CAPITALEXPENDITURES','free_cash_flow':'TR.FREECASHFLOW'}
def num(v):
 try:
  n=float(v);return n if math.isfinite(n) else None
 except (TypeError,ValueError):return None
rows=defaultdict(dict)
snapshots=defaultdict(list)
with gzip.open(MASTER,'rt') as f:
 for x in csv.DictReader(f):
  if x['dataset'] not in ['LSEG_annual_five_years','LSEG_ltm','LSEG_latest_quarter']:continue
  d=json.loads(x['record_json']);key=by_id.get(d.get('Company ID'));date=d.get('TR.TOTALREVENUE.DATE','');period=d.get('TR.TOTALREVENUE.FPERIOD','')
  if not key or not date:continue
  row={'period':period,'period_end':date,'currency':d.get('TR.TOTALREVENUE.CURRENCY') or 'UNKNOWN','units':'provider currency units, displayed in millions','source':'LSEG Workspace Data Library','source_url':d.get('Source Link') or x['source_url'],'retrieved_at':d.get('Retrieved At UTC'),'field_codes':fields,'values':{k:num(d.get(v)) for k,v in fields.items()}}
  if x['dataset']=='LSEG_annual_five_years':rows[key][date]=row
  elif date.startswith('2026'):
   row['basis']='Trailing twelve months (not FY2026)' if x['dataset']=='LSEG_ltm' else 'Single fiscal quarter (not YTD or full year)'
   snapshots[key].append(row)
out={'snapshots_2026':dict(snapshots),'scope':'Full-public historical research only; never consumed by illustrative or pseudo-private forecast calculations. Existing LSEG annual five-year snapshot; not refreshed today. Values retain provider definitions; no cross-provider reconciliation claimed.','companies':{k:sorted(v.values(),key=lambda r:r['period_end'])[-5:] for k,v in rows.items()}}
with gzip.GzipFile(filename=str(ROOT/'website/data/financial_history.json.gz'),mode='wb',mtime=0) as f:f.write(json.dumps(out,separators=(',',':')).encode())
print(json.dumps({'companies':len(rows),'annual_rows':sum(len(v) for v in out['companies'].values()),'wendy':out['companies'].get(by_id.get('IQ23557'))},indent=2))
