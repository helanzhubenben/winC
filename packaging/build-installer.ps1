# Builds the Fishpool frontend, Windows launcher, and Inno Setup installer.
[CmdletBinding()]
param(
    [string]$Version = '1.0.0'
)

$ErrorActionPreference = 'Stop'
$rootDirectory = Split-Path -Parent $PSScriptRoot
$backendDirectory = Join-Path $rootDirectory 'backend'
$frontendDirectory = Join-Path $rootDirectory 'frontend'
$pythonExecutable = Join-Path $backendDirectory '.venv\Scripts\python.exe'
$installerCompiler = @(
    (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'),
    (Join-Path $env:ProgramFiles 'Inno Setup 6\ISCC.exe'),
    (Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe')
) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

function Assert-CommandPath {
    param([string]$Path, [string]$Message)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw $Message
    }
}

Assert-CommandPath $pythonExecutable '未找到 backend\.venv\Scripts\python.exe，请先创建后端虚拟环境。'
Assert-CommandPath $installerCompiler '未找到 Inno Setup 6。请安装后重新执行此脚本。'

Push-Location $frontendDirectory
try {
    npm ci
    npm run build
}
finally {
    Pop-Location
}

$templateDirectory = Join-Path $backendDirectory 'templates\fishpool'
New-Item -ItemType Directory -Force -Path $templateDirectory | Out-Null
Copy-Item (Join-Path $backendDirectory 'static\frontend\index.html') (Join-Path $templateDirectory 'index.html') -Force

& $pythonExecutable -m pip install -r (Join-Path $backendDirectory 'requirements.txt') -r (Join-Path $backendDirectory 'requirements-packaging.txt')
$env:FISHPOOL_PACKAGED = '1'
$env:FISHPOOL_RESOURCE_DIR = $backendDirectory
& $pythonExecutable (Join-Path $backendDirectory 'manage.py') collectstatic --noinput
& $pythonExecutable -m PyInstaller --noconfirm --clean --windowed --name Fishpool --paths $backendDirectory --distpath (Join-Path $PSScriptRoot 'dist') --workpath (Join-Path $PSScriptRoot 'build') --specpath (Join-Path $PSScriptRoot 'build') --add-data "$backendDirectory\staticfiles;staticfiles" --add-data "$backendDirectory\templates;templates" --add-data "$rootDirectory\docs\templates;docs\templates" --hidden-import django.db.backends.sqlite3 --hidden-import django.core.management.commands.migrate --hidden-import django.contrib.auth --hidden-import django.contrib.contenttypes --hidden-import django.contrib.sessions --hidden-import django.contrib.messages --hidden-import django.contrib.staticfiles --hidden-import rest_framework --hidden-import corsheaders --hidden-import django_filters --collect-all whitenoise --collect-data django --collect-data rest_framework --collect-data customers --collect-submodules fishpool --collect-submodules customers (Join-Path $backendDirectory 'fishpool\launcher.py')
Get-ChildItem -Path (Join-Path $PSScriptRoot 'dist\Fishpool') -Filter 'db.sqlite3*' -File -Recurse | Remove-Item -Force
Remove-Item Env:FISHPOOL_RESOURCE_DIR -ErrorAction SilentlyContinue
Remove-Item Env:FISHPOOL_PACKAGED -ErrorAction SilentlyContinue

$packageDirectory = $PSScriptRoot
New-Item -ItemType Directory -Force -Path (Join-Path $packageDirectory 'dist') | Out-Null
$env:FISHPOOL_VERSION = $Version
Push-Location $packageDirectory
try {
    & $installerCompiler 'Fishpool.iss'
}
finally {
    Pop-Location
}

Write-Host "安装包已生成：$(Join-Path $packageDirectory "dist\Fishpool-Setup-$Version.exe")"
