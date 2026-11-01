import sys,json,base64,pathlib,time,io
root=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'services/face/runtime'))
import cv2 as cv
import numpy as np
from PIL import Image
cv.setNumThreads(2)
det=cv.FaceDetectorYN.create(str(root/'models/face-opencv/yunet.onnx'),'',(320,320),.85,.3,20)
rec=cv.FaceRecognizerSF.create(str(root/'models/face-opencv/sface.onnx'),'')
def infer(b):
 started=time.perf_counter()
 if b.get('op')=='health':return {'ready':True,'engine':'YuNet + SFace','device':'cpu'}
 raw=base64.b64decode(b['image'].split(',')[-1],validate=True)
 if len(raw)>350000:raise ValueError('图像过大')
 with Image.open(io.BytesIO(raw)) as im:
  if im.width>1280 or im.height>960:raise ValueError('图像尺寸过大')
 image=cv.imdecode(np.frombuffer(raw,np.uint8),cv.IMREAD_COLOR)
 if image is None:raise ValueError('图片无效')
 h,w=image.shape[:2];det.setInputSize((w,h));_,faces=det.detect(image)
 result=[]
 for face in (faces if faces is not None else []):
  aligned=rec.alignCrop(image,face);v=rec.feature(aligned).flatten();v=v/np.linalg.norm(v)
  # Landmark geometry is a quality heuristic, not a pose or liveness model.
  eyes=abs(float(face[4]-face[6]));nose=float(face[8]);middle=float(face[4]+face[6])/2
  pose_ok=eyes>12 and abs(nose-middle)<eyes*.4
  frontal=pose_ok and min(face[2],face[3])>=90
  recognition_ready=pose_ok and min(face[2],face[3])>=50
  ok,jpg=cv.imencode('.jpg',aligned,[cv.IMWRITE_JPEG_QUALITY,90])
  result.append({'box':[round(float(x),1) for x in face[:4]],'embedding':v.tolist(),'frontal':bool(frontal),'recognitionReady':bool(recognition_ready),'portrait':'data:image/jpeg;base64,'+base64.b64encode(jpg).decode()})
 return {'count':len(result),'faces':result,'elapsedMs':round((time.perf_counter()-started)*1000)}
for line in sys.stdin:
 try:
  b=json.loads(line);out={'id':b['id'],'result':infer(b)}
 except Exception as e:out={'id':locals().get('b',{}).get('id'),'error':str(e)}
 print(json.dumps(out,ensure_ascii=True),flush=True)
