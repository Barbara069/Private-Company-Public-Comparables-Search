"""Build the viewer from the canonical, source-filtered repository snapshot."""
from pathlib import Path
import re,subprocess
from exclude_restricted_sources import validate
P=Path(__file__).resolve().parent;R=P.parent
validate()
js=(P/'website_app.js').read_text()
subprocess.run(['node','--check',str(P/'website_app.js')],check=True)
p=R/'website/index.html';s=p.read_text()
s,n=re.subn(r'<script>.*?</script>',lambda m:'<script>\n'+js+'\n</script>',s,flags=re.S)
assert n==1
p.write_text(s)
print('Built and source-policy checked website')
