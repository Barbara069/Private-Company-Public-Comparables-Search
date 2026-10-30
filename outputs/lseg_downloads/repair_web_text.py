import json,pathlib,urllib.request,gzip,zlib,re,hashlib,concurrent.futures as cf,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent/'global_comps_560'))
from collect_web_evidence import TextParser
P=pathlib.Path(__file__).resolve().parent.parent/'global_comps_560/web_evidence'
rows=json.loads((P/'collection.json').read_text())
bad=json.loads(pathlib.Path('/tmp/4511_bad_web_pages.json').read_text())
def repair(r):
    try:
        req=urllib.request.Request(r['requested_url'],headers={'User-Agent':'Company research hb2885@columbia.edu','Accept-Encoding':'identity'})
        with urllib.request.urlopen(req,timeout=20) as response:
            b=response.read();encoding=response.headers.get('Content-Encoding','')
        if b.startswith(b'\x1f\x8b') or encoding=='gzip':b=gzip.decompress(b)
        elif encoding=='deflate':b=zlib.decompress(b)
        html=b.decode('utf-8',errors='replace');p=TextParser();p.feed(html)
        text='\n'.join(' '.join(x.split()) for x in ''.join(p.parts).splitlines() if x.strip())
        if text.count('�')>max(5,len(text)*.005):raise ValueError('Response still not valid readable text')
        pathlib.Path(r['text_file']).write_text(text)
        key=hashlib.sha256(r['requested_url'].encode()).hexdigest()[:16];(P/'raw'/(key+'.html')).write_text(html)
        r.update(text_characters=len(text),status='FETCHED_TEXT_NOT_FACT_VERIFIED',repair='Decompressed HTTP response before decoding')
    except Exception as e:
        r.update(status='TEXT_DECODE_FAILED_NOT_EVIDENCE',error=str(e)[:200]);r.pop('text_file',None)
    return r
with cf.ThreadPoolExecutor(max_workers=3) as ex:fixed=list(ex.map(repair,bad))
byurl={r['requested_url']:r for r in fixed}
rows=[byurl.get(r['requested_url'],r) for r in rows]
(P/'collection.json').write_text(json.dumps(rows,indent=2));print('Repaired',len(fixed),'responses;',sum(r['status']=='TEXT_DECODE_FAILED_NOT_EVIDENCE' for r in fixed),'failed')
