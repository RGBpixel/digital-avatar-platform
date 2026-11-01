$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
$taskFast=Test-Path -LiteralPath (Join-Path $taskRoot 'data\fast-tts.enabled')
$taskPython = if($taskFast){Join-Path $taskRoot 'experiments\tts-streaming\.venv-fast\Scripts\python.exe'}else{Join-Path $taskRoot '.venv-tts\Scripts\python.exe'}
$taskModelConfig = Join-Path $taskRoot 'models\Qwen3-TTS-12Hz-0.6B-Base\config.json'
if (!(Test-Path -LiteralPath $taskPython) -or !(Test-Path -LiteralPath $taskModelConfig)) { Write-Host '本地声音模型尚未安装完成。请使用普通启动入口；克隆能力不可用。'; exit 1 }
try { $taskHealth = Invoke-RestMethod 'http://127.0.0.1:9880/health' -TimeoutSec 2; if ($taskHealth.ready -and $taskHealth.model -eq 'Qwen3-TTS-12Hz-0.6B-Base' -and (($taskFast -and $taskHealth.engine -eq 'faster-qwen3-tts') -or (!$taskFast -and !$taskHealth.streaming))) { exit 0 } } catch {}
$taskPidFile=Join-Path $taskRoot 'data\tts.pid'
if(Test-Path -LiteralPath $taskPidFile){
 $taskOldPid=Get-Content -LiteralPath $taskPidFile
 $taskOld=Get-CimInstance Win32_Process -Filter "ProcessId=$taskOldPid" -ErrorAction SilentlyContinue
 if($taskOld -and $taskOld.CommandLine -match 'services[\\/]tts[\\/](qwen_server|fast_server)\.py'){Stop-Process -Id $taskOld.ProcessId}
}
$taskData = Join-Path $taskRoot 'data'
New-Item -ItemType Directory -Path $taskData -Force | Out-Null
$taskScript = if($taskFast){Join-Path $taskRoot 'services\tts\fast_server.py'}else{Join-Path $taskRoot 'services\tts\qwen_server.py'}
$taskProcess = Start-Process -FilePath $taskPython -ArgumentList ('"'+$taskScript+'"') -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskData 'tts.log') -RedirectStandardError (Join-Path $taskData 'tts-errors.log')
Set-Content -LiteralPath (Join-Path $taskData 'tts.pid') -Value $taskProcess.Id
Write-Host '正在加载本地声音模型，请稍候。'
for ($taskAttempt=0; $taskAttempt -lt 90; $taskAttempt++) { try { $taskHealth = Invoke-RestMethod 'http://127.0.0.1:9880/health' -TimeoutSec 2; if ($taskHealth.ready) { Write-Host '模型已就绪。'; exit 0 } } catch {}; if ($taskProcess.HasExited) { Write-Host '模型启动失败，详情见 data/tts-errors.log'; exit 1 }; Start-Sleep -Seconds 2 }
Write-Host '模型加载超时，使用普通启动入口，或查看 data/tts-errors.log'; exit 1
