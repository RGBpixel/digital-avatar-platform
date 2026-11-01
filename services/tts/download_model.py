import os
from pathlib import Path
root = Path(__file__).resolve().parents[2]
os.environ['HF_HOME'] = str(root / 'models' / '.hf-cache')
from huggingface_hub import snapshot_download
snapshot_download('Qwen/Qwen3-TTS-12Hz-0.6B-Base', local_dir=str(root / 'models' / 'Qwen3-TTS-12Hz-0.6B-Base'))
