import json,urllib.request,time
from reception_phrases import FIXED_PHRASES
base='http://127.0.0.1:3210'
samples=json.load(urllib.request.urlopen(base+'/api/voice-samples?site=office'))
if len(samples)!=1:raise RuntimeError('请指定当前样音，不能自动选择多个样音')
for text in FIXED_PHRASES:
 payload=json.dumps(dict(sampleId=samples[0]['id'],text=text,personality='calm',emotion='neutral',intensity=0.5)).encode()
 start=time.monotonic()
 req=urllib.request.Request(base+'/api/tts?site=office',data=payload,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=200) as r:
  audio=r.read()
  assert audio[:4]==b'RIFF'
 print('固定问话已准备，耗时 %.2f 秒'%(time.monotonic()-start),flush=True)
