import pathlib,json,urllib.request,subprocess,concurrent.futures,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
root=pathlib.Path(__file__).parent/'models'/'Fun-CosyVoice3-0.5B-2512';root.mkdir(parents=True,exist_ok=True)
repo='FunAudioLLM/Fun-CosyVoice3-0.5B-2512'
meta=json.load(urllib.request.urlopen('https://huggingface.co/api/models/'+repo+'?blobs=true',timeout=60))
selected=[f for f in meta['siblings'] if f['rfilename'].startswith('CosyVoice-BlankEN/') or f['rfilename'] in ['campplus.onnx','config.json','configuration.json','cosyvoice3.yaml','flow.pt','hift.pt','llm.pt','speech_tokenizer_v3.onnx']]
def download(f):
 name=f['rfilename'];target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
 expected=f.get('lfs',{}).get('sha256')
 if target.exists() and (not expected or hashlib.file_digest(open(target,'rb'),'sha256').hexdigest()==expected):return
 part=pathlib.Path(str(target)+'.part')
 url='https://huggingface.co/'+repo+'/resolve/'+meta['sha']+'/'+name
 subprocess.run(['curl.exe','-sS','-L','--fail','--retry','8','--retry-delay','3','--retry-all-errors','--connect-timeout','30','--continue-at','-','--output',str(part),url],check=True)
 if expected and hashlib.file_digest(open(part,'rb'),'sha256').hexdigest()!=expected:raise RuntimeError('SHA256 mismatch '+name)
 part.replace(target);print('已下载 '+name,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(download,selected))
(root/'source.json').write_text(json.dumps({'repo':repo,'revision':meta['sha']}))
print('官方权重已完整校验',flush=True)
