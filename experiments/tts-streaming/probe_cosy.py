import sys,pathlib
root=pathlib.Path(__file__).parent
sys.path.insert(0,str(root/'deps'));sys.path.insert(0,str(root/'vendor/Matcha-TTS-main'));sys.path.insert(0,str(root/'CosyVoice-main'))
from cosyvoice.cli.cosyvoice import CosyVoice3
print('CosyVoice3导入成功',flush=True)
