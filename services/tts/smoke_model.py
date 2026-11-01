"""用官方公开参考样音做模型生成检查；不创建用户声音档案。"""
import base64, io, json, time, urllib.request
from pathlib import Path
import soundfile as sf
root = Path(__file__).resolve().parents[2]
ref = urllib.request.urlopen('https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-TTS-Repo/clone.wav', timeout=30).read()
transcript = 'Okay. Yeah. I resent you. I love you. I respect you. But you know what? You blew it! And thanks to you.'
payload = json.dumps({'text': '你好，欢迎参观。', 'personality': 'calm', 'emotion': 'neutral', 'intensity': 0.5, 'referenceAudio': {'mimeType': 'audio/wav', 'base64': base64.b64encode(ref).decode(), 'transcript': transcript}}).encode()
start = time.monotonic()
request = urllib.request.Request('http://127.0.0.1:9880/tts', data=payload, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(request, timeout=240) as response:
    output = response.read()
    style = response.headers.get('X-TTS-Style-Control')
audio, sr = sf.read(io.BytesIO(output))
if len(audio) < sr / 2 or abs(audio).max() < 0.001:
    raise RuntimeError('输出音频过短或为空')
file = root / 'data' / 'tts-smoke.wav'
file.parent.mkdir(exist_ok=True)
file.write_bytes(output)
print(json.dumps({'output': str(file), 'sampleRate': sr, 'seconds': len(audio) / sr, 'generationSeconds': round(time.monotonic()-start,2), 'styleControl': style, 'result': 'generated-audio-not-perceptual-verification'}, ensure_ascii=False), flush=True)
