"""Reject restricted-source input files and adapters anywhere in the publication tree."""
from pathlib import Path
import csv,gzip,json,re,zipfile
from source_policy import restricted,require_allowed
ROOT=Path(__file__).resolve().parents[1]
ENDPOINT=re.compile(r'https?://[^\s\"\'<>]*(?:wrds|wharton\.upenn)[^\s\"\'<>]*',re.I)
def check():
    checked=0
    for p in ROOT.rglob('*'):
        if not p.is_file() or '.git' in p.parts:continue
        relative=p.relative_to(ROOT).as_posix()
        if restricted(relative):raise ValueError('Restricted-source input filename: '+relative)
        if p.suffix=='.xlsx':
            with zipfile.ZipFile(p) as z:
                for name in z.namelist():
                    if name.endswith('.xml'):require_allowed(z.read(name).decode('utf-8'))
        elif p.suffix=='.csv':
            csv.field_size_limit(2**31-1)
            with p.open(encoding='utf-8-sig',newline='') as f:
                for row in csv.DictReader(f):require_allowed(row)
        elif p.suffix in ['.py','.js','.ipynb']:
            if ENDPOINT.search(p.read_text()):raise ValueError('Restricted-provider endpoint in executable source: '+relative)
        checked+=1
    if (ROOT/'website/data/comparison_rebuild_manifest.json.gz').exists():
        from validate_rebuilt_comparables import validate
        validate()
    if (ROOT/'website/data/private_forecast_prototype.json.gz').exists():
        from validate_forecast_prototype import check as check_forecast
        check_forecast()
    print('Publication-tree inputs/adapters checked:',checked)
if __name__=='__main__':check()
