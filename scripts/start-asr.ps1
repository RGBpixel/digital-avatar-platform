$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$taskPython=Join-Path $taskRoot '.venv-tts\Scripts\python.exe'
$taskScript=Join-Path $taskRoot 'services\asr\server.py'
if (!(Test-Path -LiteralPath $taskPython) -or !(Test-Path -LiteralPath (Join-Path $taskRoot 'models\faster-whisper-base\model.bin'))) { Write-Host '本地识别模型未安装，可在设置中改用浏览器识别。'; exit 0 }
try { $health=Invoke-RestMethod 'http://127.0.0.1:9882/health' -TimeoutSec 2; if ($health.engine -in @('faster-whisper-base','faster-whisper-small','sensevoice-small-int8')) { exit 0 } } catch {}
$taskData=Join-Path $taskRoot 'data'
New-Item -ItemType Directory -Path $taskData -Force | Out-Null
$taskProcess=Start-Process -FilePath $taskPython -ArgumentList ('"'+$taskScript+'"') -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskData 'asr.log') -RedirectStandardError (Join-Path $taskData 'asr-errors.log')
Set-Content -LiteralPath (Join-Path $taskData 'asr.pid') -Value $taskProcess.Id
Write-Host '本地中文识别服务已启动，模型加载需要片刻。'
