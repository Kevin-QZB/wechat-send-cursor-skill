# Codebase Testing

Date: 2026-04-24

## Current Test Setup

- The repo uses Python's built-in `unittest` framework.
- The active test file is `tests/test_send_wechat_message.py`.
- Tests import the script module directly from `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` by prepending the script directory to `sys.path`.

## What Is Covered

The current tests cover pure helper behavior, including:

- CLI argument parsing for repeated `--file` flags
- Validation that message and file payloads cannot be supplied together
- Validation that an empty payload is rejected
- File path normalization and deduplication
- Marker extraction for image vs non-image file sends
- Text matching helpers for raw UI items and parsed message lists

Evidence: `tests/test_send_wechat_message.py`.

## What Is Not Covered

The test suite does not currently cover:

- Real WeChat process attachment
- `wxauto4` / `wxautox4` import behavior on actual Windows machines
- Live session search and chat switching
- Actual text or file send operations
- Packaging flow in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- End-to-end verification against the shipped exe in `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`

## Testing Characteristics

- Tests are fast and local because they avoid GUI automation.
- They are regression checks for helper logic rather than full confidence checks for the product.
- The current structure is appropriate for smoke coverage but leaves the most failure-prone behavior untested.

## Suggested Mental Model

Treat the current test suite as a guardrail for utility logic, not as proof that the skill works end to end on a real Windows desktop with real WeChat state.

## Related Files

- `tests/test_send_wechat_message.py`
- `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
- `README.md`

## Gaps Worth Watching

- Packaging and runtime drift between source and checked-in exe
- Desktop UI automation regressions that unit tests cannot observe
- Environment-specific failures around accessibility, WeChat version, or backend availability
# Testing Patterns

**Analysis Date:** 2026-04-24

## Test Framework

**Runner:**
- Python `unittest` from the standard library.
- Config: Not detected. No `pytest.ini`, `conftest.py`, `tox.ini`, or `pyproject.toml` is present at the workspace root.

**Assertion Library:**
- `unittest.TestCase` assertions such as `assertEqual`, `assertTrue`, and `assertRaises` in `tests/test_send_wechat_message.py`.

**Run Commands:**
```bash
python -m unittest discover -s tests      # Run all discovered tests
python -m unittest tests.test_send_wechat_message  # Run the current test module
Not applicable                            # Coverage command is not configured
```

**Environment Note:**
- In the current shell environment, `python -m unittest tests.test_send_wechat_message` fails before tests run because `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` uses built-in generic syntax such as `List[tuple[str, str]]` and `set[str]`, which is not importable on Python 3.8.
- The repository does not declare the required Python version in `pyproject.toml`, `setup.cfg`, or similar, so the effective test runtime requirement is implicit in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

## Test File Organization

**Location:**
- Tests live in a dedicated top-level `tests/` directory rather than next to the implementation.
- The only detected automated test file is `tests/test_send_wechat_message.py`.

**Naming:**
- Test files follow `test_*.py`, e.g. `tests/test_send_wechat_message.py`.
- Test methods follow `test_<behavior>()`, e.g. `test_resolve_send_payload_rejects_both_message_and_file()` in `tests/test_send_wechat_message.py`.

**Structure:**
```text
tests/
  test_send_wechat_message.py
```

## Test Structure

**Suite Organization:**
```python
class SendWeChatMessageTests(unittest.TestCase):
    def test_parse_args_accepts_repeated_file_flags(self) -> None:
        ...

    def test_resolve_send_payload_rejects_both_message_and_file(self) -> None:
        ...
```

**Patterns:**
- The suite in `tests/test_send_wechat_message.py` imports the script module directly after adding `.cursor/skills/send-wechat-message/scripts` to `sys.path`.
- Tests target pure helpers and argument parsing in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, not live WeChat automation.
- Setup is inlined inside each test rather than centralized with `setUp()` or `tearDown()`.
- Temporary filesystem state is created with `tempfile.TemporaryDirectory()` and cleaned automatically in `tests/test_send_wechat_message.py`.

## Mocking

**Framework:** Not detected.

**Patterns:**
```python
# No unittest.mock, patch(), or monkeypatch usage is present in `tests/test_send_wechat_message.py`.
# Tests currently rely on pure functions plus temporary files instead of mocked backends.
```

**What to Mock:**
- Mock Windows and WeChat integration boundaries when expanding coverage for `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`: `importlib.import_module`, `subprocess.Popen`, `time.sleep`, `wx.SendMsg`, `wx.SendFiles`, `wx.ChatWith`, `wx.GetAllMessage`, and `wx.ChatBox.msgbox.GetChildren`.
- Mock session search results and chat metadata for `open_chat()`, `resolve_target_chat_name()`, `verify_message_sent()`, and `verify_files_sent()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

**What NOT to Mock:**
- Keep pure helpers real: `normalize_file_paths()`, `resolve_send_payload()`, `collect_file_marker_groups()`, `raw_item_contains_text()`, and `message_list_contains_text()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Keep temp-file based path normalization tests close to the current style in `tests/test_send_wechat_message.py`.

## Fixtures and Factories

**Test Data:**
```python
with tempfile.TemporaryDirectory() as tmpdir:
    sample = Path(tmpdir) / "sample.txt"
    sample.write_text("hello", encoding="utf-8")
```

**Location:**
- Fixtures are inline inside `tests/test_send_wechat_message.py`.
- No shared fixture module, factory helper, or sample-data directory is present.

## Coverage

**Requirements:** None enforced.

**View Coverage:**
```bash
Not applicable
```

**Observed Coverage Shape:**
- Covered behaviors are argument parsing, payload exclusivity, file-path normalization, image marker generation, and helper substring checks in `tests/test_send_wechat_message.py`.
- No automated tests cover the main control flow in `main()`, Windows gating in `main()`, backend import fallback in `import_wechat_backend()`, app launch behavior in `launch_wechat()`, chat switching in `open_chat()`, or send verification loops in `verify_message_sent()` and `verify_files_sent()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

## Test Types

**Unit Tests:**
- Present, but narrow.
- The current suite in `tests/test_send_wechat_message.py` focuses on deterministic helpers from `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

**Integration Tests:**
- Not detected.
- There are no automated tests that exercise a real or simulated WeChat backend, the packaged `exe`, or the PowerShell build script `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`.

**E2E Tests:**
- Not used.
- Manual command examples in `README.md`, `INSTALL.md`, and `.cursor/skills/send-wechat-message/reference.md` act as operational verification guidance rather than executable E2E automation.

## Common Patterns

**Async Testing:**
```python
# No async test pattern is present.
# Time-based production loops exist in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`,
# but no tests patch `time.sleep()` or assert retry timing.
```

**Error Testing:**
```python
with self.assertRaises(swm.WeChatSendError):
    swm.resolve_send_payload("", [])
```

**Current Gaps With Evidence:**
- No tests cover fuzzy chat matching logic in `resolve_target_chat_name()` and `choose_search_result()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- No tests cover message verification fallback from `GetAllMessage()` to raw UI items in `verify_message_sent()` and `verify_files_sent()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- No tests cover build and packaging behavior in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` and `.cursor/skills/send-wechat-message/wechat_message_sender.spec`.
- No tests cover Windows-only startup rules and backend import compatibility in `main()`, `ensure_tkinter_stub()`, and `import_wechat_backend()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

---

*Testing analysis: 2026-04-24*
