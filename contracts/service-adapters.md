# 可扩展服务契约 v0.1

所有适配器返回 mode（mock/real）、状态与回执；真实接入需保持场所隔离，不通过名称或追踪 ID 授权。

| 接口 | 当前实现 / 后续契约 |
|---|---|
| CameraAdapter.detect({online,people}) | 模拟 online 与 tracks；真实事件追加 siteId、deviceId、eventId、timestamp、region，断线重连独立处理 |
| IdentityAdapter.match() | uncertain、verified:false；后续候选 ID、置信度、登记同意、独立确认凭据，不返回门禁批准 |
| MessagingAdapter.send({recipient,purpose,fail}) | delivered/failed 与 receipt；后续增加幂等键、重试次数和提供商回执，构造时注入 |
| AccessAdapter.execute(decision) | 仅消费独立批准；当前 deny；真实需 PermissionService 签发短时单次指令、门范围、审计 ID |
| DialogueAdapter.reply(text) | 模拟回答；后续模型服务接口含 sessionId、responseId、persona、style、取消信号；幽默服务独立替换 |
| AudioAdapter / TTSAdapter | 待实现；输入音频块/文本，输出音频块、时间戳、viseme、取消回执 |

跨端表演仍遵守 performance-event.example.json 的音频播放时钟与 responseId；当前占位跳动不输出音素事件。UE 后续只执行能力映射后的事件。

HTTP: GET /api/health；POST /api/chat、/api/camera；GET/POST /api/people；PATCH/DELETE /api/people/:id；POST /api/visits、/api/notify、/api/access。业务接口通过 ?site=office 或 restaurant 选择模拟场所。用户输入不能设置 verified、role 或 employeeConfirmed。

Person/Visit/Preference 已有内存实现；FaceEnrollment、Memory、Permission、持久化 Notification/AccessEvent 仍为后续模型。

## 客户场所与岗位配置 v0.1
GET /api/templates 返回九种模板；GET /api/workspaces 返回独立场所；POST /api/workspaces 创建；PATCH /api/workspaces?site=:id 更新配置并要求 revision。字段 name、role、environment、greeting、tone、duties、knowledge、workflow、handoff、templateId；后台生成 id，更新递增 revision。不接受配置字段授予 verified、permissions 或 employeeConfirmed。
既有业务接口 site 参数改为独立 Workspace ID（旧 office/restaurant 保留），templateId 是可更换的行业类型。后续账户服务必须将当前用户授权场所注入上下文；此版本只供本机模拟控制台。
