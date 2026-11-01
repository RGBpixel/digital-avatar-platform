@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start-tts.ps1
if errorlevel 1 (
  pause
  exit /b 1
)
set "LOCAL_TTS_URL=http://127.0.0.1:9880/tts"
call 启动项目.cmd
