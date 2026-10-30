import json,pathlib,time,warnings
import pandas as pd
import lseg.data as ld
import download_560 as core
warnings.filterwarnings('ignore',category=FutureWarning)
P=pathlib.Path(__file__).resolve().parent;R=P/'raw_560'
OVERRIDES={'ARTN.A':'ARTNA.O','BATR.K':'BATRK.O','CTLP':'CTLP.O^E26','CGEH':'CEPL.O','CL':'CL.CD','EEX':'EEX.N^G26','A950140':'950140.KQ','FWON.K':'FWONK.O','GLIB.A':'GLIBA.O','GETY':'GETYQ.PK','GDEN':'GDEN.O^E26','GTII':'GTII.CD','IAC':'PPLI.O','IMKT.A':'IMKTA.O','ISSC':'IA.O','MPX':'MPX.N^E26','MASI':'MASI.O^F26','HLTC':'NHP.O','NRC':'NRC.O','QVCG.A':'QVCG.O','RCMT':'RCMT.O','SNFC.A':'SNFCA.O','SENE.A':'SENEA.O','SBSA.A':'SBSAQ.PK','TGS':'TGS.OL','AREN':'PAAI.K','TBRG':'TBRG.O^G26','TRUL':'TRLV.K','UNIT':'UNIT.O','UONE.K':'UONEK.O','TMHC':'TMHC.K^G26'}
REVIEW={'CGEH','GLIB.A','IAC','ISSC','NRC','AREN','TRUL','UNIT','QVCG.A'}
F=['TR.TotalRevenue','TR.EBITDA','TR.EBIT','TR.GrossProfit','TR.OperatingIncome','TR.NetIncome','TR.TotalAssets','TR.TotalAssetsReported','TR.TotalLiabilities','TR.TotalEquity','TR.TotalDebt','TR.NetDebt','TR.CashAndSTInvestments','TR.CashFromOperatingActivities','TR.CapitalExpenditures','TR.CapexCFStmt','TR.ResearchAndDevelopment','TR.Depreciation','TR.InterestExpense','TR.EffectiveTaxRate','TR.NumberofEmployees','TR.TotalCurrentAssets','TR.TotalCurrentLiabilities','TR.FreeCashFlow']
DATED=['TR.CommonName','TR.TotalRevenue.date','TR.TotalRevenue.currency','TR.TotalRevenue.fperiod','TR.TotalRevenue.calcdate','TR.NumberofEmployees.date']+F
def load(name):return pd.read_csv(P/(name+'.csv'),keep_default_na=False)
def store_combined(name,extra,valid):
    parts=[]
    if (P/(name+'.csv')).exists():parts.append(load(name))
    parts.extend(extra)
    if not parts:return
    d=pd.concat(parts,ignore_index=True);d=d[d.Instrument.isin(valid)].drop_duplicates()
    core.save(d,P/name)
def get_batches(rics,fields,params,prefix,size=15):
    parts=[]
    for i in range(0,len(rics),size):
        d=core.get(rics[i:i+size],fields,params,prefix+'_'+str(i))
        if len(d):parts.append(d)
        else:
            for ric in rics[i:i+size]:
                d=core.get([ric],fields,params,prefix+'_single_'+ric.replace('/','_'))
                if len(d):parts.append(d)
        print(prefix,min(i+size,len(rics)),'/',len(rics),flush=True)
    return parts
def main():
    mapping=json.loads((P/'target_mapping_560.json').read_text())
    old={r['ric'] for r in mapping if r['ric']}
    for m in mapping:
        ticker=m['input_ticker']
        if ticker in OVERRIDES:
            m['initial_ric']=m['ric'];m['ric']=OVERRIDES[ticker]
            m['mapping_status']='NAME_OR_LEGAL_ENTITY_CHANGE_REVIEW_REQUIRED' if ticker in REVIEW else 'LSEG_EQUITY_SEARCH_MATCH'
            m['mapping_evidence']='LSEG equity search / primary RIC; identity_exception_searches.json. Share class retained where known.'
    assert len(mapping)==560 and all(m['ric'] for m in mapping)
    pd.DataFrame(mapping).to_csv(P/'target_mapping_560.csv',index=False);(P/'target_mapping_560.json').write_text(json.dumps(mapping,indent=2))
    valid={m['ric'] for m in mapping};new=sorted(valid-old)
    ld.open_session();print('Supplement',len(new),'new instruments; final target rows',len(mapping),flush=True)
    profile=['TR.CommonName','TR.BusinessSummary','TR.HeadquartersCountry','TR.TRBCBusinessSector','TR.TRBCIndustryGroup','TR.TRBCIndustry','TR.NumberofEmployees','TR.NumberofEmployees.date','TR.CompanyIncorpDate','TR.PrimaryRIC','TR.ISIN','TR.CUSIP','TR.ExchangeName']
    store_combined('company_profiles_raw',get_batches(new,profile,{},'resolved_profiles'),valid)
    store_combined('annual_five_years',get_batches(new,DATED,{'SDate':0,'EDate':-4,'FRQ':'FY','Curn':'USD','Scale':0},'resolved_annual'),valid)
    # Never retain the earlier quarterly request that defaulted to FY.
    parts=get_batches(sorted(valid),DATED,{'Period':'FQ0','Curn':'USD','Scale':0},'quarter_verified',20)
    if parts:core.save(pd.concat(parts,ignore_index=True),P/'latest_quarter')
    store_combined('ltm',get_batches(new,DATED,{'Period':'LTM','Curn':'USD','Scale':0},'resolved_ltm'),valid)
    current=load('ltm');missing=sorted(valid-set(current.Instrument))
    store_combined('ltm',get_batches(missing,DATED,{'Period':'LTM','Curn':'USD','Scale':0},'retry_ltm',1),valid)
    market=['TR.CompanyMarketCap','TR.EV','TR.EVToEBITDA','TR.PriceClose','TR.SharesOutstanding','TR.PriceClose.date']
    store_combined('market',get_batches(new,market,{},'resolved_market'),valid)
    for name,base in [('business_segments','TR.BGS.BusTotalRevenue'),('geographic_segments','TR.BGS.GeoTotalRevenue')]:
        fields=[base,base+'.segmentName',base+'.fperiod',base+'.currency']
        if name=='business_segments':fields.append(base+'.segmentCode')
        store_combined(name,get_batches(new,fields,{'Period':'FY0','Curn':'USD','Scale':0},'resolved_'+name,8),valid)
    ld.close_session();(R/'completion_request_log.json').write_text(json.dumps(core.LOG,indent=2));print('Supplement finished',flush=True)
if __name__=='__main__':main()
