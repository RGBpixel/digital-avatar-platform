# 本机中文声音克隆与流式对比

2026-10-13，RTX5070 Laptop 8GB，PyTorch2.14.1+cu130。使用当前场所已授权样音；三份同名录音文件SHA256一致。目标文字统一为“您好，今天有什么可以帮您？”。不上传样音到任何云端。

| 实现 | 首块可用 | 全部音频完成 | 状态 |
|---|---:|---:|---|
| 现有 Qwen3-TTS0.6B普通接口 | 11.250秒（整段返回） | 11.250秒 | 真实平台请求，非预生成固定句 |
| faster-qwen3-tts0.5.4，第1次 | 0.766秒 | 2.266秒 | 10块，2.96秒音频 |
| faster-qwen3-tts0.5.4，第2次 | 0.250秒 | 1.734秒 | 10块，3.20秒音频 |
| CosyVoice3，第1次 | 3.921秒 | 5.890秒 | 3块，3.36秒音频 |
| CosyVoice3，第2次 | 3.391秒 | 3.391秒 | 短句只产生1块，2.92秒音频 |

首块时间是本机生成器输出，不是网页开始播放时间，也不包括ASR、大模型或加载模型。每种只测两次，生成带随机性，不代表全部文字或平均延迟。音色相似度需本人试听，不能从计时或ASR判断。

faster-Qwen复用当前Qwen0.6B权重与同一样音，ICL克隆模式，chunk_size=4，CUDA Graph预热约14.4秒，首个请求包含样音特征准备；第二次复用特征，仍重新生成完整音频，没有WAV缓存。使用独立兼容SDK与Transformers5.15.1，不修改原Qwen依赖。

CosyVoice使用官方Fun-CosyVoice3-0.5B-2512权重，逐文件SHA256校验，fp16，Windows原生、没有vLLM/TensorRT。音频tokenizer使用CPU ONNX；样音注册另外用时1.016秒。为了兼容新torchaudio，实验只将WAV读取改为SoundFile+同样的resample；配置移除无用训练对象，神经网络与权重不变，原YAML保留。需要进一步加速时不能直接套用150ms宣传值。

当前网页仍使用原Qwen服务，已恢复CUDA运行；此次完成的是独立引擎对比，尚未把faster-Qwen的PCM块接入网页播放器。建议下一步接入同源流式接口与连续PCM播放，并测试首次出声、取消、换场所和多人草稿隔离。不要把这份基准当作网站已达0.25秒回复。

## 来源
- https://github.com/andimarafioti/faster-qwen3-tts （MIT，社区推理实现）
- https://github.com/FunAudioLLM/CosyVoice
- https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512 （Apache-2.0模型卡）
- https://github.com/QwenLM/Qwen3-TTS

## 复现与文件
实验目录 experiments/tts-streaming；benchmark_fast.py、benchmark_cosy.py和results/*.json保留真实结果，results/*.wav为当前样音生成的测试问候。独立虚拟环境只读复用原GPU运行库，各自使用不同deps目录。模型加载时一次只保留一个声音模型在显存，测试结束恢复原服务。
