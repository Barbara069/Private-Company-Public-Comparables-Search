"""LSEG collection for the original 560 only. No comp selection or scoring."""
import json,pathlib,time,datetime,collections,urllib.parse,re,difflib
import pandas as pd
import lseg.data as ld
P=pathlib.Path(__file__).resolve().parent
RAW=P/'raw_560';RAW.mkdir(exist_ok=True)
TARGETS=json.loads((P.parent/'global_comps_560/prepared/Targets_560.json').read_text())
LOG=json.loads((RAW/'request_log.json').read_text()) if (RAW/'request_log.json').exists() else []
def save(df,path):
    df.to_csv(path.with_suffix('.csv'),index=False)
    path.with_suffix('.json').write_text(df.to_json(orient='records',force_ascii=False))
def get(universe,fields,params,tag):
    file=RAW/(tag+'.csv')
    if file.exists():return pd.read_csv(file,keep_default_na=False,dtype={'Instrument':str})
    for retry in range(2):
        try:
            d=ld.get_data(universe,fields,parameters=params,header_type=ld.HeaderType.NAME)
            save(d,RAW/tag)
            LOG.append(dict(tag=tag,status='DOWNLOADED',instruments=universe,fields=fields,parameters=params,rows=len(d)))
            (RAW/'request_log.json').write_text(json.dumps(LOG,indent=2))
            time.sleep(1);return d
        except Exception as e:
            if retry==0:time.sleep(3)
            else:
                LOG.append(dict(tag=tag,status='FAILED',instruments=universe,fields=fields,parameters=params,error=str(e)[:1500]))
                (RAW/'request_log.json').write_text(json.dumps(LOG,indent=2));return pd.DataFrame()
def domain(u):
    u=str(u or '')
    return urllib.parse.urlparse(u if '://' in u else 'https://'+u).netloc.lower().removeprefix('www.')
def tokens(n):
    return set(re.findall('[a-z0-9]+',str(n).lower()))-set('the inc incorporated corp corporation holdings holding company co limited ltd plc group'.split())
def main():
    assert len(TARGETS)==560
    ld.open_session()
    conversions=[]
    for i in range(0,560,40):
        f=RAW/f'conversion_{i}.json'
        if f.exists():part=json.loads(f.read_text())
        else:
            tickers=[t['ticker'] for t in TARGETS[i:i+40]]
            try:
                d=ld.discovery.convert_symbols(tickers,from_symbol_type=ld.discovery.SymbolTypes.TICKER_SYMBOL,to_symbol_types=[ld.discovery.SymbolTypes.RIC,ld.discovery.SymbolTypes.ISIN,ld.discovery.SymbolTypes.OA_PERM_ID],preferred_country_code='USA')
                d=d.reset_index().rename(columns={'index':'input_ticker'})
                part=json.loads(d.to_json(orient='records'));f.write_text(json.dumps(part));time.sleep(1)
            except Exception as e:
                part=[];print('Conversion batch failed',i,str(e)[:100],flush=True)
        conversions.extend(part)
        print('Identifier conversion',min(i+40,560),'/560',flush=True)
    (P/'identifier_conversion_raw.json').write_text(json.dumps(conversions,indent=2))
    bytic=collections.defaultdict(list)
    for r in conversions:
        symbol=str(r.get('input_ticker',r.get('index','')))
        ric=r.get('RIC')
        if isinstance(ric,str) and ric:bytic[symbol].append(r)
    rics=sorted({r['RIC'] for r in conversions if isinstance(r.get('RIC'),str) and r['RIC']})
    profilefields=['TR.CommonName','TR.BusinessSummary','TR.HeadquartersCountry','TR.TRBCBusinessSector','TR.TRBCIndustryGroup','TR.TRBCIndustry','TR.NumberofEmployees','TR.NumberofEmployees.date','TR.CompanyIncorpDate','TR.PrimaryRIC','TR.ISIN','TR.CUSIP','TR.ExchangeName']
    profiles=[]
    for i in range(0,len(rics),30):
        d=get(rics[i:i+30],profilefields,{},f'profiles_{i}')
        if len(d):profiles.append(d)
        print('Company profiles',min(i+30,len(rics)),'/',len(rics),flush=True)
    prof=pd.concat(profiles,ignore_index=True) if profiles else pd.DataFrame()
    save(prof,P/'company_profiles_raw')
    profmap={str(r.get('Instrument')):r for r in prof.to_dict('records')}
    mapping=[]
    for t in TARGETS:
        choices=bytic.get(t['ticker'],[]);eligible=[]
        for c in choices:
            r=profmap.get(c['RIC'],{});name=r.get('TR.CommonName',r.get('TR.COMMONNAME',''))
            web=r.get('TR.CompanyWebsite',r.get('TR.COMPANYWEBSITE',''))
            a,b=tokens(t['company_name']),tokens(name)
            overlap=len(a&b)/max(1,min(len(a),len(b)))
            exact_domain=bool(domain(web)) and domain(web)==domain(t['website'])
            if exact_domain or overlap>=.6:eligible.append((c,exact_domain,overlap))
        chosen=eligible[0] if len(eligible)==1 else None
        mapping.append(dict(company_id=t['company_id'],target_name=t['company_name'],input_ticker=t['ticker'],original_website=t['website'],
                            ric=chosen[0]['RIC'] if chosen else '',
                            mapping_status='DOMAIN_OR_NAME_CONSISTENT_REVIEWABLE' if chosen else ('AMBIGUOUS_OR_NAME_MISMATCH' if choices else 'NO_SYMBOL_RESULT'),
                            candidate_rics=';'.join(c['RIC'] for c in choices)))
    pd.DataFrame(mapping).to_csv(P/'target_mapping_560.csv',index=False)
    (P/'target_mapping_560.json').write_text(json.dumps(mapping,indent=2))
    # Collect candidate instruments even when mapping needs review, but never silently attach
    # their data to the target. The 560-row mapping is authoritative for joins.
    probe=json.loads((P/'field_probe.json').read_text())
    valid=set(probe.get('annual',{}).get('columns',[]))
    wanted=['TR.TotalRevenue','TR.EBITDA','TR.EBIT','TR.GrossProfit','TR.OperatingIncome','TR.NetIncome','TR.TotalAssets','TR.TotalAssetsReported','TR.TotalLiabilities','TR.TotalEquity','TR.TotalDebt','TR.NetDebt','TR.CashAndSTInvestments','TR.CashFromOperatingActivities','TR.CapitalExpenditures','TR.CapexCFStmt','TR.ResearchAndDevelopment','TR.Depreciation','TR.InterestExpense','TR.EffectiveTaxRate','TR.NumberofEmployees','TR.TotalCurrentAssets','TR.TotalCurrentLiabilities','TR.FreeCashFlow']
    fields=[x for x in wanted if x.upper() in {v.upper() for v in valid}]
    dated=['TR.CommonName','TR.TotalRevenue.date','TR.TotalRevenue.currency','TR.TotalRevenue.fperiod','TR.TotalRevenue.calcdate','TR.NumberofEmployees.date']+fields
    print('Financial fields',fields,flush=True)
    for kind,params in [('annual_five_years',{'SDate':0,'EDate':-4,'FRQ':'FY','Curn':'USD','Scale':0}),('latest_quarter',{'SDate':0,'EDate':0,'FRQ':'FQ','Curn':'USD','Scale':0}),('ltm',{'Period':'LTM','Curn':'USD','Scale':0})]:
        parts=[]
        for i in range(0,len(rics),20):
            d=get(rics[i:i+20],dated,params,f'{kind}_{i}')
            if len(d):parts.append(d)
            print(kind,min(i+20,len(rics)),'/',len(rics),flush=True)
        if parts:save(pd.concat(parts,ignore_index=True),P/kind)
    for kind in ['market','business_segments','geographic_segments']:
        if kind.endswith('segments'):
            base='TR.BGS.BusTotalRevenue' if kind=='business_segments' else 'TR.BGS.GeoTotalRevenue'
            fields=[base,base+'.segmentName',base+'.fperiod',base+'.currency']
            if kind=='business_segments':fields.append(base+'.segmentCode')
            parts=[]
            for i in range(0,len(rics),10):
                d=get(rics[i:i+10],fields,{'Period':'FY0','Curn':'USD','Scale':0},f'{kind}_{i}')
                if len(d):parts.append(d)
            if parts:save(pd.concat(parts,ignore_index=True),P/kind)
            continue
        columns=probe.get(kind,{}).get('columns',[])
        fields=[x for x in probe.get(kind,{}).get('fields',[]) if x.upper() in {v.upper() for v in columns}]
        if not fields:continue
        parts=[]
        for i in range(0,len(rics),20):
            d=get(rics[i:i+20],fields,{},f'{kind}_{i}')
            if len(d):parts.append(d)
        if parts:save(pd.concat(parts,ignore_index=True),P/kind)
    (P/'collection_scope.json').write_text(json.dumps(dict(targets=560,ric_candidates=len(rics),mapped=sum(bool(r['ric']) for r in mapping),scope='Original 560 only. No comparable selection, scoring, split or evaluation.',retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='LSEG Workspace Data Library through desktop proxy',amount_units='Native API defaults. Currency and scale require field-level verification before comparisons.'),indent=2))
    ld.close_session();print('Collection finished',flush=True)
if __name__=='__main__':main()
