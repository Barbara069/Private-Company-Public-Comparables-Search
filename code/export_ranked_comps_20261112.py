from pathlib import Path
import csv,gzip,json,math
P=Path(__file__).resolve().parent;D=P.parents[1]/'outputs/public_research_website/data/matches';O=P.parents[1]/'outputs/clean_research_delivery/Public_Comps_All_Targets.csv'
def number(x):
 try:return float(x) if x is not None and x!='' and math.isfinite(float(x)) else -math.inf
 except (TypeError,ValueError):return -math.inf
def key(r):return (str(r.get('Status','')).startswith('WITHHELD') or number(r.get('Similarity Percent'))==-math.inf,-number(r.get('Similarity Percent')),-number(r.get('Evidence Coverage Percent')),-number(r.get('Evidence Supported Points')),r['Candidate Name'],r['Candidate RIC'])
def summary(r):
 ds=[f for f in r.get('Facet Details',[]) if number(f.get('weight'))>0 and not f.get('duplicate_of_main') and f.get('score') is not None and f.get('target',{}).get('text') and f.get('candidate',{}).get('text')]
 if not ds:return ('No eligible paired evidence.','Not established; missing evidence is not a difference.')
 a=max(ds,key=lambda f:(number(f['score']),number(f['weight'])));shared=sorted(set(a['target'].get('categories',[]))&set(a['candidate'].get('categories',[])));match=a['facet']+': '+('shared '+', '.join(shared[:3]) if shared else 'closest observed facet-text match')+f" ({a['score']}/100)"
 exp=[f for f in ds if set(f['target'].get('categories',[]))^set(f['candidate'].get('categories',[]))];b=min(exp or ds,key=lambda f:(number(f['score']),-number(f['weight'])));ta=sorted(set(b['target'].get('categories',[]))-set(b['candidate'].get('categories',[])));cb=sorted(set(b['candidate'].get('categories',[]))-set(b['target'].get('categories',[])));diff=b['facet']+': '+('target-only extracted categories: '+(', '.join(ta[:2]) or 'none extracted')+'; comp-only: '+(', '.join(cb[:2]) or 'none extracted') if ta or cb else 'lowest observed text similarity; specific economic difference not verified')
 return match,diff
columns=['Target ID','Target Name','Rank','Candidate Name','Candidate RIC','Similarity Percent','Evidence Coverage Percent','Evidence Supported Points','Strongest Observed Match','Largest Observed Difference','Candidate Source URL','Ranking Basis','Status'];groups={}
for p in sorted(D.glob('group_*.json.gz')):groups.update(json.load(gzip.open(p,'rt')))
count=0
with O.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
 for tid,rs in sorted(groups.items()):
  for i,r in enumerate(sorted(rs,key=key),1):
   a,b=summary(r);row={k:r.get(k) for k in columns if k in r};row.update({'Rank':i,'Strongest Observed Match':a,'Largest Observed Difference':b,'Ranking Basis':'Observed similarity descending; then evidence coverage; then evidence-supported points; withheld/unknown last','Status':r.get('Status','EXPLORATORY; NOT_FINAL_RECOMMENDATION')});w.writerow(row);count+=1
assert len(groups)==560 and all(5<=len(rs)<=10 for rs in groups.values()) and count==sum(map(len,groups.values()));print('Exported',len(groups),'targets and',count,'sorted candidates:',O)
