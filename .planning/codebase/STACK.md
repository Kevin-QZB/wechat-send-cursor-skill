# Codebase Stack

Date: 2026-04-24

## Overview

This repository is a Windows-focused Cursor skill distribution for sending text or files through desktop WeChat. The repo mixes distributable assets, source code, build automation, and end-user documentation.

## Languages and Formats

- Python is the primary implementation language in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- PowerShell is used for build and packaging automation in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`.
- Markdown is used for user docs and skill docs in `README.md`, `INSTALL.md`, `.cursor/skills/send-wechat-message/SKILL.md`, and `.cursor/skills/send-wechat-message/reference.md`.
- A prebuilt Windows executable is shipped at `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`.

## Runtime Model

- The runtime target is Windows only. The Python entrypoint explicitly rejects non-Windows environments in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- The shipped user-facing default is the prebuilt exe referenced by `README.md` and `.cursor/skills/send-wechat-message/SKILL.md`.
- The Python script is the fallback path when the exe is missing or broken, again documented in `.cursor/skills/send-wechat-message/SKILL.md` and `.cursor/skills/send-wechat-message/reference.md`.

## Python Dependencies

The repo does not expose a root `requirements.txt` or `pyproject.toml`. Instead, the build script installs dependencies imperatively:

- Build tools: `pip`, `setuptools`, `wheel`, `pyinstaller`
- Runtime helpers: `pywin32`, `pillow`, `comtypes`, `pyperclip`, `psutil`, `tenacity`, `colorama`
- WeChat automation backends: `wxauto4`, `wxautox4`, fallback `wxauto`

Evidence: `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`.

## Packaging Strategy

- Default distribution mode is a single-file exe built with PyInstaller.
- Optional `-OneDir` mode keeps the unpacked distribution layout.
- Offline wheel installation is supported from `.cursor/skills/send-wechat-message/vendor/`.
- Build workspace paths are hard-coded relative to the skill directory, including `.build-venv`, `build`, and `dist`.

Evidence: `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` and `.gitignore`.

## Configuration and Environment

- The script relies on standard Windows environment variables such as `ProgramFiles`, `ProgramFiles(x86)`, and `USERPROFILE` when locating WeChat binaries in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- WeChat 4.x accessibility setup is documented via the `QT_ACCESSIBILITY=1` requirement in `INSTALL.md` and `.cursor/skills/send-wechat-message/reference.md`.
- No repo-level app config file, lockfile, or environment template is present at the root.

## Repository Characteristics

- This is not a typical installable Python package; it is a distributable automation artifact plus maintenance source.
- The repo treats the built exe as a first-class deliverable, not just a build output.
- Tests are lightweight and live in `tests/test_send_wechat_message.py`.

## Files To Know

- `README.md` - product positioning and default usage
- `INSTALL.md` - end-user installation and troubleshooting
- `.cursor/skills/send-wechat-message/SKILL.md` - agent workflow contract
- `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` - runtime implementation
- `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` - packaging pipeline
- `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe` - shipped binary
# Technology Stack

**Analysis Date:** 2026-04-24

## Languages

**Primary:**
- Python 3.x - Core implementation in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` and tests in `tests/test_send_wechat_message.py`

**Secondary:**
- PowerShell - Build and packaging automation in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- Markdown - User and maintainer documentation in `README.md`, `INSTALL.md`, `.cursor/skills/send-wechat-message/SKILL.md`, and `.cursor/skills/send-wechat-message/reference.md`

## Runtime

**Environment:**
- Windows desktop runtime - enforced by `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Desktop WeChat client - required by `README.md`, `INSTALL.md`, and `.cursor/skills/send-wechat-message/dist-readme-template.txt`
- End-user default runtime is the packaged executable at `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`

**Package Manager:**
- pip - used only for maintainer build steps in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- Lockfile: missing

## Frameworks

**Core:**
- Python standard library `argparse`, `subprocess`, `pathlib`, `importlib`, and `unittest` - CLI behavior, process launch, file handling, dynamic backend loading, and tests in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` and `tests/test_send_wechat_message.py`
- WeChat automation backends `wxauto4`, `wxautox4`, and `wxauto` - desktop WeChat automation selected dynamically in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`

**Testing:**
- `unittest` - test runner used in `tests/test_send_wechat_message.py`

**Build/Dev:**
- PyInstaller - executable packaging in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` and `.cursor/skills/send-wechat-message/wechat_message_sender.spec`
- Python `venv` - isolated build environment in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`

## Key Dependencies

**Critical:**
- `wxauto4` - preferred WeChat 4.x automation backend referenced in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, `.cursor/skills/send-wechat-message/SKILL.md`, and `.cursor/skills/send-wechat-message/reference.md`
- `wxautox4` - fallback WeChat 4.x compatible backend referenced in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` and `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- `wxauto` - legacy fallback backend for older WeChat variants referenced in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` and `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- `pywin32`, `comtypes`, and `uiautomation` - Windows UI automation support included by `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`, `.cursor/skills/send-wechat-message/wechat_message_sender.spec`, and `.cursor/skills/send-wechat-message/vendor/README.txt`

**Infrastructure:**
- `PyInstaller` - builds the distributable executable in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- `PIL` from Pillow - bundled in `.cursor/skills/send-wechat-message/wechat_message_sender.spec`
- `pyperclip`, `psutil`, `tenacity`, and `colorama` - installed in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` and bundled in `.cursor/skills/send-wechat-message/wechat_message_sender.spec`

## Configuration

**Environment:**
- No `.env`, `package.json`, `pyproject.toml`, or `requirements.txt` was detected at the repository root
- Runtime behavior is configured mainly by CLI flags `--who`, `--message`, `--file`, `--list-sessions`, `--timeout`, and `--dry-run` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Windows environment variables `ProgramFiles`, `ProgramFiles(x86)`, and `USERPROFILE` are read in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` to locate the WeChat executable
- `QT_ACCESSIBILITY` is the only documented operator-set environment variable, referenced in `INSTALL.md`, `.cursor/skills/send-wechat-message/SKILL.md`, `.cursor/skills/send-wechat-message/reference.md`, and `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`

**Build:**
- Build script: `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- PyInstaller spec: `.cursor/skills/send-wechat-message/wechat_message_sender.spec`
- Offline wheel staging area: `.cursor/skills/send-wechat-message/vendor/`
- Ignore rules for build outputs: `.gitignore`

## Platform Requirements

**Development:**
- Windows host with PowerShell and Python available for maintainers running `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- Desktop WeChat installed and logged in for runtime verification, documented in `README.md` and `INSTALL.md`
- Cursor project layout expected by `.cursor/skills/send-wechat-message/SKILL.md`

**Production:**
- Local Windows desktop execution through `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`
- No server deployment target detected

---

*Stack analysis: 2026-04-24*
