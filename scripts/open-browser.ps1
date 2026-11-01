$taskNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
# 使用隐藏助手等待后台健康检查，避免浏览器先于服务打开。
Start-Process -FilePath $taskNode -ArgumentList ('"'+(Join-Path $PSScriptRoot 'open-browser.mjs')+'"') -WindowStyle Hidden
