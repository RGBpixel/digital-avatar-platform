$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $taskRoot
$taskBasePython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$taskTemp = Join-Path $taskRoot '.tts-tmp'
New-Item -ItemType Directory -Path $taskTemp -Force | Out-Null
$env:TEMP = $taskTemp
$env:TMP = $taskTemp
$env:HF_HOME = Join-Path $taskRoot 'models\.hf-cache'
$taskPython = Join-Path $taskRoot '.venv-tts\Scripts\python.exe'
if (!(Test-Path -LiteralPath $taskPython)) { & $taskBasePython -m venv .venv-tts; if ($LASTEXITCODE -ne 0) { exit 1 } }
& $taskPython -m ensurepip --upgrade --default-pip
if ($LASTEXITCODE -ne 0) { exit 1 }
& $taskPython -c "import torch; raise SystemExit(0 if torch.version.cuda else 1)"
if ($LASTEXITCODE -ne 0) {
  & $taskPython -m pip install torch==2.14.1 torchaudio==2.11.0 --index-url https://download.pytorch.org/whl/cpu --cache-dir .tts-tmp/pip-cache
  if ($LASTEXITCODE -ne 0) { exit 1 }
}
& $taskPython -m pip install -r services/tts/requirements.txt --cache-dir .tts-tmp/pip-cache
if ($LASTEXITCODE -ne 0) { & $taskPython services/tts/build_sox.py; if ($LASTEXITCODE -ne 0) { exit 1 }; & $taskPython -m pip install -r services/tts/requirements.txt --cache-dir .tts-tmp/pip-cache; if ($LASTEXITCODE -ne 0) { exit 1 } }
& $taskPython services/tts/download_weights.py
if ($LASTEXITCODE -ne 0) { exit 1 }
Write-Host '依赖与权重下载已完成；还需实际生成验收，不等于已验证声音相似度。'
