"""本地参考音频克隆服务。未安装/验证前不得宣称可用。"""
import base64, io, json, os, threading, hashlib, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from reception_phrases import FIXED_PHRASES
ROOT = Path(__file__).resolve().parents[2]
os.environ['HF_HOME'] = str(ROOT / 'models' / '.hf-cache')
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / 'models' / 'Qwen3-TTS-12Hz-0.6B-Base'
LOCK = threading.Lock()
PROMPTS = {}
AUDIO_CACHE = {}
FIXED_CACHE=ROOT/'data'/'tts-fixed-cache'
FIXED_CACHE.mkdir(parents=True,exist_ok=True)
torch.set_num_threads(min(12, os.cpu_count() or 4))
DEVICE='cuda:0' if torch.cuda.is_available() and os.environ.get('TTS_DEVICE','auto')!='cpu' else 'cpu'
DTYPE=torch.bfloat16 if DEVICE.startswith('cuda') else torch.float32
MODEL = Qwen3TTSModel.from_pretrained(str(MODEL_DIR), device_map=DEVICE, dtype=DTYPE, attn_implementation='sdpa', local_files_only=True)

def decode_audio(raw):
    try:
        audio, sr = sf.read(io.BytesIO(raw), dtype='float32', always_2d=True)
        audio = audio.mean(axis=1)
    except Exception:
        import av
        frames = []
        samples = 0
        with av.open(io.BytesIO(raw)) as container:
            converter = av.AudioResampler(format='flt', layout='mono', rate=24000)
            for frame in container.decode(audio=0):
                for out in converter.resample(frame):
                    values = out.to_ndarray().flatten()
                    samples += len(values)
                    if samples > 24000 * 60:
                        raise ValueError('参考样音超过60秒')
                    frames.append(values)
        if not frames:
            raise ValueError('无法解码参考音频')
        audio, sr = np.concatenate(frames).astype(np.float32), 24000
    if not 3 <= len(audio) / sr <= 60:
        raise ValueError('参考样音需要3至60秒')
    return audio, sr

class Handler(BaseHTTPRequestHandler):
    def message(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        self.message(200, {'ready': True, 'model': 'Qwen3-TTS-12Hz-0.6B-Base', 'referenceVoice': True, 'emotionalInstructions': False, 'device':DEVICE, 'dtype':str(DTYPE), 'gpu':torch.cuda.get_device_name(0) if DEVICE.startswith('cuda') else None})
    def do_POST(self):
        if self.path == '/clear-cache' and not self.headers.get('Origin'):
            with LOCK:
                PROMPTS.clear(); AUDIO_CACHE.clear()
                for file in FIXED_CACHE.glob('*.wav'):file.unlink(missing_ok=True)
            return self.message(200, {'cleared':True})
        if self.path != '/tts':
            return self.message(404, {'error': '接口不存在'})
        if self.headers.get('Origin'):
            return self.message(403, {'error': '请通过平台后台调用'})
        length = int(self.headers.get('Content-Length', '0'))
        if not 0 < length <= 15 * 1024 * 1024:
            return self.message(413, {'error': '请求大小无效'})
        if not LOCK.acquire(blocking=False):
            return self.message(409, {'error': 'TTS 正在生成，请稍后再试'})
        try:
            data = json.loads(self.rfile.read(length))
            text = data.get('text', '')
            if not isinstance(text, str) or not 0 < len(text) <= 500:
                raise ValueError('CPU原型每次支持1至500字，长稿分段生成')
            ref = data['referenceAudio']
            started=time.monotonic()
            raw=base64.b64decode(ref['base64'], validate=True)
            transcript = ref.get('transcript', '').strip()
            reference_key=hashlib.sha256(raw+transcript.encode()).hexdigest()
            audio_key=hashlib.sha256((reference_key+text).encode()).hexdigest()
            now=time.monotonic()
            for cache in (PROMPTS,AUDIO_CACHE):
                for key in list(cache):
                    if now-cache[key][0]>300:del cache[key]
            fixed_file=FIXED_CACHE/(audio_key+'.wav')
            disk_hit=text in FIXED_PHRASES and fixed_file.exists()
            hit=audio_key in AUDIO_CACHE or disk_hit
            if hit:audio_bytes=fixed_file.read_bytes() if disk_hit else AUDIO_CACHE[audio_key][1]
            else:
                with torch.inference_mode():
                    if reference_key not in PROMPTS:
                        reference=decode_audio(raw)
                        prompt=MODEL.create_voice_clone_prompt(ref_audio=reference,ref_text=transcript or None,x_vector_only_mode=not bool(transcript))
                        if len(PROMPTS)>=4:PROMPTS.pop(next(iter(PROMPTS)))
                        PROMPTS[reference_key]=(now,prompt)
                    wavs,sr=MODEL.generate_voice_clone(text=text,language='Chinese',voice_clone_prompt=PROMPTS[reference_key][1],max_new_tokens=2048)
                output=io.BytesIO();sf.write(output,wavs[0],sr,format='WAV',subtype='PCM_16');audio_bytes=output.getvalue()
                if text in FIXED_PHRASES:fixed_file.write_bytes(audio_bytes)
                if len(AUDIO_CACHE)>=16:AUDIO_CACHE.pop(next(iter(AUDIO_CACHE)))
                if len(audio_bytes)<=1024*1024:AUDIO_CACHE[audio_key]=(time.monotonic(),audio_bytes)
            self.send_response(200)
            self.send_header('Content-Type', 'audio/wav')
            self.send_header('X-TTS-Cache', 'hit' if hit else 'miss')
            self.send_header('X-TTS-Elapsed', str(round(time.monotonic()-started,3)))
            self.send_header('X-TTS-Style-Control', 'not-supported')
            self.end_headers()
            self.wfile.write(audio_bytes)
        except Exception as exc:
            self.message(400, {'error': str(exc)})
        finally:
            LOCK.release()
    def log_message(self, fmt, *args):
        # 不打印样音、文字或请求体。
        print('TTS 请求完成', flush=True)

if __name__ == '__main__':
    print('本地 Qwen 参考音频模型已加载：http://127.0.0.1:9880/tts；不支持独立情绪指令', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 9880), Handler).serve_forever()
