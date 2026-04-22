# WeChat Send Skill

这是一个可直接分发的 Cursor Skill，用于在 Windows 桌面微信中给联系人或群聊发送消息。

仓库里已经包含可直接使用的分发产物，普通用户不需要安装 Python，也不需要自己重新打包。

## 最方便的使用方式

1. 直接使用已打包好的可执行文件：

```powershell
.cursor\skills\send-wechat-message\dist\wechat-message-sender\wechat-message-sender.exe --who "张三" --message "你好"
```

2. 或者把整个 `.cursor/skills/send-wechat-message/` 目录复制到你的 Cursor 项目中，然后直接对代理说：

- `打开微信给张三发你好`
- `给九安 梁辉煌发今晚八点开会`

如果你是第一次安装到自己的 Cursor 项目，建议直接看 [`INSTALL.md`](INSTALL.md)。

## 当前版本特性

- 支持联系人名和群名的模糊匹配。
- 会先切回微信聊天页，再优先点击左侧会话或搜索结果打开目标对话。
- 已规避 `wxauto4` 初始化时弹出个人资料卡的问题。
- 发送成功会按目标对话中的原始聊天气泡做校验，不再误判“已发送”为失败。

## 仓库内容

- `.cursor/skills/send-wechat-message/SKILL.md`：Skill 入口说明。
- `.cursor/skills/send-wechat-message/reference.md`：维护和排障文档。
- `.cursor/skills/send-wechat-message/dist/wechat-message-sender/`：开箱即用的 onedir 分发目录。
- `.cursor/skills/send-wechat-message/dist/wechat-message-sender.zip`：便于直接分发的压缩包。

## 重新打包

只有在需要重新构建分发产物时，才需要运行：

```powershell
powershell -ExecutionPolicy Bypass -File ".cursor/skills/send-wechat-message/build_wechat_sender.ps1" -Clean
```
