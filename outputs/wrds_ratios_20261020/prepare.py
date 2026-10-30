import pandas as pd, json
from pathlib import Path
p=Path(__file__).parent
inputs=json.loads((p/'input_companies.json').read_text())
files=['WRDS_ratios_raw.csv','WRDS_ratios_missing_retry_raw.csv','WRDS_ratios_gvkey_raw.csv','WRDS_ratios_renamed_raw.csv']
frames=[]
for f in files:
 d=pd.read_csv(p/f,dtype={'gvkey':str,'permno':str,'Ticker':str,'CUSIP':str}); d['source_file']=f;frames.append(d)
d=pd.concat(frames,ignore_index=True).drop_duplicates(subset=list(frames[0].columns[:-1]))
ids=['gvkey','permno','adate','qdate','public_date','Ticker','CUSIP']
ratios=[c for c in frames[0] if c not in ids+['source_file']]
assert len(ratios)==69
overrides=dict(zip(['ARTN.A','BATR.K','CRD.B','FWON.K','IMKT.A','SENE.A','UONE.K','QVCG.A','ACH','CVSA','OPLN','WFRD'],['017341','027186','003581','027187','012972','008582','120301','174147','008213','003905','183581','004367']))
d.gvkey=d.gvkey.str.zfill(6)
latest=[];coverage=[];hist=[]
for i,c in enumerate(inputs,1):
 t=str(c['target_ciq_ticker']); t=t[:-2] if t.endswith('.0') else t
 x=d[d.gvkey.eq(overrides[t])] if t in overrides else d[d.Ticker.eq(t)]
 method='Verified company-name/GVKEY lookup' if t in overrides else 'Exact ticker; name not independently verified'
 warnings=[];chosen=None
 if len(x):
  date=x.public_date.max(); z=x[x.public_date.eq(date)]
  if z.gvkey.nunique()==1:
   g=z.gvkey.iloc[0]; x=d[d.gvkey.eq(g)]; date=x.public_date.max(); z=x[x.public_date.eq(date)]
   if len(z.drop_duplicates(subset=ids))==1: chosen=z.iloc[0]
   else: warnings.append('Multiple securities at latest firm date; candidate rows retained')
  else: warnings.append('Multiple firm identities at latest ticker date')
  if chosen is not None:
   h=x.copy();h.insert(0,'input_ticker',t);h.insert(0,'input_company_id',c['IQ_COMPANY_ID']);hist.append(h)
  if x.gvkey.nunique()>1:warnings.append('Historical ticker reuse / multiple GVKEYs')
 if t=='CRD.B':warnings.append('Requested B class mapped to firm primary A class; per-share ratios may differ')
 if t=='WFRD':warnings.append('Restructuring history; verify comparability across periods')
 status='NOT RETURNED / UNRESOLVED' if chosen is None else ('LATEST SOURCE MONTH' if chosen.public_date=='2025-12-31' else 'HISTORICAL ONLY')
 base={'company_id':c['IQ_COMPANY_ID'],'company_name':c['target_company_name'],'input_ticker':t,'exchange':c['target_ciq_exchange'],'status':status}
 row={**base,**{k:None for k in ids+ratios}}
 if chosen is not None:
  row.update({k:chosen[k] for k in ids+ratios})
  if isinstance(row['divyield'],str):row['divyield']=float(row['divyield'].replace('%',''))/100
 row['available_ratios']=sum(pd.notna(row[r]) for r in ratios)
 row['mapping_method']=method if len(x) else 'No returned match'
 row['warnings']='; '.join(warnings)
 latest.append(row)
 coverage.append({**base,'wrds_ticker':None if chosen is None else chosen.Ticker,'gvkey':None if chosen is None else chosen.gvkey,'first_month':None if not len(x) else x.public_date.min(),'last_month':None if not len(x) else x.public_date.max(),'history_rows':len(x),'available_ratios':row['available_ratios'],'mapping_method':row['mapping_method'],'warnings':row['warnings']})
L=pd.DataFrame(latest); C=pd.DataFrame(coverage)
L.to_csv(p/'latest_ratios_560.csv',index=False);C.to_csv(p/'coverage_560.csv',index=False)
pd.concat(hist,ignore_index=True).to_csv(p/'matched_historical_ratios.csv',index=False)
def clean(o):
 if isinstance(o,dict):return {k:clean(v) for k,v in o.items()}
 if isinstance(o,list):return [clean(v) for v in o]
 if pd.isna(o):return None
 return o.item() if hasattr(o,'item') else o
summary={'companies':560,'ratios':69,'source_latest':'2025-12-31','historical_rows':sum(len(h) for h in hist),'status_counts':C.status.value_counts().to_dict(),'matched_with_evm':int(L.evm.notna().sum())}
(p/'prepared.json').write_text(json.dumps(clean({'latest':latest,'coverage':coverage,'ratios':ratios,'summary':summary}),ensure_ascii=False))
print(json.dumps(summary,indent=2));print(C[C.status.str.startswith('NOT')][['input_ticker','company_name']].to_string(index=False))
