import os,io,json,time,threading,pathlib
os.environ['HF_HUB_OFFLINE']='1'
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import unquote
import av
import numpy as np
root=pathlib.Path(__file__).resolve().parents[2]
size='small' if (root/'models'/'faster-whisper-small'/'source.json').exists() else 'base'
engine='sensevoice-small-int8' if (root/'data/sensevoice.enabled').exists() and (root/'models/sensevoice-small-int8/model.int8.onnx').exists() else 'faster-whisper-'+size
speaker_model=None;speaker_gate=None;speaker_error=None;model=None;error=None;lock=threading.Lock()
def load():
 global model,error,speaker_gate,speaker_error,speaker_model
 try:
  if engine=='sensevoice-small-int8':
   import sys
   sys.path.insert(0,str(root/'services/asr/sensevoice-runtime'))
   import sherpa_onnx
   model=sherpa_onnx.OfflineRecognizer.from_sense_voice(model=str(root/'models'/engine/'model.int8.onnx'),tokens=str(root/'models'/engine/'tokens.txt'),num_threads=4,provider='cpu',language='zh',use_itn=True)
  else:
   from faster_whisper import WhisperModel
   model=WhisperModel(str(root/'models'/engine),device='cpu',compute_type='int8',cpu_threads=8,local_files_only=True)
 except Exception as e:error=type(e).__name__
 try:
  import sys
  sys.path.insert(0,str(root/'services/asr/sensevoice-runtime'))
  import sherpa_onnx
  from speaker_gate import SpeakerGate
  from speaker_model import select_speaker_model
  selected_speaker,selected_path=select_speaker_model(root)
  config=sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=str(selected_path),num_threads=2,provider='cpu')
  speaker_gate=SpeakerGate(sherpa_onnx.SpeakerEmbeddingExtractor(config))
  speaker_model=selected_speaker
 except Exception as e:speaker_error=type(e).__name__
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send_json(self,status,data):
  blob=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(blob)
 def do_GET(self):
  if self.path!='/health':return self.send_json(404,{'error':'not found'})
  self.send_json(200,{'ready':model is not None,'engine':engine,'error':error,'local':True,'speakerReady':speaker_gate is not None,'speakerError':speaker_error,'speakerModel':speaker_model,'personVoiceEmbedding':True})
 def do_POST(self):
  if self.headers.get('Origin'):return self.send_json(403,{'error':'Only local backend may call'})
  if self.path not in ['/transcribe','/speaker-lock','/speaker-release','/speaker-update','/speaker-embedding']:return self.send_json(404,{'error':'not found'})
  site=self.headers.get('X-Speaker-Site','office')
  token=self.headers.get('X-Speaker-Session','')
  speaker_mode=self.headers.get('X-Speaker-Mode','conversation')
  if speaker_mode not in ['conversation','strict']:return self.send_json(400,{'error':'声纹模式无效'})
  if len(site)>100 or len(token)>100:return self.send_json(400,{'error':'声纹会话参数无效'})
  if self.path=='/speaker-release':
   if speaker_gate:speaker_gate.release(token,site)
   return self.send_json(200,{'released':True})
  hotwords=unquote(self.headers.get('X-ASR-Hotwords',''))
  if len(hotwords)>30:return self.send_json(400,{'error':'唤醒短语过长'})
  length=int(self.headers.get('Content-Length','0'))
  if length<100 or length>4*1024*1024:return self.send_json(413,{'error':'录音大小无效，最多4MB'})
  audio_bytes=self.rfile.read(length)
  if model is None:return self.send_json(503,{'error':'本地识别模型尚未就绪，请稍候'})
  try:
   pieces=[];decoded=0
   with av.open(io.BytesIO(audio_bytes),mode='r') as container:
    resampler=av.AudioResampler(format='s16',layout='mono',rate=16000)
    for frame in container.decode(audio=0):
     for output in resampler.resample(frame):
      samples=output.to_ndarray().reshape(-1).astype(np.float32)/32768.0
      decoded+=len(samples)
      if decoded>35*16000:raise ValueError('Audio too long')
      pieces.append(samples)
    for output in resampler.resample(None):pieces.append(output.to_ndarray().reshape(-1).astype(np.float32)/32768.0)
   audio=np.concatenate(pieces) if pieces else np.zeros(0,dtype=np.float32)
   seconds=len(audio)/16000
   if seconds<0.3 or seconds>35:return self.send_json(400,{'error':'录音需为0.3–35秒'})
   rms=float(np.sqrt(np.mean(audio**2)))
   if rms<0.0005:return self.send_json(200,{'text':'','local':True,'duration':seconds,'rms':rms,'reason':'音频接近静音'})
   if not lock.acquire(blocking=False):return self.send_json(429,{'error':'本机识别正在处理另一段录音，请稍后重试'})
   try:
    started=time.monotonic()
    if self.path=='/speaker-embedding':
     if speaker_gate is None:return self.send_json(503,{'error':'声纹模型尚未就绪'})
     try:
      voiced=sum(float(np.sqrt(np.mean(audio[i:i+320]**2)))>.002 for i in range(0,len(audio)-320,320))*.02
      if voiced<.8:return self.send_json(400,{'error':'有效说话太短，请说：你好宝贝，我来了'})
      return self.send_json(200,{'embedding':speaker_gate.embedding(audio).tolist(),'model':speaker_model,'voicedSeconds':round(voiced,2),'local':True})
     except ValueError as e:return self.send_json(400,{'error':str(e)})
    if self.path=='/speaker-update':
     if speaker_gate is None:return self.send_json(503,{'error':'声纹模型尚未就绪'})
     try:return self.send_json(200,speaker_gate.update(audio,token,site))
     except ValueError as e:return self.send_json(400,{'error':str(e)})
    if self.path=='/speaker-lock':
     if speaker_gate is None:return self.send_json(503,{'error':'声纹模型尚未就绪'})
     try:return self.send_json(200,{'sessionId':speaker_gate.enroll(audio,site),'local':True,'expiresIn':600,'speakerModel':speaker_model})
     except ValueError as e:return self.send_json(400,{'error':str(e)})
    speaker=None
    speaker_ms=0
    if token:
     if speaker_gate is None:return self.send_json(503,{'error':'声纹模型不可用，本轮不发送'})
     speaker_started=time.monotonic()
     speaker=speaker_gate.verify(audio,token,site,strict=speaker_mode=='strict')
     speaker_ms=round((time.monotonic()-speaker_started)*1000,1)
     if not speaker['accepted']:return self.send_json(200,{'text':'','engine':engine,'speaker':speaker,'local':True})
    asr_started=time.monotonic()
    if engine=='sensevoice-small-int8':
     stream=model.create_stream()
     stream.accept_waveform(16000,audio)
     model.decode_stream(stream)
     text=stream.result.text.strip()
    else:
     segments,info=model.transcribe(audio,language='zh',task='transcribe',beam_size=5,hotwords=hotwords or None,vad_filter=False,condition_on_previous_text=False)
     text=''.join(s.text for s in segments if s.no_speech_prob<0.8).strip()
    self.send_json(200,{'text':text,'local':True,'engine':engine,'duration':seconds,'rms':rms,'elapsed':round(time.monotonic()-started,3),'speaker':speaker,'timing':{'speakerMs':speaker_ms,'asrMs':round((time.monotonic()-asr_started)*1000,1)}})
   finally:lock.release()
  except Exception:self.send_json(400,{'error':'音频无法解码或识别失败，请重新录制'})
threading.Thread(target=load,daemon=True).start()
print('Local ASR listening on 127.0.0.1:9882',flush=True)
ThreadingHTTPServer(('127.0.0.1',9882),Handler).serve_forever()
