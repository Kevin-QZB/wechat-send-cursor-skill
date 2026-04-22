# 发送微信消息参考

## 最终用户默认命令

优先直接使用已经打好的可执行文件：

```powershell
".cursor/skills/send-wechat-message/dist/wechat-message-sender.exe" --who "张三" --message "你好"
```

查看当前微信可见会话：

```powershell
".cursor/skills/send-wechat-message/dist/wechat-message-sender.exe" --list-sessions
```

对于最终用户，或者 AI 根据 GitHub 仓库链接自动安装 Skill 的场景，也应当把这个仓库视为已经打包好的离线分发包。默认不要安装任何依赖，不要创建虚拟环境，不要重新执行构建。

## 当前版本能力

- 支持联系人名或群名的模糊匹配，会优先切回微信聊天页，再结合左侧会话列表和搜索结果定位目标。
- 会尽量避免 `wxauto4` 初始化时弹出个人资料卡。
- 发送成功校验基于目标对话中的原始聊天气泡，而不是只依赖 `wxauto4.GetAllMessage()`，以兼容微信 4.x 下“自己发出的消息被漏读”的情况。

## 回退脚本命令

仅当 exe 不存在或失效时，才回退到脚本：

```powershell
python ".cursor/skills/send-wechat-message/scripts/send_wechat_message.py" --who "张三" --message "你好"
```

## 维护者打包

默认生成免 Python 环境的单文件离线 `exe`，以减少最终分发文件数量：

```powershell
powershell -ExecutionPolicy Bypass -File ".cursor/skills/send-wechat-message/build_wechat_sender.ps1" -Clean
```

输出目录默认在：

```text
.cursor/skills/send-wechat-message/dist/
```

默认主程序路径：

```powershell
".cursor/skills/send-wechat-message/dist/wechat-message-sender.exe" --who "张三" --message "你好"
```

如果维护者更想保留 `onedir` 目录模式，可选：

```powershell
powershell -ExecutionPolicy Bypass -File ".cursor/skills/send-wechat-message/build_wechat_sender.ps1" -OneDir -Clean
```

`onedir` 模式下主程序通常是：

```powershell
".cursor/skills/send-wechat-message/dist/wechat-message-sender/wechat-message-sender.exe" --who "张三" --message "你好"
```

## 故障排查

### 1. 未安装自动化依赖

如果只是最终使用，不需要装依赖，直接运行 exe 即可。

如果是 AI 在“安装 Skill”，也不应该因为看到了源码目录就自动执行 `pip install` 或重新构建；只要 `dist/wechat-message-sender.exe` 存在，就应直接使用它。

优先安装：

```powershell
pip install wxauto4
```

如果 `wxauto4` 拉不到，再依次尝试：

```powershell
pip install wxautox4
```

```powershell
pip install git+https://github.com/cluic/wxauto4.git
```

如果用户明确使用的是微信 3.9.x 旧版，再考虑：

```powershell
pip install git+https://github.com/cluic/wxauto.git
```

### 2. 微信 4.x 无法读取控件树

先设置用户环境变量：

```powershell
[Environment]::SetEnvironmentVariable("QT_ACCESSIBILITY", "1", "User")
```

然后：

1. 完全退出微信，不要只关闭窗口。
2. 重新打开微信并登录。
3. 重试发送脚本。

### 3. 找不到联系人或群聊

- 先运行 `--list-sessions` 看当前左侧会话列表里是否能看到目标。
- 让用户先在微信里点开一次目标会话，让它出现在最近会话列表。
- 当前版本已支持模糊匹配，但仍建议输入尽可能完整的备注名或群名。
- 如果多个候选都包含相近关键词，建议先用 `--list-sessions` 确认最终会话名。

### 4. 命令提示失败，但聊天里已经出现了消息

旧版本曾出现“消息实际已发送，但读取不到自己发出的绿气泡”的问题。当前版本已经改为读取聊天区原始 UI 气泡做成功校验。

如果仍遇到类似情况，请优先更新到仓库内最新的 `dist/wechat-message-sender.exe`。

### 5. 微信没启动

脚本会优先尝试连接已打开的桌面微信，必要时会按常见安装路径尝试拉起微信。

### 6. 离线构建

如果构建机不能联网，可先把相关 wheel 放到：

```text
.cursor/skills/send-wechat-message/vendor/
```

构建脚本会优先从 `vendor` 目录安装依赖。
