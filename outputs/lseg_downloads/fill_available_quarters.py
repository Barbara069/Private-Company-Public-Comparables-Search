import pathlib,warnings
import pandas as pd,lseg.data as ld
import download_560 as core
from complete_and_validate import DATED
warnings.filterwarnings('ignore',category=FutureWarning)
P=pathlib.Path(__file__).resolve().parent
d=pd.read_csv(P/'latest_quarter.csv',keep_default_na=False);d['Quarter Selection']='FQ0'
ld.open_session()
for lag in range(1,5):
    missing=d.loc[d['TR.TOTALREVENUE'].eq(''),'Instrument'].tolist()
    if not missing:break
    r=core.get(missing,DATED,{'Period':f'FQ-{lag}','Curn':'USD','Scale':0},'published_quarter_fallback_'+str(lag))
    if len(r):
        valid=r.loc[r['TR.TOTALREVENUE'].notna() & r['TR.TOTALREVENUE'].ne('')].copy()
        valid['Quarter Selection']=f'FQ-{lag}: most recent nonmissing reported quarter'
        d=pd.concat([d.loc[~d.Instrument.isin(valid.Instrument)],valid],ignore_index=True)
        print('Quarter fallback',lag,'added',len(valid),flush=True)
core.save(d,P/'latest_quarter');ld.close_session()
