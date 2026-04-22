# 安装说明

这份说明是给最终用户的，目标是用最少步骤把技能放进自己的 Cursor 项目里。

这也是 AI 通过 GitHub 链接“安装技能”时应该遵循的流程。这个仓库已经自带离线分发产物，不需要额外安装任何 Python 依赖。

## 适用环境

- Windows
- 已安装并登录桌面微信
- 已安装 Cursor

## 最简单安装法

1. 下载仓库里的技能目录，或者直接下载整个仓库。
2. 把 `.cursor/skills/send-wechat-message/` 整个目录复制到你自己的项目里。
3. 确认目标路径是：

```text
你的项目/.cursor/skills/send-wechat-message/
```

4. 打开 Cursor，让代理在这个项目中工作。
5. 直接对代理说：

- `打开微信给张三发你好`
- `给某个群聊发收到请回复`

## 不需要做的事

安装这个技能时，普通用户和普通 AI 都不需要做下面这些事：

- 不需要安装 Python。
- 不需要创建虚拟环境。
- 不需要执行 `pip install`、`uv sync`、`poetry install`。
- 不需要重新运行打包脚本。

只要仓库里的 `dist/wechat-message-sender.exe` 还在，就应当直接使用它。

## 如果你想手动验证

进入你项目根目录后，可以直接运行：

```powershell
.cursor\skills\send-wechat-message\dist\wechat-message-sender.exe --who "张三" --message "你好"
```

查看当前微信可见会话：

```powershell
.cursor\skills\send-wechat-message\dist\wechat-message-sender.exe --list-sessions
```

## 当前版本已经处理的常见问题

- 支持联系人名和群名的模糊匹配。
- 会自动切回微信聊天页，再优先点击左侧会话或搜索结果。
- 已规避初始化时弹出微信资料卡的问题。
- 发送成功会根据聊天区里的原始消息气泡做确认，不会再把“实际已发出”误判成失败。

## 如果发送失败

1. 确认桌面微信已经登录，而且窗口是可见的。
2. 如果是微信 4.x，先执行：

```powershell
[Environment]::SetEnvironmentVariable("QT_ACCESSIBILITY", "1", "User")
```

3. 完全退出微信，再重新打开。
4. 先运行 `--list-sessions`，确认目标联系人或群聊当前是可见的。

## 给维护者

普通用户不需要 Python 环境，也不需要自己重新打包。

只有在你要更新技能分发产物时，才需要运行：

```powershell
powershell -ExecutionPolicy Bypass -File ".cursor/skills/send-wechat-message/build_wechat_sender.ps1" -Clean
```

如果你更想保留 `onedir` 目录模式，可选：

```powershell
powershell -ExecutionPolicy Bypass -File ".cursor/skills/send-wechat-message/build_wechat_sender.ps1" -OneDir -Clean
```
