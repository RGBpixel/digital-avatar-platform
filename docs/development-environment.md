# 本机开发环境（2026-10-12）
Windows 内核 10.0.26200；Intel Core Ultra 9 275HX；24 逻辑核心；约 63 GiB 内存。
系统 PATH 未找到 Node/Git；python 命令访问失败。已验证 Codex 捆绑 Node 24.19.0、Python 3.12.14、Git 2.53.0。启动脚本使用 %USERPROFILE% 下的 Codex 运行时，不修改系统 PATH，无需 npm 安装。
UE 未在 PATH 或默认 C:/Program Files/Epic Games 目录发现；其他自定义安装位置未全面扫描。nvidia-smi 返回 NVML 初始化失败，显卡型号/显存未确认，不据此判定没有 GPU。第一阶段不需要 UE 或 GPU。
依赖路径：%USERPROFILE%/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe。后续若 Codex 清理运行时，可安装 Node.js 24，并调整启动脚本。
项目无 GitHub 远程配置；未创建或发布云资源。

声音扩展：项目 .venv-tts 独立Python环境，CPU版Torch与Qwen3-TTS0.6B参考音频模型已安装、实际生成通过。权重位于 models/，约2.4GB，默认不使用GPU或云资源。精确依赖版本见 services/tts/environment.lock.txt，测试详情见 verification.md。
