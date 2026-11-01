from pathlib import Path
import requests,zipfile,hashlib,json,time
root=Path(__file__).resolve().parents[1];target=root/'models'/'vision';target.mkdir(parents=True,exist_ok=True);runtime=root/'tools'/'llama-vision';runtime.mkdir(parents=True,exist_ok=True)
files=[('https://github.com/ggml-org/llama.cpp/releases/download/b11707/llama-b11707-bin-win-cuda-12.4-x64.zip',runtime/'llama.zip'),('https://github.com/ggml-org/llama.cpp/releases/download/b11707/cudart-llama-bin-win-cuda-12.4-x64.zip',runtime/'cudart.zip'),('https://huggingface.co/unsloth/Qwen3.5-2B-GGUF/resolve/main/Qwen3.5-2B-Q4_K_M.gguf',target/'Qwen3.5-2B-Q4_K_M.gguf'),('https://huggingface.co/unsloth/Qwen3.5-2B-GGUF/resolve/main/mmproj-F16.gguf',target/'mmproj-F16.gguf')]
for url,path in files:
 if path.exists():print('Exists:',path.name,flush=True);continue
 tmp=path.with_suffix(path.suffix+'.part');start=tmp.stat().st_size if tmp.exists() else 0
 with requests.get(url,headers={'Range':'bytes='+str(start)+'-'} if start else {},stream=True,timeout=(20,90)) as r:
  r.raise_for_status();mode='ab' if r.status_code==206 else 'wb';total=int(r.headers.get('content-length','0'));print('Downloading',path.name,total,flush=True);last=time.monotonic()
  with tmp.open(mode) as f:
   for chunk in r.iter_content(1024*1024):
    f.write(chunk)
    if time.monotonic()-last>15:print(path.name,tmp.stat().st_size,'bytes',flush=True);last=time.monotonic()
 tmp.rename(path)
 if path.suffix=='.zip':
  with zipfile.ZipFile(path) as z:
   for n in z.namelist():
    resolved=(runtime/n).resolve()
    if not resolved.is_relative_to(runtime.resolve()):raise RuntimeError('unsafe zip path')
   z.extractall(runtime)
 print('Ready:',path.name,flush=True)
print('All vision downloads completed',flush=True)
