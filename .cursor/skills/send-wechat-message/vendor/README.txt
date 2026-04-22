把离线 wheel 放到这个目录。

构建脚本 `build_wechat_sender.ps1` 会优先从这里安装以下依赖：
- wxauto4 / wxautox4 / wxauto
- pywin32
- comtypes
- uiautomation

适用于构建机无法联网，或需要固定依赖来源的场景。
