# WeChat Send Skill

这是一个可直接分发的 Cursor Skill，用于在 Windows 桌面微信中给联系人或群聊发送消息。

仓库里已经包含可直接使用的分发产物，普通用户不需要安装 Python，也不需要自己重新打包。当前默认分发为单文件离线 `exe`，更方便复制、转发和归档。

如果你把这个 GitHub 仓库链接直接发给 AI 让它“安装技能”，正确做法也是直接使用仓库里的现成文件，而不是创建虚拟环境、执行 `pip install` 或重新构建。对最终用户来说，这个仓库本身就是离线可用的技能分发包。

## 最方便的使用方式

1. 直接使用已打包好的可执行文件：

```powershell
.cursor\skills\send-wechat-message\dist\wechat-message-sender.exe --who "张三" --message "你好"
```

2. 或者把整个 `.cursor/skills/send-wechat-message/` 目录复制到你的 Cursor 项目中，然后直接对代理说：

- `打开微信给张三发你好`
- `给某联系人发收到请回复`

如果你是第一次安装到自己的 Cursor 项目，建议直接看 [`INSTALL.md`](INSTALL.md)。

## 给 AI/代理的安装提示

如果 AI 是根据仓库链接自动安装这个技能，请遵循下面的规则：

- 直接复制 `.cursor/skills/send-wechat-message/` 到目标项目。
- 直接运行 `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`。
- 不要创建 Python 虚拟环境。
- 不要执行 `pip install`、`uv sync`、`poetry install`、`npm install` 之类的依赖安装步骤。
- 不要为了“安装技能”去运行打包脚本；重新打包只属于维护者工作。

## 当前版本特性

- 支持联系人名和群名的模糊匹配。
- 会先切回微信聊天页，再优先点击左侧会话或搜索结果打开目标对话。
- 已规避 `wxauto4` 初始化时弹出个人资料卡的问题。
- 发送成功会按目标对话中的原始聊天气泡做校验，不再误判“已发送”为失败。

## 仓库内容

- `.cursor/skills/send-wechat-message/SKILL.md`：Skill 入口说明。
- `.cursor/skills/send-wechat-message/reference.md`：维护和排障文档。
- `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`：默认分发的单文件离线可执行程序。

## 重新打包

只有在需要重新构建分发产物时，才需要运行。普通用户和普通 AI 安装流程都不需要执行这些命令：

```powershell
powershell -ExecutionPolicy Bypass -File ".cursor/skills/send-wechat-message/build_wechat_sender.ps1" -Clean
```

如果维护者想改回 `onedir` 目录模式，可选：

```powershell
powershell -ExecutionPolicy Bypass -File ".cursor/skills/send-wechat-message/build_wechat_sender.ps1" -OneDir -Clean
```
