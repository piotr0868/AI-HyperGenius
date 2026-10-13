@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  call installa.bat
  if errorlevel 1 goto errore
)
".venv\Scripts\python.exe" scripts\avvio_automatico.py
if errorlevel 1 goto errore
exit /b 0
:errore
echo Avvio non completato. Leggi il messaggio sopra: file e memoria sono conservati.
pause
exit /b 1
