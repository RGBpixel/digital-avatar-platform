import os,sys,pathlib,json,time,urllib.request,hashlib,io
sys.stdout.reconfigure(encoding='utf-8')
r=pathlib.Path(__file__).parent;project=r.parents[1];sys.path.insert(0,str(r/'fastdeps'))
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import torch,numpy as np,soundfile as sf,av
from faster_qwen3_tts import FasterQwen3TTS
samples=json.load(urllib.request.urlopen('http://127.0.0.1:3210/api/voice-samples?site=office'))
assert samples and all(p['consent'] for p in samples)
assert len({hashlib.sha256((project/'data/voice-samples'/(p['id']+'.audio')).read_bytes()).hexdigest() for p in samples})==1
p=samples[0];pieces=[]
with av.open(str(project/'data/voice-samples'/(p['id']+'.audio'))) as source:
 converter=av.AudioResampler(format='flt',layout='mono',rate=24000)
 for frame in source.decode(audio=0):
  for out in converter.resample(frame):pieces.append(out.to_ndarray().flatten())
 for out in converter.resample(None):pieces.append(out.to_ndarray().flatten())
reference=r/'reference-for-test.wav';sf.write(reference,np.concatenate(pieces),24000)
start=time.monotonic()
model=FasterQwen3TTS.from_pretrained(str(project/'models/Qwen3-TTS-12Hz-0.6B-Base'),device='cuda',max_seq_len=1024,local_files_only=True)
model.warmup(prefill_len=128)
print('模型加载与图预热秒数',round(time.monotonic()-start,3),flush=True)
results=[]
for index in range(2):
 start=time.monotonic();chunks=[];first=None;timings=[]
 for chunk,sr,timing in model.generate_voice_clone_streaming(text='您好，今天有什么可以帮您？',language='Chinese',ref_audio=str(reference),ref_text=p['transcript'],chunk_size=4,max_new_tokens=384):
  if first is None:first=time.monotonic()-start;print('首块到达',round(first,3),flush=True)
  chunks.append(chunk);timings.append(timing)
 audio=np.concatenate(chunks);duration=len(audio)/sr;elapsed=time.monotonic()-start
 assert np.isfinite(audio).all() and duration>0.3
 out=r/'results';out.mkdir(exist_ok=True);sf.write(out/('faster-qwen-'+str(index+1)+'.wav'),audio,sr)
 result=dict(run=index+1,first_chunk_seconds=round(first,3),total_seconds=round(elapsed,3),audio_seconds=round(duration,3),chunks=len(chunks),chunk_size=4,streaming=True)
 results.append(result);print(json.dumps(result,ensure_ascii=False),flush=True)
(out/'faster-qwen.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
