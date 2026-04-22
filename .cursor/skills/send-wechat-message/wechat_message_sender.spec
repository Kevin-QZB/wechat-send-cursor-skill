# -*- mode: python ; coding: utf-8 -*-

import importlib.util
from pathlib import Path

from PyInstaller.utils.hooks import collect_all


project_dir = Path(SPECPATH)
script_path = project_dir / "scripts" / "send_wechat_message.py"


def add_package(name, datas, binaries, hiddenimports):
    try:
        d, b, h = collect_all(name)
    except Exception:
        return
    datas += d
    binaries += b
    hiddenimports += h


def add_package_binaries(name, datas, binaries, hiddenimports):
    spec = importlib.util.find_spec(name)
    if spec is None or not spec.submodule_search_locations:
        return

    package_dir = Path(next(iter(spec.submodule_search_locations)))
    package_root = package_dir.parent

    for file_path in package_dir.rglob("*"):
        if file_path.is_dir():
            continue
        destination = str(file_path.relative_to(package_root).parent)
        if file_path.suffix.lower() in {".pyd", ".dll"}:
            binaries.append((str(file_path), destination))
        elif file_path.suffix.lower() in {".pyi"}:
            datas.append((str(file_path), destination))

    hiddenimports += [
        name,
        f"{name}.uia",
        f"{name}.ui",
        f"{name}.msgs",
        f"{name}.utils",
    ]


datas = []
binaries = []
hiddenimports = [
    "pythoncom",
    "pywintypes",
    "win32timezone",
]

for package_name in (
    "wxauto4",
    "wxautox4",
    "wxauto",
    "comtypes",
    "uiautomation",
    "win32com",
    "pyperclip",
    "psutil",
    "tenacity",
    "PIL",
):
    add_package(package_name, datas, binaries, hiddenimports)

add_package_binaries("wxauto4", datas, binaries, hiddenimports)


a = Analysis(
    [str(script_path)],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name="wechat-message-sender",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="wechat-message-sender",
)
