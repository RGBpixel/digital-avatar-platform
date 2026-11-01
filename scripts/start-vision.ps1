$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
try { $taskHealth=Invoke-RestMethod 'http://127.0.0.1:9884/health' -TimeoutSec 2; if($taskHealth.status -eq 'ok'){Write-Host '本机视觉服务已就绪';exit 0} } catch {}
$taskExe=Join-Path $taskRoot 'tools\llama-vision\llama-server.exe'
$taskModel=Join-Path $taskRoot 'models\vision\Qwen3.5-2B-Q4_K_M.gguf'
$taskProjector=Join-Path $taskRoot 'models\vision\mmproj-F16.gguf'
if(!(Test-Path -LiteralPath $taskModel) -or !(Test-Path -LiteralPath $taskProjector) -or !(Test-Path -LiteralPath $taskExe)){Write-Host '视觉文件尚未安装完成，其他功能可继续使用。';exit 1}
$taskListener=Get-NetTCPConnection -LocalPort 9884 -State Listen -ErrorAction SilentlyContinue
if($taskListener){Write-Host '9884端口已被占用，未启动重复视觉进程，请查看视觉服务状态。';exit 1}
$taskArguments=@('-m',('"'+$taskModel+'"'),'--mmproj',('"'+$taskProjector+'"'),'--host','127.0.0.1','--port','9884','--alias','local-vision','-c','1024','-b','128','-ub','128','-ngl','99','--no-mmproj-offload','-fa','on','-np','1','--jinja','--no-webui')
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList $taskArguments -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskRoot 'data\vision.log') -RedirectStandardError (Join-Path $taskRoot 'data\vision-errors.log')
Set-Content -LiteralPath (Join-Path $taskRoot 'data\vision.pid') -Value $taskProcess.Id
Write-Host '本机视觉模型正在加载，可在摄像头页面查看状态。'
