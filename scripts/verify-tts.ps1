$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $taskRoot
$taskData = Join-Path $taskRoot 'data'
New-Item -ItemType Directory -Path $taskData -Force | Out-Null
$taskPython = Join-Path $taskRoot '.venv-tts\Scripts\python.exe'
$taskScript = Join-Path $taskRoot 'services\tts\qwen_server.py'
$taskModelProcess = Start-Process -FilePath $taskPython -ArgumentList ('-X utf8 -u "'+$taskScript+'"') -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskData 'tts-verify.log') -RedirectStandardError (Join-Path $taskData 'tts-verify-errors.log')
try {
    Write-Host '正在加载 CPU 模型，随后用官方公开参考样音验证新文字生成。'
    $taskReady = $false
    for ($taskAttempt=0; $taskAttempt -lt 120; $taskAttempt++) {
        try { $taskHealth = Invoke-RestMethod 'http://127.0.0.1:9880/health' -TimeoutSec 2; if ($taskHealth.ready) { $taskReady = $true; break } } catch {}
        if ($taskModelProcess.HasExited) { Get-Content -LiteralPath (Join-Path $taskData 'tts-verify-errors.log') -Tail 40; throw '本地模型启动失败' }
        Start-Sleep -Seconds 2
    }
    if (!$taskReady) { Get-Content -LiteralPath (Join-Path $taskData 'tts-verify-errors.log') -Tail 40; throw '本地模型加载超时' }
    Write-Host '模型就绪，正在生成验证音频。'
    & $taskPython -X utf8 services/tts/smoke_model.py
    if ($LASTEXITCODE -ne 0) { throw '实际音频生成验证未通过' }
    $env:LOCAL_TTS_URL = 'http://127.0.0.1:9880/tts'
    $env:PORT = '3214'
    $taskNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
    $taskAPIScript = Join-Path $taskRoot 'services\api\server.mjs'
    $taskAPIProcess = Start-Process -FilePath $taskNode -ArgumentList ('"'+$taskAPIScript+'"') -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskData 'api-voice-verify.log') -RedirectStandardError (Join-Path $taskData 'api-voice-verify-errors.log')
    try {
        for ($taskPoll=0; $taskPoll -lt 30; $taskPoll++) { try { $taskAPIHealth = Invoke-RestMethod 'http://127.0.0.1:3214/api/health' -TimeoutSec 2; if ($taskAPIHealth.ok) { break } } catch {}; Start-Sleep -Seconds 1 }
        & $taskNode services/tts/smoke_platform.mjs
        if ($LASTEXITCODE -ne 0) { throw '平台真实TTS链路未通过' }
    } finally { if (!$taskAPIProcess.HasExited) { Stop-Process -Id $taskAPIProcess.Id } }

} finally { if (!$taskModelProcess.HasExited) { Stop-Process -Id $taskModelProcess.Id }; Write-Host '本轮验证模型进程已停止。' }
