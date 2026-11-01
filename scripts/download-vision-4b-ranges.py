from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,json,time,shutil
root=Path(__file__).resolve().parents[1];folder=root/'models'/'vision-4b';name='Qwen3VL-4B-Instruct-Q4_K_M.gguf';target=folder/name;old=target.with_suffix('.part');total=2497281664
if target.exists():print('Already complete',flush=True);raise SystemExit(0)
meta=folder/'range-plan.json'
if meta.exists():plan=json.loads(meta.read_text())
else:
 start=old.stat().st_size if old.exists() else 0;step=(total-start+5)//6;plan={'prefix':start,'ranges':[(i,start+i*step,min(total-1,start+(i+1)*step-1)) for i in range(6) if start+i*step<total]};meta.write_text(json.dumps(plan))
def run(part):
 index,first,last=part;p=folder/('range-'+str(index)+'.part');offset=first+(p.stat().st_size if p.exists() else 0)
 if offset>last:return p
 url='https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct-GGUF/resolve/main/'+name+'?download=true&segment='+str(index)+'&offset='+str(offset)
 with requests.get(url,headers={'Range':f'bytes={offset}-{last}'},stream=True,timeout=(30,90)) as r:
  r.raise_for_status()
  if r.status_code!=206 or not r.headers.get('content-range','').startswith('bytes '+str(offset)+'-'):raise RuntimeError('Range not honored')
  print('Range',index,'start',offset,'end',last,flush=True)
  with p.open('ab') as f:
   for chunk in r.iter_content(1024*1024):f.write(chunk)
 if p.stat().st_size!=last-first+1:raise RuntimeError('Incomplete range')
 print('Range',index,'ready',flush=True);return p
with ThreadPoolExecutor(max_workers=6) as pool:parts=list(pool.map(run,plan['ranges']))
assembled=target.with_suffix('.assembled')
with assembled.open('wb') as dst:
 if plan['prefix']:
  with old.open('rb') as src:shutil.copyfileobj(src,dst,1024*1024)
 for p in parts:
  with p.open('rb') as src:shutil.copyfileobj(src,dst,1024*1024)
if assembled.stat().st_size!=total:raise RuntimeError('Wrong total size')
assembled.rename(target);print('4B model ready',total,flush=True)
