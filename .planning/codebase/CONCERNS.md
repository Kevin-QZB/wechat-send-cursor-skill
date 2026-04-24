# Codebase Concerns

Date: 2026-04-24

## Overview

The repo is small and focused, but its main risks come from desktop automation brittleness, packaging drift, and low end-to-end test coverage.

## Concern 1: Source vs Binary Drift

- The repo ships a production exe at `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`.
- The visible tests exercise the Python source in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, not the checked-in exe.
- If the exe is not rebuilt after source changes, users may run behavior that differs from the repo's current source and docs.

## Concern 2: UI Automation Fragility

- Success depends on desktop WeChat UI structure and backend behavior from `wxauto4`, `wxautox4`, or `wxauto`.
- The source contains many compatibility branches and retries in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, which is evidence that the integration surface is unstable.
- WeChat upgrades or backend library changes could break chat resolution or send verification without obvious compile-time signals.

## Concern 3: Environment Sensitivity

- The runtime is Windows-only and assumes desktop WeChat is installed, logged in, visible, and automation-accessible.
- `INSTALL.md` and `.cursor/skills/send-wechat-message/reference.md` both document the `QT_ACCESSIBILITY=1` dependency for some WeChat 4.x setups.
- This means field failures can come from machine setup, not only from repo logic.

## Concern 4: Packaging Reproducibility

- There is no pinned dependency manifest such as `requirements.txt`, `pyproject.toml`, or lockfile at the repo root.
- `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` installs dependencies imperatively from pip and optional local wheels.
- Rebuilds may not be perfectly reproducible across time or machines.

## Concern 5: Thin Automated Coverage

- Only `tests/test_send_wechat_message.py` is present.
- The tests cover argument parsing and helper functions, but not live automation, packaging, or distribution behavior.
- The most failure-prone path in the repo is the least automated one.

## Concern 6: Single-Module Concentration

- Most product logic lives in a single file: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- This keeps the repo simple, but it also concentrates chat matching, send logic, backend bootstrap, and verification into one change surface.
- Future edits can easily create cross-cutting regressions if not tested carefully.

## Concern 7: Documentation Duplication

- Usage and install guidance is intentionally repeated in `README.md`, `INSTALL.md`, `.cursor/skills/send-wechat-message/SKILL.md`, and `.cursor/skills/send-wechat-message/reference.md`.
- This improves discoverability, but it increases the chance that one document lags behind the others after future changes.

## Security Notes

- No obvious embedded API keys or cloud credentials were found in the inspected source and docs.
- The main security boundary is local desktop automation; mistakes are more likely to cause wrong-recipient sends or false success/failure judgments than remote data leakage.

## Watch First

- `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`
- `tests/test_send_wechat_message.py`
# Codebase Concerns

**Analysis Date:** 2026-04-24

This document records confirmed concerns from code and docs. Where the code suggests a risk rather than a proven defect, the item is labeled as an inferred risk.

## Tech Debt

**WeChat backend compatibility shims:**
- Issue: `send_wechat_message.py` monkey-patches `wxauto4` behavior in `patch_wxauto4_profile_popup()` and injects a fake `tkinter` module in `ensure_tkinter_stub()`.
- Files: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, `.cursor/skills/send-wechat-message/reference.md`
- Impact: Upstream backend updates can silently invalidate these workarounds, and failures may appear only on real Windows/WeChat combinations.
- Fix approach: Isolate backend adapters behind a narrow compatibility layer, gate workarounds by backend version, and add smoke tests against the packaged runtime.

**Non-reproducible packaging inputs:**
- Issue: `build_wechat_sender.ps1` installs `pyinstaller`, `wxauto4`, `wxautox4`, and other runtime packages without pinned versions. The offline `vendor/` directory is supported, but only `README.txt` is present.
- Files: `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`, `.cursor/skills/send-wechat-message/vendor/README.txt`
- Impact: The same source tree can produce different binaries over time, and breakage can come from upstream package changes rather than local edits.
- Fix approach: Pin build/runtime versions, commit a lock manifest, and vendor the exact wheels used for release builds.

**Source and distributed binary can drift:**
- Issue: The repository instructs users to run the committed binary at `dist/wechat-message-sender.exe`, while the test suite imports and tests only the Python source module.
- Files: `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`, `README.md`, `INSTALL.md`, `tests/test_send_wechat_message.py`
- Impact: A green unit test run does not prove that the checked-in executable matches current source behavior.
- Fix approach: Record binary provenance (hash + build metadata), or rebuild the release artifact in CI from the current source before distribution.

## Known Bugs

**Ambiguous fuzzy matching can select the wrong chat:**
- Symptoms: A partial contact or group name can resolve to a different visible session than the operator intended.
- Files: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, `.cursor/skills/send-wechat-message/SKILL.md`, `.cursor/skills/send-wechat-message/reference.md`
- Trigger: `resolve_target_chat_name()` auto-selects the shortest substring match when multiple matches exist, and `choose_search_result()` auto-picks the top scored search result once the threshold is met.
- Workaround: Use the full chat name, run `--list-sessions` first, or use `--dry-run` to confirm the opened chat before sending.

**File-send verification can report success on unrelated UI changes:**
- Symptoms: The command may return success even when file markers were not positively detected in the chat area.
- Files: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Trigger: `verify_files_sent()` falls back to success when `len(after_raw_items) > len(before_raw_items)`, even if the new raw UI items are not the expected file card or image markers.
- Workaround: Manually inspect the target conversation after file sends when reliability matters.

## Security Considerations

**Accidental disclosure risk from immediate send after fuzzy resolution:**
- Risk: The tool sends as soon as a chat is opened; there is no mandatory confirmation step after fuzzy matching.
- Files: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, `.cursor/skills/send-wechat-message/SKILL.md`
- Current mitigation: Docs tell the operator to prefer exact names and to confirm when multiple candidates look similar.
- Recommendations: Make exact match the default, require an explicit `--allow-fuzzy` flag for non-exact sends, or require `--dry-run` before first send to a fuzzy-resolved chat.

**Unsigned prebuilt executable is the default delivery path:**
- Risk: Users are directed to run the checked-in binary directly, but the repo does not publish an integrity check, signed release process, or reproducible build proof.
- Files: `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`, `README.md`, `INSTALL.md`, `.cursor/skills/send-wechat-message/SKILL.md`
- Current mitigation: Source code and local build scripts are present in the repo.
- Recommendations: Publish a checksum, sign release artifacts, or move distribution to CI-generated releases with attestations.

## Performance Bottlenecks

**UI polling reads full message and raw control lists repeatedly:**
- Problem: Success verification loops call `GetAllMessage()` and re-scan the chat UI tree every 300 ms for up to 8-10 seconds.
- Files: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Cause: `verify_message_sent()` and `verify_files_sent()` repeatedly call `get_messages_in_current_chat()` and `get_raw_message_items()` instead of diffing a narrow tail region.
- Improvement path: Track only the last observed items, use exponential backoff, and prefer backend-native send acknowledgements where available.

## Fragile Areas

**WeChat 4.x accessibility dependency:**
- Files: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, `INSTALL.md`, `.cursor/skills/send-wechat-message/SKILL.md`, `.cursor/skills/send-wechat-message/reference.md`
- Why fragile: The runtime depends on Windows desktop WeChat exposing UI Automation controls and, for 4.x, often requires `QT_ACCESSIBILITY=1` plus a full client restart.
- Safe modification: Validate any send/open-flow change on a real WeChat 4.x client with and without pre-existing open chats.
- Test coverage: No automated integration test covers this environment contract.

**Broad exception swallowing around backend and UI operations:**
- Files: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Why fragile: Many `except Exception` blocks convert backend-specific failures into retries, fallbacks, or empty results, which reduces observability and can hide the real break point.
- Safe modification: Replace generic catches with backend-specific exceptions where possible, and log structured context before fallback paths.
- Test coverage: Current tests do not exercise the retry/fallback branches against mocked backend failures.

**Cross-backend method assumptions:**
- Files: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Why fragile: The code assumes similar semantics across `wxauto4`, `wxautox4`, and `wxauto` for methods such as `ChatWith`, `SendMsg`, `SendFiles`, `GetSession`, and `CurrentChat`, but handles differences mainly with runtime trial-and-error.
- Safe modification: Introduce an explicit backend adapter per library instead of branching on method signatures inline.
- Test coverage: No compatibility matrix test exists for the three supported backend families.

## Scaling Limits

**Single-desktop, single-session execution model:**
- Current capacity: One interactive send flow per process, against one logged-in desktop WeChat instance on Windows.
- Limit: The codebase has no queueing, no parallel session model, and no headless/server mode; bulk sends and concurrent operators do not fit the current design.
- Scaling path: Move send requests behind an explicit job queue with per-chat confirmation and runtime telemetry before attempting multi-send workflows.

## Dependencies at Risk

**WeChat automation backends are not pinned:**
- Risk: API or behavior changes in `wxauto4`, `wxautox4`, or `wxauto` can break attach, chat selection, or message verification without any local source change.
- Impact: Build failures or runtime regressions in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` and `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`.
- Migration plan: Pin known-good versions, test them in CI, and keep vendored wheels for release builds.

**PyInstaller build tool is not pinned:**
- Risk: Packaging behavior can change between PyInstaller releases, especially around hidden imports and collected binaries.
- Impact: The produced executable in `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe` can fail differently from the source module.
- Migration plan: Pin PyInstaller, keep a release manifest, and smoke-test the built executable before committing it.

## Missing Critical Features

**No stable support for native voice-message bubbles:**
- Problem: The docs explicitly state that real WeChat voice-note automation is not supported; only existing audio files can be sent as files.
- Blocks: Voice-message workflows that require a true in-chat voice bubble instead of a file attachment.
- Files: `README.md`, `INSTALL.md`, `.cursor/skills/send-wechat-message/SKILL.md`, `.cursor/skills/send-wechat-message/reference.md`

## Test Coverage Gaps

**No end-to-end coverage for live WeChat interaction:**
- What's not tested: Attaching to WeChat, opening chats, fuzzy selection, sending text/files, and send verification against the real UI tree.
- Files: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, `tests/test_send_wechat_message.py`
- Risk: The highest-risk behavior depends on external UI state, but the current tests cover only pure helper logic and argument parsing.
- Priority: High

**Packaged artifact and release flow are untested:**
- What's not tested: The PyInstaller build pipeline and the checked-in `dist/wechat-message-sender.exe`.
- Files: `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`, `.cursor/skills/send-wechat-message/wechat_message_sender.spec`, `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`
- Risk: Distribution regressions can ship unnoticed even when source-level tests pass.
- Priority: High

---

*Concerns audit: 2026-04-24*
