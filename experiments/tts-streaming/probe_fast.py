import sys,pathlib,inspect
r=pathlib.Path(__file__).parent;sys.path.insert(0,str(r/'fastdeps'))
from faster_qwen3_tts import FasterQwen3TTS
print('FastQwen导入成功',flush=True)
print(inspect.signature(FasterQwen3TTS.from_pretrained),flush=True)
print(inspect.signature(FasterQwen3TTS.generate_voice_clone_streaming),flush=True)
