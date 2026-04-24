# Codebase Structure

Date: 2026-04-24

## Top-Level Layout

- `.cursor/` - Cursor-facing assets, including the actual skill implementation directory
- `tests/` - Python unit tests for helper logic
- `wxauto_logs/` - runtime log output directory
- `README.md` - project overview and usage
- `INSTALL.md` - installation and troubleshooting guide
- `.gitignore` - ignored build and runtime artifacts

## Skill Directory Layout

The core implementation lives under `.cursor/skills/send-wechat-message/`.

Key locations:

- `.cursor/skills/send-wechat-message/SKILL.md` - skill entry instructions for agents
- `.cursor/skills/send-wechat-message/reference.md` - maintainer reference and troubleshooting
- `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py` - Python source implementation
- `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` - packaging automation
- `.cursor/skills/send-wechat-message/dist/` - distributable exe output
- `.cursor/skills/send-wechat-message/vendor/` - optional offline dependency wheels and related binaries
- `.cursor/skills/send-wechat-message/dist-readme-template.txt` - packaged README template

## Source Organization

There is only one real source module in the current repo:

- `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`

That file contains CLI parsing, backend import logic, chat resolution, send behavior, and delivery verification. There is no `src/` tree or multi-module package split.

## Test Organization

- `tests/test_send_wechat_message.py` imports the script module by injecting `.cursor/skills/send-wechat-message/scripts/` into `sys.path`.
- Tests are colocated under a single `tests/` directory and currently focus on pure helper functions rather than live WeChat UI automation.

## Naming Patterns

- Python code uses `snake_case` for functions such as `resolve_target_chat_name()` and `verify_files_sent()`.
- Constants are uppercase, for example `IMAGE_FILE_SUFFIXES`.
- PowerShell functions are verb-noun style such as `Install-BaseDeps` and `Run-Build`.
- Documentation files are uppercase or title-like markdown names such as `SKILL.md`, `README.md`, and `INSTALL.md`.

## Artifact Boundaries

- Runtime source and packaging logic live together under the skill directory.
- Built outputs are intentionally present in the repository, not only ignored local outputs.
- Temporary build products like `.build-venv/`, `build/`, and unpacked dist directories are excluded in `.gitignore`.

## Practical Navigation Order

If you are new to this repo, read in this order:

1. `README.md`
2. `.cursor/skills/send-wechat-message/SKILL.md`
3. `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
4. `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`
5. `tests/test_send_wechat_message.py`
6. `.cursor/skills/send-wechat-message/reference.md`
# Codebase Structure

**Analysis Date:** 2026-04-24

## Directory Layout

```text
[project-root]/
|-- .cursor/
|   `-- skills/
|       `-- send-wechat-message/   # Skill package, runtime source, build assets, and distributed binary
|-- .planning/
|   `-- codebase/                  # Generated codebase mapping documents
|-- tests/                         # Unit tests for script helpers
|-- wxauto_logs/                   # Runtime log output ignored by git
|-- .gitignore                     # Ignore rules for build outputs and logs
|-- INSTALL.md                     # End-user installation guide
`-- README.md                      # Repository overview and usage entry
```

## Directory Purposes

**`.cursor/skills/send-wechat-message/`:**
- Purpose: Hold the complete distributable Cursor skill.
- Contains: User-facing skill docs, maintainer docs, runtime source, build scripts, packaging spec, vendor placeholder files, and the packaged executable.
- Key files: `.cursor/skills/send-wechat-message/SKILL.md`, `.cursor/skills/send-wechat-message/reference.md`, `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`, `.cursor/skills/send-wechat-message/wechat_message_sender.spec`, `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`

**`.cursor/skills/send-wechat-message/scripts/`:**
- Purpose: Hold Python runtime source code.
- Contains: The single executable source module for sending messages and files through desktop WeChat.
- Key files: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`

**`.cursor/skills/send-wechat-message/dist/`:**
- Purpose: Hold packaged release artifacts consumed by users and agents.
- Contains: The committed onefile executable `wechat-message-sender.exe`; the build pipeline can also place onedir output and zip archives here.
- Key files: `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`

**`.cursor/skills/send-wechat-message/vendor/`:**
- Purpose: Stage optional offline dependency wheels for rebuilds.
- Contains: Documentation plus any maintainer-supplied wheels or binary inputs.
- Key files: `.cursor/skills/send-wechat-message/vendor/README.txt`

**`tests/`:**
- Purpose: Hold repository tests.
- Contains: `unittest` coverage for CLI parsing and helper-level behavior.
- Key files: `tests/test_send_wechat_message.py`

**`.planning/codebase/`:**
- Purpose: Hold generated architecture and structure analysis for GSD workflows.
- Contains: Mapping documents such as `.planning/codebase/ARCHITECTURE.md` and `.planning/codebase/STRUCTURE.md`.
- Key files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`

## Key File Locations

**Entry Points:**
- `.cursor/skills/send-wechat-message/SKILL.md`: Cursor skill entry contract for agents.
- `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`: Default runtime entry for end users and agents.
- `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`: Source-level CLI entry and runtime implementation.
- `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`: Maintainer build entry for regenerating packaged artifacts.

**Configuration:**
- `.gitignore`: Ignores build virtualenvs, build output folders, cached Python artifacts, logs, and vendor binaries.
- `.cursor/skills/send-wechat-message/wechat_message_sender.spec`: PyInstaller packaging configuration for the onedir build path.
- `.cursor/skills/send-wechat-message/dist-readme-template.txt`: Template copied into packaged distributions.

**Core Logic:**
- `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`: All runtime behavior, including backend probing, session resolution, payload sending, and verification.

**Testing:**
- `tests/test_send_wechat_message.py`: Unit tests importing the runtime script directly from `.cursor/skills/send-wechat-message/scripts/`.

**Documentation:**
- `README.md`: Repository overview, usage, and distribution expectations.
- `INSTALL.md`: End-user installation and validation instructions.
- `.cursor/skills/send-wechat-message/reference.md`: Maintainer troubleshooting and build guidance.

## Naming Conventions

**Files:**
- Python source uses `snake_case`, as in `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`.
- Packaged executables and release folders use `kebab-case`, as in `.cursor/skills/send-wechat-message/dist/wechat-message-sender.exe`.
- Top-level user docs use uppercase names, as in `README.md` and `INSTALL.md`.
- The PyInstaller spec follows the runtime module name in `snake_case`, as in `.cursor/skills/send-wechat-message/wechat_message_sender.spec`.

**Directories:**
- Feature and utility directories are lowercase, as in `tests/`, `dist/`, and `vendor/`.
- The skill directory uses a descriptive `kebab-case` name, as in `.cursor/skills/send-wechat-message/`.

## Where to Add New Code

**New Feature:**
- Primary code: `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`
- Tests: `tests/test_send_wechat_message.py`

**New Component/Module:**
- Implementation: Add new helper modules under `.cursor/skills/send-wechat-message/scripts/` and import them from `.cursor/skills/send-wechat-message/scripts/send_wechat_message.py`

**Utilities:**
- Shared runtime helpers: Keep them under `.cursor/skills/send-wechat-message/scripts/`
- Build helpers: Keep them beside `.cursor/skills/send-wechat-message/build_wechat_sender.ps1` only if they are packaging-specific

**User-Facing Docs:**
- Skill invocation rules: `.cursor/skills/send-wechat-message/SKILL.md`
- End-user setup and usage: `README.md` and `INSTALL.md`
- Troubleshooting and rebuild instructions: `.cursor/skills/send-wechat-message/reference.md`

## Special Directories

**`.cursor/skills/send-wechat-message/dist/`:**
- Purpose: Distribution output directory for packaged binaries.
- Generated: Yes
- Committed: Yes for the current onefile executable `wechat-message-sender.exe`; the ignored onedir folder and zip outputs are excluded by `.gitignore`

**`.cursor/skills/send-wechat-message/vendor/`:**
- Purpose: Offline dependency staging area for rebuilds.
- Generated: No
- Committed: Documentation is committed; wheels and downloaded binaries are ignored by `.gitignore`

**`.cursor/skills/send-wechat-message/.build-venv/`:**
- Purpose: Build-only virtual environment created by `.cursor/skills/send-wechat-message/build_wechat_sender.ps1`.
- Generated: Yes
- Committed: No, ignored by `.gitignore`

**`.cursor/skills/send-wechat-message/build/`:**
- Purpose: PyInstaller work directory created during rebuilds.
- Generated: Yes
- Committed: No, ignored by `.gitignore`

**`wxauto_logs/`:**
- Purpose: Runtime logs produced during actual use.
- Generated: Yes
- Committed: No, ignored by `.gitignore`

---

*Structure analysis: 2026-04-24*
