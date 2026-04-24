# Codebase Conventions

Date: 2026-04-24

## Product-Level Convention

The strongest convention in this repo is "distribution first":

- User docs in `README.md`, `INSTALL.md`, and `.cursor/skills/send-wechat-message/SKILL.md` repeatedly instruct consumers to use the shipped exe first.
- Source code and build tooling exist mainly to maintain that distributable artifact.
- The repo explicitly discourages casual dependency installation or local rebuilds during normal skill usage.

## Python Coding Style

Observed in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`:

- Functions are small to medium-sized helpers with descriptive `snake_case` names.
- Custom domain errors use a dedicated exception type: `WeChatSendError`.
- Types are annotated on many helpers using `typing.Any`, `List`, `Optional`, and `Tuple`.
- `pathlib.Path` is preferred for path normalization.
- Compatibility logic is implemented with defensive `try/except` blocks rather than strict fail-fast imports.

## Error Handling Pattern

- User-facing runtime failures are normalized into `WeChatSendError`.
- The script prefers layered fallback behavior before failing:
  - multiple backend imports
  - multiple attach attempts
  - multiple chat-open strategies
  - multiple send call signatures
- Final CLI exit handling is centralized in the `if __name__ == "__main__"` block of `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

## Compatibility Convention

- The code is written for real-world desktop automation instability, not for ideal APIs.
- Library quirks are patched inline, for example `patch_wxauto4_profile_popup()`.
- Verification often checks both parsed message APIs and raw UI child nodes to survive backend inconsistencies.

## PowerShell Build Style

Observed in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`:

- Functions are grouped by responsibility: environment setup, dependency install, build, packaging.
- `$ErrorActionPreference = "Stop"` is used to make failures explicit.
- Helper functions use PascalCase verb-noun naming like `Ensure-BuildVenv` and `Pack-Distribution`.
- Console progress uses a dedicated `Write-Step` helper.

## Documentation Convention

- Docs are written for both humans and agents.
- Commands are shown as runnable PowerShell snippets.
- Operational guidance is repeated in multiple files on purpose so that both end users and AI agents see the same install rule.
- The skill contract in `.cursor/skills/send-wechat-message/SKILL.md` is treated as executable behavior guidance, not just prose.

## Testing Convention

- Tests in `tests/test_send_wechat_message.py` focus on deterministic utility behavior.
- The test suite avoids live WeChat dependencies.
- Imports are done by path injection instead of packaging the module as an installable distribution.

## Things Not Present

- No formatter config such as `black`, `ruff`, or `isort`
- No repo-wide lint config
- No CI workflow in the visible repo contents
- No formal package metadata file for Python distribution
# Coding Conventions

**Analysis Date:** 2026-04-24

## Naming Patterns

**Files:**
- Python source and tests use `snake_case` file names, e.g. `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` and `tests/test_send_wechat_message.py`.
- PowerShell maintenance scripts use lower-case task-oriented names with underscores, e.g. `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`.
- User-facing documentation files use upper-case topic names, e.g. `README.md` and `INSTALL.md`.

**Functions:**
- Python functions use `snake_case`, e.g. `import_wechat_backend()`, `resolve_target_chat_name()`, and `collect_file_marker_groups()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- PowerShell functions use Verb-Noun style with PascalCase segments, e.g. `Ensure-BuildVenv`, `Install-WeChatBackend`, and `Write-Step` in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`.

**Variables:**
- Local Python variables use `snake_case`, e.g. `last_error`, `target_norm`, `before_raw_items`, and `file_paths` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Module-level constants use `UPPER_CASE`, e.g. `IMAGE_FILE_SUFFIXES` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- PowerShell script variables use PascalCase with a leading `$`, e.g. `$Root`, `$VenvDir`, and `$DistDir` in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`.

**Types:**
- Python classes use PascalCase, e.g. `WeChatSendError` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` and `SendWeChatMessageTests` in `tests/test_send_wechat_message.py`.
- Type hints are present on most Python helpers and test methods, using `Path`, `Optional[...]`, `Tuple[...]`, `List[...]`, and built-in generics such as `list[str]` and `set[str]` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

## Code Style

**Formatting:**
- No repository-level formatter config is detected: `pyproject.toml`, `setup.cfg`, `.flake8`, `.ruff.toml`, `.prettierrc*`, and `eslint.config.*` are not present at the workspace root.
- Follow the style already present in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`: four-space indentation, blank lines between top-level functions, trailing commas in multi-line literals, and one helper per focused behavior.
- Keep user-visible CLI strings in Chinese, matching `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`, `README.md`, and `INSTALL.md`.

**Linting:**
- No active lint configuration file is detected in the repository.
- Inline suppressions show the implicit lint baseline: `# noqa: E402` in `tests/test_send_wechat_message.py`, `# noqa: F401` and `# type: ignore` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Treat those suppressions as narrowly scoped compatibility exceptions, not a reason to skip typing or import hygiene elsewhere.

## Import Organization

**Order:**
1. Python standard library imports first, e.g. `argparse`, `difflib`, `importlib`, `os`, `subprocess`, `sys`, and `time` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
2. Standard-library support imports from `pathlib` and `typing` next in the same block in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
3. Local script import after path bootstrapping in tests, e.g. `sys.path.insert(...)` followed by `import send_wechat_message as swm` in `tests/test_send_wechat_message.py`.

**Path Aliases:**
- Not used.
- Tests import the script directly by prepending `.cursor/skills/send-wechat-message/scripts` to `sys.path` in `tests/test_send_wechat_message.py` instead of importing through a package.

## Error Handling

**Patterns:**
- Raise the custom exception `WeChatSendError` for user-facing failures in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`; examples include missing payload, missing files, chat switch failure, and send verification failure.
- Use guard clauses and early returns aggressively to keep happy paths flat, e.g. `patch_wxauto4_profile_popup()`, `normalize_file_paths()`, and `choose_search_result()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Compatibility helpers often swallow backend-specific exceptions and continue with fallbacks, e.g. `switch_to_chat_page()`, `get_messages_in_current_chat()`, `get_raw_message_items()`, and several `try`/`except` fallback branches in `open_chat()` and `attach_wechat()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- The CLI boundary converts domain errors into exit codes in the `if __name__ == "__main__"` block of `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`: `main()` returns `0` on success, and `WeChatSendError` is printed to `stderr` before exiting with status `1`.

## Logging

**Framework:** `print`

**Patterns:**
- Use `print(...)` for user-visible status, compatibility notices, fuzzy-match diagnostics, dry-run output, and success confirmation in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Use `Write-Host` in `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` for build-phase progress updates via `Write-Step`.
- There is no structured logger, log level abstraction, or centralized logging helper in the repository.

## Comments

**When to Comment:**
- Comments are sparse and reserved for compatibility or non-obvious behavior, e.g. the inline note in `verify_files_sent()` about delayed file cards in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Prefer self-contained helper names over explanatory inline comments; the main Python file expresses intent through narrow functions such as `message_signature()`, `search_result_contents()`, and `verify_message_sent()`.

**JSDoc/TSDoc:**
- Not applicable.
- Python docstrings appear only where the behavior is surprising or environment-specific, e.g. `patch_wxauto4_profile_popup()` and `ensure_tkinter_stub()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

## Function Design

**Size:** Helpers are mostly small and single-purpose, but the CLI orchestration functions `open_chat()` and `main()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` are the accepted larger coordinators.

**Parameters:** Functions prefer explicit primitive inputs over config objects, e.g. `(wx, variant, who, message, before)` in `verify_message_sent()` and `(message, file_args)` in `resolve_send_payload()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

**Return Values:**
- Pure helpers return normalized values or booleans, e.g. `normalize_name()`, `collect_file_labels()`, `raw_item_contains_text()`, and `message_list_contains_text()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Side-effecting workflow functions return `None` and signal failure by raising `WeChatSendError`, e.g. `send_message()`, `send_files()`, and `verify_files_sent()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

## Module Design

**Exports:**
- The Python script is a flat utility module with top-level helper functions plus one CLI entry point, all defined in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Tests call helpers directly from the imported module alias `swm` in `tests/test_send_wechat_message.py`; there is no public package API layer.

**Barrel Files:** Not used.

**Additional Notes:**
- The repository does not declare a Python version in `pyproject.toml` or similar, but `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` uses built-in generic syntax such as `list[tuple[str, str]]` and `set[str]`, which requires Python 3.9+.
- Because tests import the script directly, keep import-time side effects minimal. The current module follows this rule by deferring Windows checks and backend attachment to `main()` in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.

---

*Convention analysis: 2026-04-24*
