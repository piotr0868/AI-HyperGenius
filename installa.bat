@echo off
setlocal
cd /d "%~dp0"
echo Preparazione di Officina. Serve Python 3.12 per Windows.
if not exist ".venv\Scripts\python.exe" (
  where pymanager >nul 2>&1
  if not errorlevel 1 (
    pymanager exec -V:3.12 -m venv .venv
  ) else (
    py -3.12 -m venv .venv
  )
  if errorlevel 1 goto runtime_mancante
)
".venv\Scripts\python.exe" -m pip install --require-hashes -r requirements.lock
if errorlevel 1 goto errore
if not exist .env copy .env.example .env >nul
echo Installazione completata. Configura .env e poi apri avvia.bat.
pause
exit /b 0
:errore
echo Installazione non completata. Conserva il messaggio di errore mostrato sopra.
echo Nessuna verifica TLS o checksum e' stata disabilitata.
pause
exit /b 1
:runtime_mancante
echo Python 3.12 non avviabile. Con Python Install Manager usa: pymanager install 3.12
echo La finestra resta aperta per leggere il risultato. Nessuna modifica al registro.
pause
exit /b 1
