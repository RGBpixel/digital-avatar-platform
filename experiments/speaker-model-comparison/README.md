# 声纹模型独立对比
本目录仅作离线对比，不参与当前项目运行配置。

运行：使用项目 .venv-tts/Scripts/python.exe 执行 experiments/speaker-model-comparison/benchmark.py。

结果：results/对比报告.md（阅读版）、results/comparison.json（完整数据）。

模型：当前CAM++从原models目录只读加载；两个候选位于本实验models目录，来源及SHA见source.json。全部使用现有隔离的sherpa-onnx 1.13.8，CPU两线程，无额外修改TTS环境。

协议：固定同一音频、同一预处理，一次预热、九次热推理计时。只比较本机可运行性、速度及小样本分数；不宣称真人准确率或视频声音分离效果。增强样本在内存生成，不写真人声纹或新录音。
