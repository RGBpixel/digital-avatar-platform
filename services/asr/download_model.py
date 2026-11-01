import json,urllib.request,hashlib,os,pathlib
size=os.environ.get('ASR_MODEL_SIZE','small')
if size not in ['base','small','medium']:raise ValueError('Unsupported model')
root=pathlib.Path(__file__).resolve().parents[2]/'models'/('faster-whisper-'+size)
root.mkdir(parents=True,exist_ok=True)
repo='Systran/faster-whisper-'+size
meta=json.load(urllib.request.urlopen('https://huggingface.co/api/models/'+repo+'?blobs=true',timeout=60))
revision=meta['sha']
for item in meta['siblings']:
 name=item['rfilename']
 if name not in ['config.json','model.bin','tokenizer.json','vocabulary.json','vocabulary.txt','preprocessor_config.json']:continue
 target=root/name
 expected=item.get('lfs',{}).get('sha256')
 if target.exists() and (not expected or hashlib.sha256(target.read_bytes()).hexdigest()==expected):continue
 print('Downloading '+name,flush=True)
 with urllib.request.urlopen('https://huggingface.co/'+repo+'/resolve/'+revision+'/'+name,timeout=120) as src,open(str(target)+'.part','wb') as out:
  sha=hashlib.sha256()
  while True:
   chunk=src.read(1024*1024)
   if not chunk:break
   out.write(chunk);sha.update(chunk)
 if expected and sha.hexdigest()!=expected:raise RuntimeError('Model SHA256 mismatch')
 os.replace(str(target)+'.part',target)
(root/'source.json').write_text(json.dumps({'repo':repo,'revision':revision}),encoding='utf8')
print('Model ready',flush=True)
