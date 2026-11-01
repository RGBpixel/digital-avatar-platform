import os,sys,pathlib,time,json,urllib.request
sys.stdout.reconfigure(encoding='utf-8')
r=pathlib.Path(__file__).parent;sys.path.insert(0,str(r/'deps'));sys.path.insert(0,str(r/'vendor/Matcha-TTS-main'));sys.path.insert(0,str(r/'CosyVoice-main'))
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import torch,numpy as np,soundfile as sf
from cosyvoice.cli.cosyvoice import CosyVoice3
# torchaudio 2.11 delegates decoding to TorchCodec; use genuine SoundFile I/O
# for this WAV-only experiment and the same torchaudio resampling operation.
import cosyvoice.cli.frontend as frontend_module
import torchaudio
def decode_wav(path,rate):
 values,sr=sf.read(path,dtype='float32',always_2d=True)
 tensor=torch.from_numpy(values.mean(axis=1).copy()).unsqueeze(0)
 return torchaudio.functional.resample(tensor,sr,rate) if sr!=rate else tensor
frontend_module.load_wav=decode_wav

model_dir=r/'models/Fun-CosyVoice3-0.5B-2512'
assert (model_dir/'source.json').exists(),'权重尚未校验完成'
yaml=model_dir/'cosyvoice3.yaml';original=model_dir/'cosyvoice3.original.yaml'
if not original.exists():original.write_bytes(yaml.read_bytes())
# Only strip unused training objects; llm/flow/hift remain unchanged.
s=original.read_text();start=s.index('# gan related module');end=s.index('# processor functions');s=s[:start]+s[end:]
a=s.index('parquet_opener:');b=s.index('get_tokenizer:');s=s[:a]+s[b:]
a=s.index('tokenize:');b=s.index('feat_extractor:');s=s[:a]+s[b:]
s=s[:s.index('compute_fbank:')]
yaml.write_text(s,encoding='utf-8')
start=time.monotonic();model=CosyVoice3(str(model_dir),fp16=True)
print('CosyVoice加载秒数',round(time.monotonic()-start,3),flush=True)
samples=json.load(urllib.request.urlopen('http://127.0.0.1:3210/api/voice-samples?site=office'));p=samples[0];assert p['consent']
prep=time.monotonic();prompt='You are a helpful assistant.<|endofprompt|>'+p['transcript']
model.add_zero_shot_spk(prompt,str(r/'reference-for-test.wav'),'bench')
prep=time.monotonic()-prep;print('样音特征准备秒数',round(prep,3),flush=True)
results=[]
for index in range(2):
 start=time.monotonic();chunks=[];first=None
 for output in model.inference_zero_shot('您好，今天有什么可以帮您？',prompt,str(r/'reference-for-test.wav'),zero_shot_spk_id='bench',stream=True,text_frontend=False):
  if first is None:first=time.monotonic()-start;print('CosyVoice首块到达',round(first,3),flush=True)
  chunks.append(output['tts_speech'].detach().cpu().numpy().reshape(-1))
 audio=np.concatenate(chunks);elapsed=time.monotonic()-start
 assert np.isfinite(audio).all() and len(audio)/model.sample_rate>0.3
 sf.write(r/'results'/('cosyvoice-'+str(index+1)+'.wav'),audio,model.sample_rate)
 result=dict(run=index+1,first_chunk_seconds=round(first,3),total_seconds=round(elapsed,3),audio_seconds=round(len(audio)/model.sample_rate,3),chunks=len(chunks),streaming=True,reference_preparation_seconds=round(prep,3),onnx_providers=model.frontend.speech_tokenizer_session.get_providers())
 results.append(result);print(json.dumps(result,ensure_ascii=False),flush=True)
(r/'results/cosyvoice.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
