import sys,time,json
from pathlib import Path
import av,numpy as np
r=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(r/'services/asr/sensevoice-runtime'))
import sherpa_onnx
from faster_whisper import WhisperModel
path=r/'models/sensevoice-small-int8/test_wavs/zh.wav'
with av.open(str(path)) as c:
 resampler=av.AudioResampler(format='s16',layout='mono',rate=16000);parts=[]
 for f in c.decode(audio=0):
  for o in resampler.resample(f):parts.append(o.to_ndarray().reshape(-1).astype(np.float32)/32768)
 for o in resampler.resample(None):parts.append(o.to_ndarray().reshape(-1).astype(np.float32)/32768)
a=np.concatenate(parts);rows=[]
m=sherpa_onnx.OfflineRecognizer.from_sense_voice(model=str(r/'models/sensevoice-small-int8/model.int8.onnx'),tokens=str(r/'models/sensevoice-small-int8/tokens.txt'),num_threads=4,language='zh',use_itn=True)
for i in range(2):
 t=time.monotonic();s=m.create_stream();s.accept_waveform(16000,a);m.decode_stream(s);rows.append({'engine':'sensevoice-small-int8','run':i+1,'seconds':round(time.monotonic()-t,3),'text':s.result.text})
del m
m=WhisperModel(str(r/'models/faster-whisper-small'),device='cpu',compute_type='int8',cpu_threads=8,local_files_only=True)
t=time.monotonic();segments,_=m.transcribe(a,language='zh',beam_size=5,condition_on_previous_text=False);text=''.join(s.text for s in segments);rows.append({'engine':'faster-whisper-small','seconds':round(time.monotonic()-t,3),'text':text})
report={'source':'public official model test_wavs/zh.wav, not user microphone','duration':len(a)/16000,'results':rows}
(r/'data/asr-model-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True))
