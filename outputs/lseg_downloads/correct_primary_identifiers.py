import json,pathlib,warnings
import pandas as pd,lseg.data as ld
import download_560 as core
from complete_and_validate import get_batches,store_combined,DATED
warnings.filterwarnings('ignore',category=FutureWarning)
P=pathlib.Path(__file__).resolve().parent
def main():
    m=json.loads((P/'target_mapping_560.json').read_text())
    profile=pd.read_csv(P/'company_profiles_raw.csv').drop_duplicates('Instrument');pmap=profile.set_index('Instrument').to_dict('index')
    new=[];changes=[]
    for r in m:
        old=r['ric'];primary=pmap.get(old,{}).get('TR.PRIMARYRIC')
        if r['input_ticker']=='KORE':primary='KORE.K^G26'
        if isinstance(primary,str) and primary and primary!=old:
            r['ric']=primary;r['mapping_status']='PROVIDER_PRIMARY_EQUITY_LINK_REVIEWABLE'
            r['mapping_evidence']='LSEG TR.PrimaryRIC; KORE exception corrected using exact ordinary-share search.'
            changes.append(dict(company_id=r['company_id'],input_ticker=r['input_ticker'],old_ric=old,new_ric=primary));new.append(primary)
    (P/'primary_identifier_corrections.json').write_text(json.dumps(changes,indent=2))
    (P/'target_mapping_560.json').write_text(json.dumps(m,indent=2));pd.DataFrame(m).to_csv(P/'target_mapping_560.csv',index=False)
    valid={r['ric'] for r in m};new=sorted(set(new));ld.open_session()
    fields=['TR.CommonName','TR.BusinessSummary','TR.HeadquartersCountry','TR.TRBCBusinessSector','TR.TRBCIndustryGroup','TR.TRBCIndustry','TR.NumberofEmployees','TR.NumberofEmployees.date','TR.CompanyIncorpDate','TR.PrimaryRIC','TR.ISIN','TR.CUSIP','TR.ExchangeName']
    store_combined('company_profiles_raw',get_batches(new,fields,{},'primaryfix_profiles'),valid)
    for name,params in [('annual_five_years',{'SDate':0,'EDate':-4,'FRQ':'FY','Curn':'USD','Scale':0}),('latest_quarter',{'Period':'FQ0','Curn':'USD','Scale':0}),('ltm',{'Period':'LTM','Curn':'USD','Scale':0})]:
        store_combined(name,get_batches(new,DATED,params,'primaryfix_'+name),valid)
    # Redownload market values with explicit currency and field dates. Shares are counts.
    market=['TR.CompanyMarketCap','TR.CompanyMarketCap.currency','TR.CompanyMarketCap.date','TR.EV','TR.EV.currency','TR.EV.date','TR.EVToEBITDA','TR.PriceClose','TR.PriceClose.currency','TR.SharesOutstanding','TR.PriceClose.date']
    parts=get_batches(sorted(valid),market,{'Curn':'USD','Scale':0},'market_usd_verified',20)
    if parts:core.save(pd.concat(parts,ignore_index=True),P/'market')
    for name,base in [('business_segments','TR.BGS.BusTotalRevenue'),('geographic_segments','TR.BGS.GeoTotalRevenue')]:
        fields=[base,base+'.segmentName',base+'.fperiod',base+'.currency']
        if name=='business_segments':fields.append(base+'.segmentCode')
        store_combined(name,get_batches(new,fields,{'Period':'FY0','Curn':'USD','Scale':0},'primaryfix_'+name),valid)
    ld.close_session();print('Primary identifier corrections completed:',len(changes),flush=True)
if __name__=='__main__':main()
