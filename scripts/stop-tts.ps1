$taskRoot = Split-Path $PSScriptRoot -Parent
$taskPidFile = Join-Path $taskRoot 'data\tts.pid'
if (!(Test-Path -LiteralPath $taskPidFile)) { Write-Host '无本项目声音进程记录'; exit 0 }
$taskTtsPid = [int](Get-Content -LiteralPath $taskPidFile)
$taskProcess = Get-CimInstance Win32_Process -Filter "ProcessId=$taskTtsPid"
$taskExpectedScript = Join-Path $taskRoot 'services\tts\qwen_server.py'
if ($taskProcess -and $taskProcess.Name -eq 'python.exe' -and $taskProcess.CommandLine.Contains($taskExpectedScript)) { Stop-Process -Id $taskTtsPid; Write-Host '已停止本项目声音模型' } else { Write-Host '记录不匹配，未停止任何其他进程' }
