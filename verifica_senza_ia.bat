@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Prima apri installa.bat.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" scripts\verifica_locale.py
pause
