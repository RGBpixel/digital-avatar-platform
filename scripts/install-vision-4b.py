from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,time
root=Path(__file__).resolve().parents[1];target=root/'models'/'vision-4b';target.mkdir(parents=True,exist_ok=True)
files=['Qwen3VL-4B-Instruct-Q4_K_M.gguf','mmproj-Qwen3VL-4B-Instruct-F16.gguf']
def download(name):
 path=target/name
 if path.exists():print('Ready',name,flush=True);return
 tmp=path.with_suffix('.part');start=tmp.stat().st_size if tmp.exists() else 0
 url='https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct-GGUF/resolve/main/'+name
 with requests.get(url,headers={'Range':'bytes='+str(start)+'-'} if start else {},stream=True,timeout=(30,90)) as r:
  r.raise_for_status();append=r.status_code==206;expected=int(r.headers.get('content-length',0))+(start if append else 0);print('Downloading',name,'total',expected,flush=True)
  with tmp.open('ab' if append else 'wb') as f:
   last=time.monotonic()
   for chunk in r.iter_content(1024*1024):
    f.write(chunk)
    if time.monotonic()-last>20:print(name,tmp.stat().st_size,'bytes',flush=True);last=time.monotonic()
 if expected and tmp.stat().st_size!=expected:raise RuntimeError('Incomplete download')
 tmp.rename(path);print('Completed',name,path.stat().st_size,flush=True)
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(download,files))
print('4B files ready',flush=True)
