from pathlib import Path
import json, hashlib, shutil
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'data/master/parts.json').read_text())
out=root/'outputs/company_research_master/Company_Research_Master.csv.gz'
out.parent.mkdir(parents=True,exist_ok=True)
with out.open('wb') as f:
 for name in m['parts']:
  with (root/name).open('rb') as p: shutil.copyfileobj(p,f)
assert hashlib.sha256(out.read_bytes()).hexdigest()==m['combined_sha256']
print('Restored and SHA-256 verified:',out)
