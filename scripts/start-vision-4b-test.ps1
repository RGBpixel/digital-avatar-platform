$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if(Get-NetTCPConnection -LocalPort 9885 -State Listen -ErrorAction SilentlyContinue){Write-Host '4B测试端口已占用';exit 1}
$taskExe=Join-Path $taskRoot 'tools\llama-vision\llama-server.exe'
$taskModel=Join-Path $taskRoot 'models\vision-4b\Qwen3VL-4B-Instruct-Q4_K_M.gguf'
$taskProjector=Join-Path $taskRoot 'models\vision-4b\mmproj-Qwen3VL-4B-Instruct-F16.gguf'
if(!(Test-Path -LiteralPath $taskModel) -or !(Test-Path -LiteralPath $taskProjector)){throw '4B测试文件未下载完成'}
$taskPidFile=Join-Path $taskRoot 'data\vision.pid'
if(Test-Path -LiteralPath $taskPidFile){$taskExistingId=Get-Content -LiteralPath $taskPidFile;$taskExisting=Get-CimInstance Win32_Process -Filter "ProcessId=$taskExistingId" -ErrorAction SilentlyContinue;if($taskExisting.ExecutablePath -eq $taskExe -and $taskExisting.CommandLine -match 'Qwen3.5-2B-Q4_K_M'){Stop-Process -Id $taskExistingId -Force}}
$taskArguments=@('-m',('"'+$taskModel+'"'),'--mmproj',('"'+$taskProjector+'"'),'--host','127.0.0.1','--port','9885','--alias','local-vision','-c','1024','-b','128','-ub','128','--fit','on','--fit-target','1024','--fit-ctx','1024','--no-mmproj-offload','-fa','on','-np','1','--jinja','--no-webui')
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArguments -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskRoot 'data\vision-4b.log') -RedirectStandardError (Join-Path $taskRoot 'data\vision-4b-errors.log')
Set-Content -LiteralPath (Join-Path $taskRoot 'data\vision-4b.pid') -Value $taskProcess.Id
Write-Host '4B隔离测试已启动，临时端口9885；测试后恢复2B。'
