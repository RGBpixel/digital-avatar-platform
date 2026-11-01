# TTS接口 v0.1

POST /api/tts?site=场所ID：text、sampleId、personality(lively/calm/warm/storytelling)、emotion(neutral/happy/rich/sad)、intensity(0..1)。选取当前场所已同意样音。配置 LOCAL_TTS_URL 后后台调用本机模型服务，返回音频字节；缺少模型503，不返回假的生成音频。
模型服务 POST /tts：text、personality、emotion、intensity、referenceAudio:{mimeType,base64,transcript}；返回音频Content-Type，可返回 X-TTS-Style-Control 描述风格能力。当前预备Qwen0.6B-Base实现返回not-supported，不支持独立情绪指令。
GET /api/tts/capabilities 区分是否配置模型服务（不等于模型已启动）；样音 GET/POST /api/voice-samples，GET原音和DELETE /api/voice-samples/:id，始终校验场所。上传需 X-Voice-Consent:true、URL编码的X-Sample-Name/X-Sample-Transcript，body为二进制，最多10 MB。
客户端本机声音无服务器音频产物，状态为真实浏览器播放事件；不能用该模式冒充模型视频导出或音素同步。参考声音的模型克隆、音质、情绪、许可与实时速度单独测试。
