"""Publication input policy. Restricted-origin data must not enter research exports."""
import json,re
RESTRICTED=re.compile(r'wrds|compustat|wharton\.upenn|\bgvkey\b|w[r]?ds[_ /-]?560|wrds[_ /-]?ratios',re.I)
def restricted(value):
    return bool(RESTRICTED.search(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)))
def require_allowed(value):
    if restricted(value):
        raise ValueError('Restricted-origin content: publication blocked; reacquire from an allowed independent source.')
    return value
