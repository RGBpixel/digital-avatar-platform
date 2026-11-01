import sys,pathlib,io
r=pathlib.Path(__file__).parent;sys.path.insert(0,str(r/'deps'));sys.path.insert(0,str(r/'vendor/Matcha-TTS-main'));sys.path.insert(0,str(r/'CosyVoice-main'))
from hyperpyyaml import load_hyperpyyaml
m=r/'models/Fun-CosyVoice3-0.5B-2512';s=(m/'cosyvoice3.yaml').read_text()
a=s.index('# gan related module');b=s.index('# processor functions');s=s[:a]+s[b:]
a=s.index('parquet_opener:');b=s.index('get_tokenizer:');s=s[:a]+s[b:]
a=s.index('tokenize:');b=s.index('feat_extractor:');s=s[:a]+s[b:];s=s[:s.index('compute_fbank:')]
c=load_hyperpyyaml(io.StringIO(s),overrides={'qwen_pretrain_path':str(m/'CosyVoice-BlankEN')})
print('CosyVoice推理配置实例化通过',flush=True)
