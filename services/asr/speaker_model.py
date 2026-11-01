import json
MODELS={'campplus':'models/speaker-campplus/model.onnx','campplus-advanced':'models/speaker-campplus-advanced/model.onnx'}
def select_speaker_model(root):
 file=root/'data/speaker-model.json'
 choice=json.loads(file.read_text(encoding='utf-8')).get('model') if file.exists() else 'campplus'
 if choice not in MODELS:raise ValueError('声纹模型配置无效')
 path=root/MODELS[choice]
 if not path.is_file():raise FileNotFoundError('声纹模型文件不存在')
 return choice,path
