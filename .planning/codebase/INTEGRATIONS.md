# Codebase Integrations

Date: 2026-04-24

## Overview

This repository has very few external service integrations. Its main integration surface is the local Windows desktop environment plus WeChat automation libraries.

## Desktop WeChat Integration

- The core product behavior is to automate desktop WeChat, not to call an official WeChat cloud API.
- The runtime searches common install paths such as `C:\Program Files\Tencent\Weixin\Weixin.exe` and related variants inside `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- If WeChat is not already open, the script attempts to launch it locally via `subprocess.Popen(...)`.

## Automation Backend Integration

The script dynamically imports one of three Python automation backends:

- `wxauto4`
- `wxautox4`
- `wxauto`

This fallback chain is implemented in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

The code also patches `wxauto4` behavior to avoid opening the profile popup during initialization, which is a compatibility integration detail rather than app logic.

## Windows Accessibility Integration

- The project depends on Windows UI Automation behavior for WeChat 4.x.
- Documentation in `INSTALL.md` and `.cursor/skills/send-wechat-message/reference.md` instructs users to set `QT_ACCESSIBILITY=1` when the UI tree is not exposed.
- This is an OS-level integration dependency, not a repo-local config flag.

## Filesystem Integration

- File sending uses absolute or normalized local file paths passed with `--file`, resolved in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Offline dependency installation is supported from `.cursor/skills/send-wechat-message/vendor/`.
- Build outputs are produced into `.cursor/skills/send-wechat-message/dist/`.

## Distribution Integration

- Cursor consumes the skill definition from `.cursor/skills/send-wechat-message/SKILL.md`.
- The default agent-facing command path is `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`.
- This repo is designed to be copied into another Cursor project rather than published through a package registry.

## Not Found

Based on the current repo contents, these integrations were not found:

- No database integration
- No external HTTP API client
- No OAuth provider
- No webhook receiver or sender
- No message queue
- No cloud storage integration
- No browser frontend or web server

## Integration Hotspots

- `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` - WeChat process attach, session search, send, and verification
- `.cursor/skills/send-wechat-message/SKILL.md` - agent-level invocation contract
- `INSTALL.md` - environment setup expectations for end users
- `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` - dependency and packaging integration flow
# External Integrations

**Analysis Date:** 2026-04-24

## APIs & External Services

**Desktop application automation:**
- Tencent Desktop WeChat - target application that receives messages and files
  - SDK/Client: `wxauto4`, `wxautox4`, or `wxauto` loaded by `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
  - Auth: existing logged-in WeChat desktop session; no API key or token detected
  - Discovery: common install paths are probed in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`

**Build-time package sources:**
- PyPI package index - used only when maintainers rebuild dependencies through `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
  - SDK/Client: `pip`
  - Auth: none detected
- GitHub source repository `https://github.com/cluic/wxauto4.git` - optional fallback source in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` and `.cursor/skills/send-wechat-message/reference.md`
  - SDK/Client: `pip`
  - Auth: none detected

**HTTP or SaaS APIs:**
- Not detected in `README.md`, `INSTALL.md`, `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`, or `.cursor/skills/send-wechat-message/wechat_message_sender.spec`

## Data Storage

**Databases:**
- Not detected
  - Connection: not applicable
  - Client: not applicable

**File Storage:**
- Local filesystem only
  - Packaged executable stored at `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`
  - Source script stored at `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
  - Optional offline wheels stored at `.cursor/skills/send-wechat-message/vendor/`
  - User-selected outbound files are resolved from local paths in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`

**Caching:**
- None detected

## Authentication & Identity

**Auth Provider:**
- Custom desktop session reuse
  - Implementation: the tool attaches to a locally logged-in WeChat desktop client via `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
  - No OAuth provider, SSO provider, or repository-managed credential file detected

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logs:**
- Console stdout and stderr from `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- `wxauto_logs/` is ignored by `.gitignore`, indicating backend-generated local logs may exist, but no repository-managed log pipeline is defined

## CI/CD & Deployment

**Hosting:**
- Local filesystem distribution as a Cursor skill under `.cursor/skills/send-wechat-message/`

**CI Pipeline:**
- Not detected

## Environment Configuration

**Required env vars:**
- `QT_ACCESSIBILITY` - documented for WeChat 4.x accessibility in `INSTALL.md`, `.cursor/skills/send-wechat-message/SKILL.md`, `.cursor/skills/send-wechat-message/reference.md`, and `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- `ProgramFiles`, `ProgramFiles(x86)`, and `USERPROFILE` - read by `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` to locate WeChat executables

**Secrets location:**
- No secret store, `.env` file, or credential file detected in the explored repository files

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

## Desktop Application Dependencies

**Required desktop software:**
- Windows desktop WeChat - required by `README.md`, `INSTALL.md`, and `.cursor/skills/send-wechat-message/dist-readme-template.txt`
- Cursor-compatible project skill layout - required by `.cursor/skills/send-wechat-message/SKILL.md`

**Windows automation stack:**
- `pywin32`, `comtypes`, and `uiautomation` are bundled or installed for UI automation in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`, `.cursor/skills/send-wechat-message/wechat_message_sender.spec`, and `.cursor/skills/send-wechat-message/vendor/README.txt`

---

*Integration audit: 2026-04-24*
