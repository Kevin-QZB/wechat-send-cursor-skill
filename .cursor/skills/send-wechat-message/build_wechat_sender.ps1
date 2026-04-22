[CmdletBinding()]
param(
    [switch]$OneFile,
    [switch]$Clean,
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $Root ".build-venv"
$DistDir = Join-Path $Root "dist"
$BuildDir = Join-Path $Root "build"
$VendorDir = Join-Path $Root "vendor"
$VenvMeta = Join-Path $VenvDir ".python-path.txt"
$SpecPath = Join-Path $Root "wechat_message_sender.spec"
$ScriptPath = Join-Path $Root "scripts\send_wechat_message.py"
$DistReadmeTemplate = Join-Path $Root "dist-readme-template.txt"
$DistReadmePath = Join-Path $DistDir "wechat-message-sender\README.txt"

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Get-VenvPython {
    return Join-Path $VenvDir "Scripts\python.exe"
}

function Get-VenvPip {
    return Join-Path $VenvDir "Scripts\pip.exe"
}

function Ensure-BuildVenv {
    $pythonCommand = Get-Command $Python -ErrorAction Stop
    $resolvedPython = $pythonCommand.Source
    $needRecreate = $false

    if (-not (Test-Path (Get-VenvPython))) {
        $needRecreate = $true
    } elseif (Test-Path $VenvMeta) {
        $previousPython = (Get-Content $VenvMeta -ErrorAction SilentlyContinue | Select-Object -First 1)
        if ($previousPython -ne $resolvedPython) {
            $needRecreate = $true
        }
    } else {
        $needRecreate = $true
    }

    if ($needRecreate -and (Test-Path $VenvDir)) {
        Write-Step "Remove stale build virtualenv"
        Remove-Item $VenvDir -Recurse -Force
    }

    if ($needRecreate) {
        Write-Step "Create build virtualenv"
        & $resolvedPython -m venv $VenvDir
        Set-Content -Path $VenvMeta -Value $resolvedPython -Encoding ASCII
    }
}

function Install-BaseDeps {
    Write-Step "Install base build dependencies"
    & (Get-VenvPython) -m pip install --upgrade pip setuptools wheel pyinstaller
}

function Install-WeChatBackend {
    $pythonExe = Get-VenvPython

    if (Test-Path $VendorDir) {
        $localWheel = Get-ChildItem $VendorDir -Filter "*.whl" | Where-Object {
            $_.Name -match "wxauto4|wxautox4|wxauto|uiautomation|comtypes|pywin32"
        }
        if ($localWheel) {
            Write-Step "Install offline wheels from vendor"
            & $pythonExe -m pip install ($localWheel.FullName)
        }
    }

    foreach ($existing in @("wxauto4", "wxautox4", "wxauto")) {
        if (Test-PythonModule $existing) {
            Write-Step "Detected installed backend: $existing"
            return
        }
    }

    $attempts = @(
        "wxauto4",
        "wxautox4",
        "git+https://github.com/cluic/wxauto4.git"
    )

    foreach ($item in $attempts) {
        try {
            Write-Step "Try backend dependency: $item"
            & $pythonExe -m pip install $item
            if ($LASTEXITCODE -eq 0) {
                return
            }
        } catch {
        }
    }

    $message = @(
        "Failed to install a WeChat automation backend automatically.",
        "",
        "Options:",
        "1. Put downloaded wheels into $VendorDir",
        "2. Or run manually:",
        "   $(Get-VenvPython) -m pip install wxauto4",
        "   or",
        "   $(Get-VenvPython) -m pip install wxautox4",
        "   or",
        "   $(Get-VenvPython) -m pip install git+https://github.com/cluic/wxauto4.git"
    ) -join [Environment]::NewLine
    throw $message
}

function Install-RuntimeDeps {
    Write-Step "Install common runtime dependencies"
    & (Get-VenvPython) -m pip install pywin32 pillow comtypes pyperclip psutil tenacity colorama
}

function Test-PythonModule([string]$ModuleName) {
    if ($ModuleName -eq "wxauto4") {
        $code = @"
import sys, types
tk = types.ModuleType("tkinter")
tk.Tk = type("Tk", (), {})
tk.Toplevel = type("Toplevel", (), {})
tk.Misc = type("Misc", (), {})
tk.END = "end"
sys.modules["tkinter"] = tk
import wxauto4
"@
    } else {
        $code = "import $ModuleName"
    }
    & (Get-VenvPython) -c $code
    return $LASTEXITCODE -eq 0
}

function Run-Build {
    if ($Clean) {
        Write-Step "Clean old build outputs"
        if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
        if (Test-Path $DistDir) { Remove-Item $DistDir -Recurse -Force }
    }

    Write-Step "Run PyInstaller build"

    if ($OneFile) {
        $args = @(
            "-m", "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onefile",
            "--name", "wechat-message-sender",
            "--hidden-import", "pythoncom",
            "--hidden-import", "pywintypes",
            "--hidden-import", "win32timezone",
            "--distpath", $DistDir,
            "--workpath", $BuildDir
        )

        foreach ($pkg in @("wxauto4", "wxautox4", "wxauto", "comtypes", "uiautomation")) {
            if (Test-PythonModule $pkg) {
                $args += @("--collect-all", $pkg)
            }
        }

        $args += $ScriptPath
        & (Get-VenvPython) @args
    } else {
        & (Get-VenvPython) -m PyInstaller `
            --noconfirm `
            --clean `
            --distpath $DistDir `
            --workpath $BuildDir `
            $SpecPath
    }
}

function Write-DistReadme {
    if ((Test-Path $DistReadmeTemplate) -and (Test-Path (Split-Path $DistReadmePath -Parent))) {
        Copy-Item $DistReadmeTemplate $DistReadmePath -Force
    }
}

function Remove-DistributionMetadata {
    $folderPath = Join-Path $DistDir "wechat-message-sender"
    if (-not (Test-Path $folderPath)) {
        return
    }

    Get-ChildItem $folderPath -Recurse -Filter "direct_url.json" -File -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item $_.FullName -Force
    }
}

function Pack-Distribution {
    $zipPath = Join-Path $DistDir "wechat-message-sender.zip"
    $folderPath = Join-Path $DistDir "wechat-message-sender"
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    if (Test-Path $folderPath) {
        Compress-Archive -Path (Join-Path $folderPath "*") -DestinationPath $zipPath -Force
    }
}

Ensure-BuildVenv
Install-BaseDeps
Install-WeChatBackend
Install-RuntimeDeps
Run-Build
Write-DistReadme
Remove-DistributionMetadata
Pack-Distribution

Write-Step "Build completed"
Write-Host "Build finished" -ForegroundColor Green
Write-Host "Output: $DistDir" -ForegroundColor Green
