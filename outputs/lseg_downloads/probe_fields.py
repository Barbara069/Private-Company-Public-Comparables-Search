import lseg.data as ld,pathlib,json,time
P=pathlib.Path(__file__).resolve().parent
GROUPS={
'profile':['TR.CommonName','TR.CompanyName','TR.BusinessSummary','TR.CompanyWebsite','TR.HeadquartersCountry','TR.TRBCBusinessSector','TR.TRBCIndustryGroup','TR.TRBCIndustry','TR.NumberofEmployees','TR.CompanyFoundedYear','TR.CompanyIncorpDate','TR.PrimaryRIC','TR.ISIN','TR.CUSIP','TR.ExchangeName','TR.F.TotRevenue'],
'annual':['TR.TotalRevenue','TR.EBITDA','TR.EBIT','TR.GrossProfit','TR.OperatingIncome','TR.NetIncome','TR.TotalAssets','TR.TotalAssetsReported','TR.TotalLiabilities','TR.TotalEquity','TR.TotalDebt','TR.NetDebt','TR.CashAndSTInvestments','TR.CashFromOperatingActivities','TR.CapitalExpenditures','TR.CapexCFStmt','TR.ResearchAndDevelopment','TR.Depreciation','TR.InterestExpense','TR.EffectiveTaxRate','TR.NumberofEmployees','TR.TotalCurrentAssets','TR.TotalCurrentLiabilities','TR.FreeCashFlow'],
'market':['TR.CompanyMarketCap','TR.EV','TR.EVToEBITDA','TR.PriceClose','TR.SharesOutstanding','TR.PriceClose.date'],
'segments':['TR.BGS.BusSegmentName','TR.BGS.BusSegmentRevenue','TR.BGS.BusTotalRevenue','TR.BGS.GeoSegmentName','TR.BGS.GeoSegmentRevenue']}
ld.open_session();out={}
for group,fields in GROUPS.items():
    try:
        d=ld.get_data(['WEN.O','PCTY.O'],fields,header_type=ld.HeaderType.NAME)
        d.to_csv(P/('probe_'+group+'.csv'),index=False)
        out[group]={'fields':fields,'columns':list(d.columns),'sample':json.loads(d.to_json(orient='records'))}
        print(group,list(d.columns),flush=True)
    except Exception as e:out[group]={'error':str(e)[:800]};print(group,type(e).__name__,str(e)[:200],flush=True)
    time.sleep(1)
(P/'field_probe.json').write_text(json.dumps(out,indent=2));ld.close_session()
