"""本机流式Qwen服务；使用独立兼容环境和原Qwen权重。"""
import sys,pathlib,os,json,io,time,base64,hashlib,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'experiments/tts-streaming/fastdeps'))
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import torch,numpy as np,soundfile as sf,av
from faster_qwen3_tts import FasterQwen3TTS
MODEL=FasterQwen3TTS.from_pretrained(str(ROOT/'models/Qwen3-TTS-12Hz-0.6B-Base'),device='cuda',max_seq_len=1024,local_files_only=True)
MODEL.warmup(prefill_len=128)
LOCK=threading.Lock();PROMPTS={}
def prompt_for(ref):
 raw=base64.b64decode(ref['base64'],validate=True);text=ref.get('transcript','').strip()
 key=hashlib.sha256(raw+text.encode()).hexdigest();now=time.monotonic()
 for k in list(PROMPTS):
  if now-PROMPTS[k][0]>300:del PROMPTS[k]
 if key not in PROMPTS:
  parts=[];total=0
  with av.open(io.BytesIO(raw)) as source:
   converter=av.AudioResampler(format='flt',layout='mono',rate=24000)
   for frame in source.decode(audio=0):
    for part in converter.resample(frame):
     values=part.to_ndarray().flatten();total+=len(values)
     if total>60*24000:raise ValueError('样音超过60秒')
     parts.append(values)
   for part in converter.resample(None):parts.append(part.to_ndarray().flatten())
  audio=np.concatenate(parts) if parts else np.zeros(0)
  if not 3<=len(audio)/24000<=60:raise ValueError('样音需要3至60秒')
  audio=np.concatenate([audio,np.zeros(12000,dtype=np.float32)])
  with torch.inference_mode():prompt=MODEL.model.create_voice_clone_prompt(ref_audio=(audio,24000),ref_text=text or None,x_vector_only_mode=not bool(text))
  if len(PROMPTS)>=4:PROMPTS.pop(next(iter(PROMPTS)))
  PROMPTS[key]=(now,prompt)
 return PROMPTS[key][1],text
class Handler(BaseHTTPRequestHandler):
 protocol_version='HTTP/1.1'
 def log_message(self,*args):pass
 def json(self,status,data):
  payload=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
 def do_GET(self):
  if self.path!='/health':return self.json(404,{'error':'not found'})
  self.json(200,{'ready':True,'model':'Qwen3-TTS-12Hz-0.6B-Base','engine':'faster-qwen3-tts','streaming':True,'device':'cuda:0','referenceVoice':True,'emotionalInstructions':False})
 def chunk(self,data):
  payload=(json.dumps(data,separators=(',',':'))+'\n').encode();self.wfile.write(('%X\r\n'%len(payload)).encode()+payload+b'\r\n');self.wfile.flush()
 def do_POST(self):
  if self.headers.get('Origin'):return self.json(403,{'error':'请通过平台后台调用'})
  if self.path=='/clear-cache':
   with LOCK:PROMPTS.clear();MODEL._voice_prompt_cache.clear()
   return self.json(200,{'cleared':True})
  if self.path not in ['/tts','/tts-stream']:return self.json(404,{'error':'not found'})
  size=int(self.headers.get('Content-Length','0'))
  if not 0<size<=15*1024*1024:return self.json(413,{'error':'请求大小无效'})
  data=json.loads(self.rfile.read(size));text=data.get('text','')
  if not isinstance(text,str) or not 0<len(text)<=500:return self.json(400,{'error':'每次生成需为1至500字'})
  if not LOCK.acquire(False):return self.json(409,{'error':'声音模型正在处理其他请求，请稍后再试'})
  streaming=self.path=='/tts-stream';begun=False;generator=None
  try:
   prompt,reftext=prompt_for(data['referenceAudio'])
   generator=MODEL.generate_voice_clone_streaming(text=text,language='Chinese',voice_clone_prompt=prompt,ref_text=reftext,chunk_size=4,max_new_tokens=1024)
   chunks=[];frames=0
   for audio,sr,timing in generator:
    audio=np.asarray(audio).reshape(-1)
    if not np.isfinite(audio).all():raise ValueError('模型音频无效')
    if not len(audio):continue
    frames+=len(audio)
    if frames>120*sr:raise ValueError('生成音频过长')
    if streaming:
     if not begun:
      self.send_response(200);self.send_header('Content-Type','application/x-ndjson');self.send_header('Cache-Control','no-store');self.send_header('Transfer-Encoding','chunked');self.end_headers();begun=True
     pcm=(np.clip(audio,-1,1)*32767).astype('<i2').tobytes()
     self.chunk({'type':'audio','sampleRate':sr,'pcm':base64.b64encode(pcm).decode()})
    else:chunks.append(audio)
   if streaming:
    if not begun:raise ValueError('模型没有生成声音')
    self.chunk({'type':'done'});self.wfile.write(b'0\r\n\r\n');self.wfile.flush()
   else:
    if not chunks:raise ValueError('模型没有生成声音')
    out=io.BytesIO();sf.write(out,np.concatenate(chunks),sr,format='WAV',subtype='PCM_16');payload=out.getvalue()
    self.send_response(200);self.send_header('Content-Type','audio/wav');self.send_header('X-TTS-Style-Control','not-supported');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
  except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass
  except Exception as e:
   if begun:
    try:self.chunk({'type':'error','message':'声音生成失败，请重新开始'});self.wfile.write(b'0\r\n\r\n');self.wfile.flush()
    except OSError:pass
   else:self.json(400,{'error':'声音生成失败：'+type(e).__name__})
  finally:
   if generator:generator.close()
   LOCK.release()
print('本机流式Qwen已预热，监听9880',flush=True)
ThreadingHTTPServer(('127.0.0.1',9880),Handler).serve_forever()
