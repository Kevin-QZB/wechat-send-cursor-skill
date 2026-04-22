---
name: send-wechat-message
description: 通过桌面微信给指定联系人或群聊发送消息。Use when the user asks to “打开微信给某某发某某消息”, “给某人发微信”, “发消息到某个微信联系人/群”, or any request to send a message in desktop WeChat on Windows.
---

# Send WeChat Message

## 何时使用

当用户想让代理直接操作桌面微信发消息时使用本 Skill，典型表达包括：

- `打开微信给张三发今晚上线`
- `给李四发微信，说我晚点到`
- `发一条消息到 家庭群：我到家了`

## 工作流

1. 从用户请求中提取：
   - `who`: 联系人名或群聊名
   - `message`: 要发送的原始消息内容
2. 如果联系人或消息内容不明确，先追问，不要猜。
3. 默认直接使用已经打好的可执行文件：

```powershell
".cursor/skills/send-wechat-message/dist/wechat-message-sender.exe" --who "<联系人或群名>" --message "<消息内容>"
```

4. 只有在可执行文件不存在或失效时，才回退到 Python 脚本：

```powershell
python ".cursor/skills/send-wechat-message/scripts/send_wechat_message.py" --who "<联系人或群名>" --message "<消息内容>"
```

5. 如果用户提供的是简称、备注的一部分，或你怀疑会话名不完整，也可以直接执行发送命令。当前版本会先切回微信聊天页，再结合左侧会话列表和搜索结果做模糊匹配。

6. 如果用户只是想确认会话名，先列出当前微信可见会话：

```powershell
".cursor/skills/send-wechat-message/dist/wechat-message-sender.exe" --list-sessions
```

7. 如果 exe 不存在，再回退到脚本方式：

```powershell
python ".cursor/skills/send-wechat-message/scripts/send_wechat_message.py" --list-sessions
```

8. 只有在确认已打开目标对话、并在聊天区检测到新消息气泡后，才算发送成功。成功后明确反馈已向谁发送了什么。

## 执行约束

- 仅适用于 Windows 桌面微信。
- 优先让用户提供尽可能准确的联系人备注名或群名。当前版本支持模糊匹配，但如果多个候选都很像，仍应优先向用户确认。
- 保持消息内容原样，不要擅自润色，除非用户明确要求你改写。
- 优先使用 `wxauto4` 适配微信 4.x；仅在用户明确是老版微信 3.9.x 或 `wxauto4` 不适用时再考虑 `wxauto`。

## 常见故障处理

- 如果 exe 可用，不要让最终用户安装 Python 或自行打包。

- 仅在维护这个 Skill、需要重新构建时，才处理依赖安装问题。

- 构建环境缺少依赖时，优先安装：

```powershell
pip install wxauto4
```

如需重新生成分发包，再运行项目内的一键打包脚本：

```powershell
powershell -ExecutionPolicy Bypass -File ".cursor/skills/send-wechat-message/build_wechat_sender.ps1" -Clean
```

- 如果是微信 4.x，且脚本提示 `QT_ACCESSIBILITY=1`，说明微信启动时没有暴露 UIA 控件树。此时提示用户完全退出并重开微信；如需你代为准备环境变量，可执行：

```powershell
[Environment]::SetEnvironmentVariable("QT_ACCESSIBILITY", "1", "User")
```

然后让用户完全退出微信后重新打开。

## 额外说明

- 当前实现会优先点击左侧可见会话或搜索结果，而不是只依赖 `wxauto4.ChatWith()`。
- 当前实现的发送成功校验基于聊天区原始 UI 气泡，而不是只依赖 `wxauto4.GetAllMessage()`，以适配微信 4.x 下“自己发出的消息被漏读”的情况。
- 仓库默认分发单文件离线 `exe`，以减少最终用户需要复制和保留的文件数量。
- 更详细的排障说明见 [reference.md](reference.md)。
