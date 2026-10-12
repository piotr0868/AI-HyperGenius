@echo off
setlocal
cd /d "%~dp0"
echo Preparazione di Officina. Serve Python 3.12 per Windows.
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 goto errore
)
".venv\Scripts\python.exe" -m pip install --require-hashes -r requirements.lock
if errorlevel 1 goto errore
if not exist .env copy .env.example .env >nul
echo Installazione completata. Configura .env e poi apri avvia.bat.
pause
exit /b 0
:errore
echo Installazione non completata. Installa Python 3.12 da python.org e riprova.
echo Nessuna verifica TLS o checksum e' stata disabilitata.
pause
exit /b 1
