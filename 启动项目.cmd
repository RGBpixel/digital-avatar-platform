@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "TTS_STREAMING=0"
if exist "%~dp0data\fast-tts.enabled" set "TTS_STREAMING=1"
set "NODE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
if not exist "%NODE%" (
  echo 未找到 Codex Node 运行时。请安装 Node.js 24 或修正脚本路径。
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-asr.ps1"
if exist "%~dp0models\Qwen3-TTS-12Hz-0.6B-Base\config.json" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-tts.ps1"
  if errorlevel 1 (
    echo 自定义声音服务启动失败，请查看 data\tts-errors.log。
  ) else (
    set "LOCAL_TTS_URL=http://127.0.0.1:9880/tts"
  )
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-vision.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\open-browser.ps1"
"%NODE%" services\api\server.mjs
pause
