import sys,json,pathlib,base64,io,time
root=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'services/vision/runtime'))
sys.path.insert(0,str(root/'services/face/runtime'))
from PIL import Image
import numpy as np
from rapidocr_onnxruntime import RapidOCR
engine=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=1)
def process(b):
 if b.get('consent') is not True:raise ValueError('请先允许本机文字识别')
 value=b.get('image','')
 if not value.startswith('data:image/jpeg;base64,') or len(value)>500000:raise ValueError('图片格式或大小无效')
 raw=base64.b64decode(value.split(',')[1],validate=True)
 with Image.open(io.BytesIO(raw)) as im:
  if im.width>1280 or im.height>960:raise ValueError('图片尺寸过大')
  image=np.array(im.convert('RGB'))[:,:,::-1].copy()
 started=time.perf_counter();result,_=engine(image)
 lines=[{'text':str(x[1])[:60],'score':round(float(x[2]),3)} for x in (result or []) if float(x[2])>=.85 and len(str(x[1]))<=60][:5]
 answer='我读到的字样是：'+ '、'.join(x['text'] for x in lines)+'。这是文字识别结果，不能据此核实品牌或真假。' if lines else '没有读到清晰的衣服文字标识，请将标识放到镜头中央、靠近一些并保持不动；纯图案Logo目前不能可靠确认品牌。'
 return {'local':True,'engine':'RapidOCR-CPU','model':'local-ocr','savedImage':False,'textLines':lines,'observation':{'visible':False,'objects':[],'brands':[]},'greeting':answer,'elapsedMs':round((time.perf_counter()-started)*1000)}
for line in sys.stdin:
 try:
  b=json.loads(line);out={'id':b['id'],'result':process(b)}
 except Exception as e:out={'id':locals().get('b',{}).get('id'),'error':str(e)}
 print(json.dumps(out,ensure_ascii=True),flush=True)
