import json,pandas as pd
from pathlib import Path
p=Path(__file__).parent
d=pd.read_csv(p/'matched_historical_ratios.csv',dtype={'input_company_id':str,'input_ticker':str,'gvkey':str,'permno':str,'Ticker':str,'CUSIP':str})
d=d[d.public_date.between('2010-01-01','2025-12-31')].copy()
# Four join duplicates differ only because one record has a missing ticker.
dup=d[d.duplicated(['input_company_id','public_date'],False)]
other=[c for c in d if c not in ['Ticker','source_file']]
for _,g in dup.groupby(['input_company_id','public_date']):
 assert len(g[other].drop_duplicates())==1,'Conflicting monthly records require review'
d['_ticker_present']=d.Ticker.notna()
d=d.sort_values('_ticker_present',ascending=False).drop_duplicates(['input_company_id','public_date']).drop(columns='_ticker_present')
d=d.sort_values(['input_company_id','public_date'])
ratios=json.loads((p/'prepared.json').read_text())['ratios']
d['divyield']=pd.to_numeric(d.divyield.str.rstrip('%'),errors='coerce')/100
d.to_csv(p/'WRDS_Ratios_History_2010_2025.csv',index=False)
(p/'history_2010_2025.json').write_text(d.where(d.notna(),None).to_json(orient='records'))
print(json.dumps({'rows':len(d),'companies':d.input_company_id.nunique(),'months':d.public_date.nunique(),'first':d.public_date.min(),'last':d.public_date.max(),'ratio_fields':len(ratios)},indent=2))
