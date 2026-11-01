# 类VAM开源实时数字人路线对比

核对日期：2026-10-19。只依据作者GitHub、Hugging Face模型卡、官方项目页；没有安装模型或在4090服务器实测。用户服务器为4090和128GB系统内存，显存容量/占用及Linux环境尚待检查。

## 结论
确实存在与VAM更接近的流式生成式路线，不必把候选范围限于LiveTalking/MuseTalk。优先验证SoulX-FlashHead Lite在单4090的真实音频驱动表现；但它定位talking-head，不能把头部实时能力包装成全身可控动作。身体动作、表情编辑优先研究SoulX-LiveAct，现有单4090不应承诺实时。LiveAvatar、FlashTalk适合对照研究，官方实时条件为大显存多卡。

| 项目 | 代码/权重 | 官方公开条件 | 对当前项目的意义 |
|---|---|---|---|
| SoulX-FlashHead Lite / Pro，1.3B | GitHub Soul-AILab/SoulX-FlashHead；HF Soul-AILab/SoulX-FlashHead-1_3B | Lite单4090报告96FPS或三路25+FPS；Pro单4090约10.8FPS、双5090可25+FPS | 最适合单4090先验证，但主要为流式头像生成，完整对话、身体控制须另做 |
| SoulX-LiveAct，约18B | GitHub Soul-AILab/SoulX-LiveAct；HF Soul-AILab/LiveAct | 双H100/H200报告20FPS；支持4090/5090卸载运行，单5090官方约6FPS | 动作/情绪控制和长时生成更接近目标；能运行不等于能实时，fps参数不代表实测速度 |
| SoulX-FlashTalk，14B | GitHub Soul-AILab/SoulX-FlashTalk；HF Soul-AILab/SoulX-FlashTalk-14B | 官方32FPS/0.87秒启动为8×H800；单卡原说明>64GB，CPUoffload约40GB | 与VAM接近的DiT、蒸馏、无限流式路线，标准24GB4090不是其官方实时配置 |
| LiveAvatar，14B | GitHub Alibaba-Quark/LiveAvatar；HF Quark-Vision/Live-Avatar，另需Wan2.2-S2V-14B | v1.1说明FP8可48GB推理；稳定45+FPS为多H800；单GPU分支有离线模式 | 技术路径接近，但LoRA只有1.35GB并不意味着整套只需该显存，不适合首选单4090 |

所有数字是作者条件下的公开报告，不能横向视为同分辨率、同批量、同音频块、同端到端延迟。推理FPS、最终播放FPS、首视频块延迟和停嘴到首音/首帧必须分别测量。

## 相近但暂不作为可装方案
- StreamAvatar（streamavatar.github.io，清华/腾讯混元等）：官方展示talk/listen和身体动作、双H800实时；核对项目页未提供模型代码/权重入口，不能把其他同名DyStream派生仓库误认为其实现。
- AptAvatar：GitHub和HF确有项目，README仍有“当前代码为主、权重待发布/占位”说明，与模型页状态需要进一步核对；不把有README等同于可复现实时部署。
- Hallo-Live：音视频联合生成更激进，官方双H200约20.38FPS，不是单4090首选。

## 许可证
FlashHead代码为Apache2.0，模型卡列出组件分别授权：DiT和WanVAE等Apache2.0，但Lite的LTX0.9 VAE为Open-RAIL-M，不能把所有权重重标成Apache2.0。商业发布按实际组件和版本核对；本次没有作法律结论。

## 接入本项目
保留千问/豆包、声音、人员卡片、长期记忆、个人提醒；新增可替换音频到视频服务。笔记本负责摄像头/麦克风和播放，4090服务器负责视频生成。先单路人像实测首帧、音画同步和打断，再扩到全身；不上传用户素材到公共Space。未经用户另行授权不联系作者或付费云服务。

## 直接来源
- https://github.com/Soul-AILab/SoulX-FlashHead
- https://huggingface.co/Soul-AILab/SoulX-FlashHead-1_3B
- https://github.com/Soul-AILab/SoulX-LiveAct
- https://huggingface.co/Soul-AILab/LiveAct
- https://github.com/Soul-AILab/SoulX-FlashTalk
- https://huggingface.co/Soul-AILab/SoulX-FlashTalk-14B
- https://github.com/Alibaba-Quark/LiveAvatar
- https://huggingface.co/Quark-Vision/Live-Avatar
- https://streamavatar.github.io/
- https://github.com/TaoLiveAIGC/AptAvatar
- https://github.com/fudan-generative-vision/Hallo-Live
