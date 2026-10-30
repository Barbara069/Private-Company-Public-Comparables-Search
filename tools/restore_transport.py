from pathlib import Path
import json, hashlib, shutil
root=Path(__file__).resolve().parents[1]
for item in json.loads((root/'transport/manifest.json').read_text()):
 out=root/item['path'];out.parent.mkdir(parents=True,exist_ok=True)
 if not out.exists() or hashlib.sha256(out.read_bytes()).hexdigest()!=item['sha256']:
  with out.open('wb') as f:
   for name in item['parts']:
    with (root/name).open('rb') as p:shutil.copyfileobj(p,f)
 assert hashlib.sha256(out.read_bytes()).hexdigest()==item['sha256']
print('Transport parts restored and verified.')
