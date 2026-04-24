# Codebase Architecture

Date: 2026-04-24

## System Shape

This repository is structured as a packaged Cursor skill rather than a conventional application service. The main architecture is:

1. Skill contract and docs define how an agent should invoke the tool.
2. A shipped exe is the preferred runtime for end users.
3. A Python fallback script contains the real automation logic.
4. A PowerShell build script recreates the distributable artifact.
5. A small unittest suite validates pure helper behavior.

## Main Entry Points

- `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe` - primary production entrypoint for users
- `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` - source implementation and fallback runtime
- `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` - build pipeline entrypoint
- `tests/test_send_wechat_message.py` - test entrypoint

## Runtime Flow

The Python runtime in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` follows a clear linear pipeline:

1. Parse CLI arguments.
2. Load a usable WeChat automation backend.
3. Attach to or launch desktop WeChat.
4. Optionally list visible sessions.
5. Resolve the target chat with exact, substring, or fuzzy matching.
6. Open the chat and verify the active conversation.
7. Send either text or files.
8. Verify success by reading message content or raw UI bubble text.

## Internal Module Boundaries

Although implemented in a single Python file, the code is internally split into functional layers:

- Backend bootstrap: `ensure_tkinter_stub()`, `import_wechat_backend()`, `attach_wechat()`
- WeChat process and session navigation: `launch_wechat()`, `list_sessions()`, `open_chat()`
- Matching and normalization: `normalize_name()`, `resolve_target_chat_name()`, `choose_search_result()`
- Send and verify: `send_message()`, `send_files()`, `verify_message_sent()`, `verify_files_sent()`
- CLI layer: `parse_args()`, `main()`

This is effectively a single-module command architecture with functional segmentation.

## Data and Control Flow

- Input comes from CLI flags such as `--who`, `--message`, `--file`, and `--list-sessions`.
- Control then flows into backend discovery and WeChat window attachment.
- The script interacts with WeChat's UI tree through the imported backend object.
- Output is emitted as CLI stdout/stderr messages, not as structured JSON.
- Success confirmation is based on UI state observed after the send operation, not on a remote API acknowledgment.

## Build Architecture

The build pipeline in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` is separate from runtime logic:

- Create or refresh a dedicated build virtualenv.
- Install base build tools.
- Install a compatible WeChat automation backend.
- Install runtime helper libraries.
- Build with PyInstaller in one-file or one-dir mode.
- Copy a distribution README and package the output.

## Architectural Characteristics

- Strongly Windows-specific
- UI automation centric rather than API centric
- Single-script implementation with layered helper functions
- Distribution-first repo design, where docs and binary output matter as much as source
- Operational correctness depends on external desktop UI state

## Files To Read First

- `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- `.cursor/skills/send-wechat-message/SKILL.md`
- `README.md`
- `tests/test_send_wechat_message.py`
# Architecture

**Analysis Date:** 2026-04-24

## Pattern Overview

**Overall:** Single-purpose distributable Cursor skill with a CLI runtime and a separate maintainer build pipeline.

**Key Characteristics:**
- The repository is a skill package, not a general application service. The operator-facing contract lives in `README.md`, `INSTALL.md`, and `.cursor/skills/send-wechat-message/SKILL.md`.
- Runtime behavior is concentrated in one Python entry module: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Packaging and release concerns are explicit and local to the skill via `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` and `.cursor/skills/send-wechat-message/wechat_message_sender.spec`.

## Layers

**Skill Interface Layer:**
- Purpose: Define how Cursor agents and users invoke the skill and what guarantees the skill provides.
- Location: `.cursor/skills/send-wechat-message/`
- Contains: `SKILL.md`, `reference.md`, `dist-readme-template.txt`, and the packaged executable in `dist/wechat-message-sender.exe`.
- Depends on: The runtime executable `dist/wechat-message-sender.exe` or the fallback script `scripts/send_wechat_message.py`.
- Used by: Cursor agents, maintainers, and end users following `README.md` and `INSTALL.md`.

**Runtime Automation Layer:**
- Purpose: Parse CLI input, attach to desktop WeChat, resolve the target chat, send content, and verify success.
- Location: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Contains: `argparse` CLI parsing, backend import selection, chat resolution helpers, message/file sending helpers, and success verification logic.
- Depends on: Python standard library plus one of `wxauto4`, `wxautox4`, or `wxauto`, and a locally running desktop WeChat client.
- Used by: `dist/wechat-message-sender.exe`, direct Python fallback execution, and the unit tests in `tests/test_send_wechat_message.py`.

**Build And Packaging Layer:**
- Purpose: Produce the offline Windows executable and the optional onedir distribution.
- Location: `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`, `.cursor/skills/send-wechat-message/wechat_message_sender.spec`, and `.cursor/skills/send-wechat-message/vendor/README.txt`
- Contains: Build virtualenv bootstrap, dependency installation, vendor-wheel support, PyInstaller invocation, and distribution cleanup.
- Depends on: Local Python, PyInstaller, runtime dependencies, and optional offline wheels placed under `.cursor/skills/send-wechat-message/vendor/`.
- Used by: Maintainers rebuilding the distributed artifact in `.cursor/skills/send-wechat-message/dist/`.

**Verification Layer:**
- Purpose: Guard helper behavior around argument parsing and payload normalization without driving the real WeChat UI.
- Location: `tests/test_send_wechat_message.py`
- Contains: `unittest` cases for CLI argument parsing, file-path normalization, payload exclusivity, and file marker helpers.
- Depends on: Importing `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Used by: Maintainers validating behavior after script changes.

## Data Flow

**Send Message Or File Flow:**

1. A user or agent follows `.cursor/skills/send-wechat-message/SKILL.md` and launches `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`, or falls back to `python ".cursor/skills/send-wechat-message/scripts/send_wechat_message.py"`.
2. `main()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` parses CLI flags, validates that exactly one payload type is provided, and selects an automation backend with `import_wechat_backend()`.
3. The runtime attaches to an existing desktop WeChat instance with `attach_wechat()`, switching back to the chat page when needed.
4. The runtime resolves the requested session using visible sessions and search results through `resolve_target_chat_name()`, `list_sessions()`, and `open_chat()`.
5. The runtime sends text with `send_message()` or files with `send_files()`, then verifies success via `verify_message_sent()` or `verify_files_sent()` using both backend message APIs and raw UI bubble inspection.
6. The CLI prints a human-readable success line to stdout or raises `WeChatSendError`, which is rendered to stderr before the process exits with code `1`.

**Build Flow:**

1. A maintainer runs `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`.
2. The build script creates or refreshes `.cursor/skills/send-wechat-message/.build-venv/`, installs PyInstaller and runtime dependencies, and optionally installs offline wheels from `.cursor/skills/send-wechat-message/vendor/`.
3. The script builds a onefile executable directly from `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, or uses `.cursor/skills/send-wechat-message/wechat_message_sender.spec` for the onedir variant.
4. The script writes the distribution README, removes metadata from the packaged folder, and optionally zips the onedir output inside `.cursor/skills/send-wechat-message/dist/`.

**State Management:**
- Runtime state is in-process only. There is no database, queue, or persisted app state in the repository.
- External state comes from the local desktop WeChat UI, CLI arguments, the filesystem for `--file` payloads, and optional environment configuration such as `QT_ACCESSIBILITY`.

## Key Abstractions

**User-Facing Failure Boundary:**
- Purpose: Normalize operational failures into readable CLI output.
- Examples: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Pattern: `WeChatSendError` is raised from lower-level helpers and handled once in the `__main__` block.

**Backend Selection:**
- Purpose: Hide differences between `wxauto4`, `wxautox4`, and `wxauto`.
- Examples: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Pattern: `import_wechat_backend()` probes supported modules in order and returns both the imported module and a `variant` string used by downstream branches.

**Chat Resolution:**
- Purpose: Convert a user-provided name into the actual visible WeChat session that should receive the payload.
- Examples: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Pattern: `resolve_target_chat_name()`, `choose_search_result()`, and `open_chat()` combine normalization, fuzzy matching, visible-session inspection, and backend fallback calls.

**Delivery Verification:**
- Purpose: Confirm the payload appeared in the target conversation instead of assuming backend APIs are always reliable.
- Examples: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Pattern: `verify_message_sent()` and `verify_files_sent()` compare pre-send and post-send state using both structured message APIs and raw UI elements from `wx.ChatBox.msgbox`.

## Entry Points

**Skill Entry:**
- Location: `.cursor/skills/send-wechat-message/SKILL.md`
- Triggers: Natural-language user requests in Cursor such as sending a WeChat message or listing sessions.
- Responsibilities: Define the default executable command, fallback script command, and operating constraints for agents.

**Runtime CLI Entry:**
- Location: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Triggers: Direct Python execution or bundling into the packaged executable.
- Responsibilities: Parse CLI args, attach to WeChat, route the send flow, and emit process exit status.

**Packaged Executable Entry:**
- Location: `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`
- Triggers: Normal end-user and agent execution path documented in `README.md`, `INSTALL.md`, and `.cursor/skills/send-wechat-message/SKILL.md`.
- Responsibilities: Provide the offline Windows-native distribution of the Python runtime flow.

**Build Entry:**
- Location: `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- Triggers: Maintainer rebuilds of the distributed artifact.
- Responsibilities: Prepare build dependencies, run PyInstaller, and shape the final output under `.cursor/skills/send-wechat-message/dist/`.

## Error Handling

**Strategy:** Fail fast with explicit operational hints, while retrying backend-dependent UI actions before giving up.

**Patterns:**
- Backend import and attach failures are wrapped into `WeChatSendError` with concrete recovery steps in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Session opening and payload sending use multiple fallback attempts before surfacing the final failure from `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

## Cross-Cutting Concerns

**Logging:** Plain CLI output via `print()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
**Validation:** `argparse` plus custom validation helpers such as `resolve_send_payload()` and `normalize_file_paths()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
**Authentication:** No repository-managed auth layer. The runtime relies on a locally installed and logged-in desktop WeChat client, as described in `README.md`, `INSTALL.md`, and `.cursor/skills/send-wechat-message/reference.md`.

---

*Architecture analysis: 2026-04-24*
