# 本机中文识别切换
2026-10-14：用户反馈WhisperSmall将“你好宝贝”转写为无关文字，因此接入SenseVoiceSmall INT8（约239MB）作为本机默认识别。CPU四线程运行，不与GPU声音模型争用显存。
官方转换模型：csukuangfj/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17；模型仓库许可文件保留，文件SHA记录在models/sensevoice-small-int8/source.json。原生库sherpa-onnx和sherpa-onnx-core均1.13.8，隔离在services/asr/sensevoice-runtime；TTS/Whisper依赖未替换。初次安装的sensevoice-deps目录保留且不再使用。
同一5.592秒公开中文文件：SenseVoice两次推理0.140/0.141秒，WhisperSmall1.031秒。两者首词分别转写“开饭”和“开放”，无人工真值评分，不据此宣称准确率胜出。实际项目HTTP接口SenseVoice推理0.109秒。
Windows中文合成“你好宝贝”，1.724秒音频，实际ASR接口结果“你好，宝贝。”，推理0.063秒；唤醒匹配可通过。见data/sensevoice-wake-test.json。这是合成音频而非用户现场麦克风，不能代替真人验证。先前自定义样音TTS合成测试被ASR拒绝，不计为通过。
运行选择由data/sensevoice.enabled控制，启动项目.cmd使用现有ASR启动脚本，健康回执展示sensevoice-small-int8。Whisper模型保留；开发者回退时移除该标记并重启经过核验的services/asr/server.py进程即可。SenseVoice当前不使用Whisper的hotwords参数；前端唤醒词仍由实际转写文本匹配，不强制替换为期望词。
收音阈值默认从0.006降到0.002，界面可选择0.001/0.002/0.006。较高灵敏度会增加噪声触发；停顿与长度兜底维持，现场输入质量和识别准确率待用户验收。22项输入/ASR测试通过。持续唤醒仍为转写式检测，专用关键词模型待实现。
来源：https://k2-fsa.github.io/sherpa/onnx/sense-voice/pretrained.html
