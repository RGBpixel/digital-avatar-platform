import secrets,time,threading
import numpy as np
class SpeakerGate:
 def __init__(self,extractor,threshold=.65,clock=time.monotonic):
  self.extractor=extractor;self.threshold=threshold;self.clock=clock;self.sessions={};self.confirmed=set();self.lock=threading.Lock()
 def embedding(self,audio):
  frames=[i for i in range(0,len(audio)-320,320) if float(np.sqrt(np.mean(audio[i:i+320]**2)))>.002]
  if len(frames)<25:raise ValueError('声音样本太短或太轻，请清晰说一句完整的话后重新唤醒')
  audio=np.ascontiguousarray(audio[frames[0]:frames[-1]+320]);s=self.extractor.create_stream();s.accept_waveform(16000,audio);s.input_finished()
  if not self.extractor.is_ready(s):raise ValueError('声音样本不足，请重新说话')
  v=np.asarray(self.extractor.compute(s),dtype=np.float32);norm=float(np.linalg.norm(v))
  if not np.isfinite(v).all() or norm<1e-8:raise ValueError('声纹提取失败')
  return v/norm
 def enroll(self,audio,site):
  v=self.embedding(audio)
  with self.lock:
   self.prune()
   if len(self.sessions)>=16:raise ValueError('声纹会话过多，请先结束原会话')
   token=secrets.token_urlsafe(24);self.sessions[token]=(site,[v],self.clock()+600)
  return token
 def prune(self):
  for k in list(self.sessions):
   if self.sessions[k][2]<=self.clock():
    del self.sessions[k];self.confirmed.discard(k)
 def verify(self,audio,token,site,strict=False):
  with self.lock:
   self.prune();record=self.sessions.get(token)
   if not record or record[0]!=site:return {'accepted':False,'reason':'expired','message':'声纹锁定已过期，请重新唤醒'}
   references=record[1]
  try:v=self.embedding(audio)
  except ValueError as e:return {'accepted':False,'reason':'short','message':str(e)}
  score=max(float(np.dot(reference,v)) for reference in references);scores=[]
  # Check overlapping speech windows as well as the complete recording.
  # A matching first sentence must not authorize a different voice later.
  if strict and len(audio)>32000:
   for start in range(0,len(audio),16000):
    part=audio[start:start+32000]
    if len(part)<32000:continue
    energy=np.asarray([float(np.sqrt(np.mean(part[i:i+320]**2))) for i in range(0,len(part)-320,320)])
    speech_floor=max(.002,float(np.percentile(energy,95))*.12)
    if np.count_nonzero(energy>speech_floor)<60:continue
    try:scores.append(max(float(np.dot(reference,self.embedding(part))) for reference in references))
    except ValueError:continue
  lowest=min(scores) if scores else score
  window_threshold=max(.4,self.threshold-.15)
  accepted=score>=self.threshold and (not strict or lowest>=window_threshold)
  uncertain=not accepted and score>=self.threshold-.2 and lowest>=window_threshold-.15
  return {'accepted':accepted,'verificationMode':'strict' if strict else 'conversation','score':round(score,4),'lowestWindowScore':round(lowest,4),'checkedWindows':len(scores),'threshold':self.threshold,'windowThreshold':round(window_threshold,3),'reason':'matched' if accepted else 'uncertain' if uncertain else 'other-speaker','message':'已匹配当前说话者' if accepted else '声纹相近但确认不足，请清晰说完整一句，或重新唤醒锁定' if uncertain else '已忽略声纹明显不一致或混入其他声音的录音'}
 def update(self,audio,token,site):
  v=self.embedding(audio)
  with self.lock:
   self.prune();record=self.sessions.get(token)
   if not record or record[0]!=site:raise ValueError('声纹会话已失效，请重新唤醒')
   # Drop the unconfirmed wake reference on the first explicit correction.
   # Keep only user-confirmed examples; verification never learns by itself.
   replaced=token not in self.confirmed
   refs=[] if replaced else list(record[1])
   if not any(float(np.dot(ref,v))>=.98 for ref in refs):refs.append(v)
   refs=refs[-3:];self.confirmed.add(token);self.sessions[token]=(site,refs,record[2])
  return {'updated':True,'references':len(refs),'referenceReplaced':replaced}
 def release(self,token,site):
  with self.lock:
   if token in self.sessions and self.sessions[token][0]==site:
    del self.sessions[token];self.confirmed.discard(token)
