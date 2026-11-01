# 大模型接入

设置 → 大模型接入。先选择当前工作场所，再选演示、本地、千问、豆包或OpenAI API。填写基础地址、实际模型名称/豆包推理接入点ID及密钥，保存后生效；点击测试已保存连接验证。保存不调用模型，测试和发送问题才调用，云端可能计费。

本地服务采用OpenAI兼容Chat Completions接口，默认地址http://127.0.0.1:11434/v1，可改为本机其他端口。本地微调模型须已部署为兼容接口，再填写部署后的模型名。平台不训练、不自动下载对话模型；本地TTS语音模型不是对话大模型。当前只支持本机HTTP，局域网服务后续单独配置。

千问默认中国内地传统兼容地址，区域和密钥必须匹配；支持官方国际/美国传统地址以及北京/新加坡Workspace地址，其他地区/协议待扩展。豆包默认方舟北京api/v3，名称按自己已开通服务填写。OpenAI使用API服务，不登录ChatGPT网页账号；当前接入Chat Completions兼容模型，Responses和专有工具后续适配。不要猜测模型名称或账户权限。

ModelStore按独立场所保存data/models.json，串行原子写入、revision防止覆盖，读取只回传hasKey。提供商/地址变化不继承旧密钥，界面不长期保存密钥；本机文件尚未加密，不适合生产多租户部署。数据目录已在gitignore。错误不回传提供商正文或密钥，连接失败不静默回退演示。固定官方云域名、禁止URL密码/查询/重定向，本地地址限制loopback。

ModelRouter为后台唯一调用入口。岗位配置与当前问题发给所选模型；真人摘要仅在已确认的模拟会话、本人的档案聊天授权，以及独立云端传送同意均有效时送云端。测试只发测试句，不发送档案或岗位。模型只有文字输出，无通知/门禁工具权限，不能通过回答授予身份或执行设备动作。长对话历史、相关记忆检索、流式回复、服务端取消、重试与多提供商自动调度待实现。前端打断会忽略晚到回答和停止播放，但不保证上游已停止计算或计费。

已实现配置、持久化、适配器、连接测试和实际HTTP请求链路。自动测试使用本机兼容服务桩，未加载本地对话权重，也未使用真实云账号；用户账户连通和回答质量尚待验收。

官方资料：[OpenAI Chat Completions](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)、[千问模型服务](https://help.aliyun.com/en/model-studio/what-is-model-studio)、[火山方舟](https://docs.volcengine.com/docs/ark/context-management?lang=zh)。
