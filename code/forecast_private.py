"""Transparent private-company revenue-index prototype. No hidden target financials.
Reported observations, guidance, analyst assumptions and conditional valuation stay separate.
"""
import math,statistics

def validate_target_input_boundary(target):
 """Allow only instructor financials and official-website identity for targets.
 Public-peer enrichment remains separate. Null legacy cash is not usable data.
 """
 allowed={'id','name','website','revenue_0','EBITDA_0','debt','cash','currency','baseline_period','financial_provenance'}
 extra=set(target)-allowed
 if extra:raise ValueError('Forbidden target input fields: '+', '.join(sorted(extra)))
 if target.get('cash') is not None:raise ValueError('Target cash is not an authorized input')
 provenance=target.get('financial_provenance') or {}
 for field in ('revenue_0','EBITDA_0','debt'):
  value=target.get(field)
  if value is None:continue
  if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
   raise ValueError('Invalid target financial value: '+field)
  source=provenance.get(field,{})
  if source.get('source_type')!='INSTRUCTOR_WORKBOOK':
   raise ValueError('Target '+field+' must come from the supplied instructor workbook')
  if not all(source.get(k) for k in ('source_locator','period','currency','unit')):
   raise ValueError('Target '+field+' needs its workbook/cell, period, currency and units')
 return True

def extend_fiscal(peer,anchor,rho,end=2032):
 levels={int(k):float(v) for k,v in peer['revenue_levels'].items()};last=max(levels)
 g=levels[last]/levels[last-1]-1
 for y in range(last+1,end+1):
  g=anchor+rho*(g-anchor);levels[y]=levels[y-1]*(1+g)
 return levels

def calendarize(levels,fiscal_end_month,year):
 # Explicit uniform-within-fiscal-year assumption; no seasonal quarters fabricated.
 if fiscal_end_month==12:return levels[year]
 w=fiscal_end_month/12
 return w*levels[year]+(1-w)*levels[year+1]

def run(config):
 validate_target_input_boundary(config['target'])
 assert config['target']['revenue_0'] is None or (config['target']['currency'] and config['target']['baseline_period'])
 active=[p for p in config['peers'] if p['growth_weight']>0]
 assert len({p['issuer_id'] for p in active})==len(active)
 assert abs(sum(p['growth_weight'] for p in active)-1)<1e-10
 anchor=config['assumptions']['long_run_growth'];rho=config['assumptions']['growth_persistence']
 peer_rows=[];paths={};baseyear=config['baseline_index_year']
 for p in active:
  fs=extend_fiscal(p,anchor,rho);cy={y:calendarize(fs,p['fiscal_end_month'],y) for y in range(baseyear,baseyear+6)};paths[p['issuer_id']]=cy
  for h in range(1,6):
   y=baseyear+h
   peer_rows.append({'issuer_id':p['issuer_id'],'horizon':h,'calendar_year':y,'revenue_growth':cy[y]/cy[y-1]-1,'weight':p['growth_weight'],'source_ids':p['source_ids'],'status':'GUIDANCE_AND_ASSUMPTION_CALENDARIZED_PATH','calendarization':'Uniform intrayear revenue assumption; not actual quarterly calendarization','future_year_rule':'No invented consensus; unsupported fiscal years fade toward the explicit growth anchor'})
 forecasts=[];conditional=[];peer_growth={h:math.expm1(sum(p['growth_weight']*math.log(paths[p['issuer_id']][baseyear+h]/paths[p['issuer_id']][baseyear+h-1]) for p in active)) for h in range(1,6)}
 for scenario,d in config['scenarios'].items():
  index=100
  for h in range(1,6):
   # This is a hypothetical relative signal sensitivity, not an inferred website effect.
   delta=d['initial_log_growth_adjustment']*.5**((h-1)/config['assumptions']['signal_half_life_years'])
   g=math.expm1(math.log1p(peer_growth[h])+delta);index*=1+g
   row={'target_id':config['target']['id'],'company':config['target']['name'],'scenario':scenario,'horizon':h,'calendar_year':baseyear+h,'revenue_index':index,'revenue_growth':g,'peer_reference_growth':peer_growth[h],'target_relative_log_adjustment':delta,'revenue_currency':None if config['target']['revenue_0'] is None else config['target']['revenue_0']*index/100,'EBITDA':None,'EBITDA_margin':None,'EV':None,'equity_value':None,'status':'ILLUSTRATIVE_INDEXED_SCENARIO_NOT_CALIBRATED_COMPANY_FORECAST','assumption_ids':['A_BASE100','A_FADE','A_CALENDAR','A_SCENARIO_'+scenario.upper()],'currency':config['target']['currency']}
   forecasts.append(row)
   for margin in config['assumptions']['margin_sensitivities']:
    e=index*margin
    for haircut in config['assumptions']['enterprise_adjustment_sensitivities']:
     m=config['multiple_reference']['median_provider_multiple']*(1-haircut)
     conditional.append({'target_id':config['target']['id'],'scenario':scenario,'horizon':h,'calendar_year':baseyear+h,'revenue_index':index,'assumed_EBITDA_margin':margin,'conditional_EBITDA_per_100_baseline_revenue':e,'public_equivalent_EV_EBITDA':config['multiple_reference']['median_provider_multiple'],'illustrative_enterprise_adjustment':haircut,'conditional_EV_EBITDA':m,'conditional_EV_per_100_baseline_revenue':e*m,'multiple_snapshot_date':config['multiple_reference']['snapshot_date'],'status':'CONDITIONAL_MARGIN_AND_CONSTANT_MULTIPLE_SENSITIVITY_NOT_VALUATION','discount_scope':'Enterprise sensitivity only; no equity DLOM and no discount to revenue'})
 return {'forecasts':forecasts,'peer_paths':peer_rows,'conditional_valuation':conditional,'effective_peer_count':1/sum(p['growth_weight']**2 for p in active),'equal_weight_historical_note':'Historical four-change CAGRs are context, not a forward forecast.'}

def validate(config,result):
 assert config['target']['id']=='GC_NETCHEX'
 assert all(v is None for v in [config['target']['revenue_0'],config['target']['EBITDA_0'],config['target']['debt']]),'This published pilot has no supplied private financials'
 for scenario in config['scenarios']:
  prev=100
  rows=[x for x in result['forecasts'] if x['scenario']==scenario]
  assert len(rows)==5
  for x in rows:
   assert math.isclose(x['revenue_index'],prev*(1+x['revenue_growth']),rel_tol=1e-12)
   assert x['revenue_currency'] is None and x['EBITDA'] is None and x['EV'] is None
   prev=x['revenue_index']
  cagr=(rows[-1]['revenue_index']/100)**.2-1
  assert math.isclose((1+cagr)**5,rows[-1]['revenue_index']/100,rel_tol=1e-12)
 for x in result['conditional_valuation']:
  assert math.isclose(x['conditional_EV_per_100_baseline_revenue'],x['conditional_EBITDA_per_100_baseline_revenue']*x['conditional_EV_EBITDA'],rel_tol=1e-12)
  assert math.isclose(x['conditional_EV_EBITDA'],x['public_equivalent_EV_EBITDA']*(1-x['illustrative_enterprise_adjustment']),rel_tol=1e-12)
 # Honest concentration and scenario-order diagnostics.
 assert math.isclose(result['effective_peer_count'],4)
 for h in range(1,6):
  vals={x['scenario']:x['revenue_index'] for x in result['forecasts'] if x['horizon']==h}
  assert vals['bear']<=vals['base']<=vals['bull']
 return {'horizon_rows':len(result['forecasts']),'conditional_valuation_rows':len(result['conditional_valuation']),'absolute_target_financials':'UNKNOWN_NOT_FABRICATED','source_policy':'PERMITTED_ONLY','formula_checks':'PASSED','calibration':'NOT_PERFORMED','backtest':'NOT_PERFORMED','website_only_standalone_growth':'INSUFFICIENT_QUANTITIES'}

if __name__=='__main__':
 import argparse,json,gzip
 from pathlib import Path
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 bundle=json.load(gzip.open(a.input,'rt')) if a.input.suffix=='.gz' else json.loads(a.input.read_text())
 config=bundle.get('config',bundle);result=run(config);checks=validate(config,result)
 a.output.write_text(json.dumps({'config':config,'results':result,'validation':checks},indent=2));print(checks)
