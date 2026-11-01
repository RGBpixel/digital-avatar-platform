@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "MODEL_CONFIG_PATH=%TEMP%\avatar-test-model-%RANDOM%-%RANDOM%.json"
set "PEOPLE_DB_PATH=%TEMP%\avatar-test-people-%RANDOM%-%RANDOM%.sqlite"
"%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" --test tests\reception.test.mjs tests\workspaces.test.mjs tests\voice.test.mjs tests\voice-settings.test.mjs tests\voice-queue.test.mjs tests\pcm-stream.test.mjs tests\chat-stream.test.mjs tests\people.test.mjs tests\personal-conversation.test.mjs tests\endpoint-policy.test.mjs tests\input-devices.test.mjs tests\models.test.mjs tests\guided-reception.test.mjs tests\organization.test.mjs tests\asr.test.mjs
pause
