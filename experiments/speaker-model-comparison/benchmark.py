import sys,time,json,hashlib,statistics,platform,os
from pathlib import Path
import numpy as np,av
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'services/asr/sensevoice-runtime'),str(ROOT/'services/asr')]
import sherpa_onnx
from speaker_gate import SpeakerGate
OUT=Path(__file__).parent/'results';OUT.mkdir(exist_ok=True)
def load(path):
 with av.open(str(path)) as container:
  resampler=av.AudioResampler(format='s16',layout='mono',rate=16000);parts=[]
  for frame in container.decode(audio=0):
   for chunk in resampler.resample(frame):parts.append(chunk.to_ndarray().reshape(-1).astype(np.float32)/32768)
  for chunk in resampler.resample(None):parts.append(chunk.to_ndarray().reshape(-1).astype(np.float32)/32768)
 return np.ascontiguousarray(np.concatenate(parts),dtype=np.float32)
def rms(a):return float(np.sqrt(np.mean(a*a)))
def blend(target,noise,snr):
 background=np.resize(noise,len(target));background=background*(rms(target)/max(rms(background),1e-9))*10**(-snr/20)
 mixed=target+background;return np.ascontiguousarray(mixed/max(1.,float(np.max(np.abs(mixed)))),dtype=np.float32)
def percentile(a,p):return round(float(np.percentile(a,p)),2)
inputs={'long-reference':'data/speaker-same-person-0.wav','short-reference':'data/synthetic-wake-test.wav','same-other-sentence':'data/speaker-same-person-1.wav','different-voice':'models/sensevoice-small-int8/test_wavs/zh.wav'}
audio={k:load(ROOT/v) for k,v in inputs.items()};q=audio['same-other-sentence'];other=audio['different-voice'];rng=np.random.default_rng(20261014)
conditions={'same-clean':q,'same-quieter-12db':q*.25118864,'same-white-noise-15db':blend(q,rng.normal(0,1,len(q)).astype(np.float32),15),'same-other-speech-6db':blend(q,other,6),'same-other-speech-0db':blend(q,other,0),'different-clean':other,'different-quieter-12db':other*.25118864,'same-then-other':np.concatenate([q,other])}
models={'CAM++ current':ROOT/'models/speaker-campplus/model.onnx','CAM++ Advanced':Path(__file__).parent/'models/campplus-advanced/model.onnx','ERes2NetV2':Path(__file__).parent/'models/eres2net-v2/model.onnx'}
report={'date':'2026-10-14','environment':{'python':platform.python_version(),'processor':platform.processor(),'provider':'cpu','threads':2,'sherpa_onnx':getattr(sherpa_onnx,'__version__','unknown')},'scope':'Offline feasibility, extraction speed and score separation only; synthetic same speaker plus one public other speaker. Not a live microphone or human population accuracy benchmark. No EER/FAR/FRR claims. Running platform model and threshold unchanged.','protocol':{'warmups':1,'timingRuns':9,'timingAudio':'same-other-sentence','timingIncludes':'energy trimming + feature extraction + normalized embedding; excludes loading, disk decode, recording, ASR, LLM, TTS','references':['long-reference','short-reference'],'mixMeaning':'digitally mixed, not a physical phone loudspeaker or measured room acoustics','scores':'cosine similarities, no shared decision threshold; larger score is not automatically better across models'},'inputs':{},'models':[]}
for key,path in inputs.items():
 p=ROOT/path;report['inputs'][key]={'path':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'seconds':round(len(audio[key])/16000,3),'source':'public official model test audio' if key=='different-voice' else 'Windows synthetic Chinese voice; not user recording'}
for name,path in models.items():
 print('Testing '+name,flush=True);started=time.perf_counter();extractor=sherpa_onnx.SpeakerEmbeddingExtractor(sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=str(path),num_threads=2,provider='cpu'));gate=SpeakerGate(extractor);load_ms=(time.perf_counter()-started)*1000
 refs={k:gate.embedding(audio[k]) for k in ['long-reference','short-reference']};gate.embedding(q);times=[]
 for _ in range(9):
  started=time.perf_counter();gate.embedding(q);times.append((time.perf_counter()-started)*1000)
 scores={}
 for condition,values in conditions.items():
  vector=gate.embedding(values);scores[condition]={key:round(float(np.dot(reference,vector)),4) for key,reference in refs.items()}
 row={'model':name,'modelBytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'embeddingDim':extractor.dim,'loadMs':round(load_ms,2),'medianMs':percentile(times,50),'p95Ms':percentile(times,95),'timingRunsMs':[round(t,2) for t in times],'scores':scores,'cleanSeparation':{ref:round(scores['same-clean'][ref]-scores['different-clean'][ref],4) for ref in refs}}
 report['models'].append(row);print(json.dumps(row,ensure_ascii=True),flush=True)
 del gate,extractor
(OUT/'comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 声纹模型离线对比（2026-10-14）','','运行方式：CPU两线程，固定同一中文合成句子，预热一次、计时九次。提取耗时不含录音、云端回答或TTS。','','**仅使用同一个Windows合成声音的三条音频和另一条公开中文声音，不能据此宣布真人准确率、误拒率或视频干扰过滤成功。**','','| 模型 | 文件MB | 提取中位数ms | P95 ms | 完整参考：本人不同句子 | 完整参考：另一声音 | 短参考：本人不同句子 |','|---|---:|---:|---:|---:|---:|---:|']
for row in report['models']:
 s=row['scores'];lines.append(f"| {row['model']} | {row['modelBytes']/1000000:.1f} | {row['medianMs']} | {row['p95Ms']} | {s['same-clean']['long-reference']} | {s['different-clean']['long-reference']} | {s['same-clean']['short-reference']} |")
lines+=['','分数是余弦相似度，不同模型不能共用0.65阈值直接比较准确率。','','## 加入干扰后的本人语音分数（完整参考）','','| 模型 | 轻声-12dB | 白噪声15dB | 目标比另一声音响6dB | 双人同响0dB | 本人之后接另一声音 |','|---|---:|---:|---:|---:|---:|']
for row in report['models']:
 s=row['scores'];keys=['same-quieter-12db','same-white-noise-15db','same-other-speech-6db','same-other-speech-0db','same-then-other'];lines.append('| '+row['model']+' | '+' | '.join(str(s[k]['long-reference']) for k in keys)+' |')
lines+=['','混音中包含本人，分数高并不代表已经滤掉旁人的话；本测试不执行目标人声分离，也不比较混音的转写污染。此混音没有模拟手机扬声器、回声、距离及房间。','','短参考是1条独立唤醒句；完整参考是另1条较长句。两者音素内容和时长均不同，不能把差异全部归因于时长。','','每个模型独立提取参考与测试特征，没有跨模型混用声纹。所有阈值均待真人、同设备、不同句子和非本人负例标定。不得用这份小样本结果训练阈值后再宣称测试准确率。','','来源与哈希见各模型source.json；所有增强只在内存中生成，没有新增真人录音或生物特征持久化。运行中的模型未替换。']
(OUT/'对比报告.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
