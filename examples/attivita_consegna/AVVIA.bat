@echo off
setlocal
cd /d "%~dp0"
title Backend attivita - Avvio
docker info >nul 2>&1
if errorlevel 1 (
  echo Apri Docker Desktop dal menu Start e attendi la scritta Engine running.
  echo Poi apri di nuovo questo file AVVIA.bat.
  pause
  exit /b 1
)
docker inspect officina-attivita-e32ae57b >nul 2>&1
if not errorlevel 1 goto esistente
echo Preparo il backend. La prima volta servono alcuni secondi.
docker build --network=none --pull=false -t officina-attivita-e32ae57b:1 .
if errorlevel 1 goto errore
docker network inspect officina-attivita-e32ae57b >nul 2>&1
if errorlevel 1 docker network create officina-attivita-e32ae57b
if errorlevel 1 goto errore
docker network inspect --format "{{.Driver}}" officina-attivita-e32ae57b | findstr /x "bridge" >nul
if errorlevel 1 goto errore
docker run -d --name officina-attivita-e32ae57b --label officina_delivery=e32ae57b --network officina-attivita-e32ae57b -p 127.0.0.1:8766:8000 --read-only --cap-drop=ALL --security-opt=no-new-privileges --memory=256m --memory-swap=256m --cpus=0.5 --pids-limit=64 --tmpfs /tmp:rw,noexec,nosuid,size=16m -v officina-attivita-e32ae57b-dati:/data officina-attivita-e32ae57b:1
if errorlevel 1 goto errore
goto attendi
:esistente
docker inspect --format "{{.Config.Labels.officina_delivery}}" officina-attivita-e32ae57b | findstr /x "e32ae57b" >nul
if errorlevel 1 goto errore
docker start officina-attivita-e32ae57b >nul
if errorlevel 1 goto errore
:attendi
for /l %%n in (1,1,15) do (
  curl.exe --silent --fail --max-time 1 http://127.0.0.1:8766/activities >nul 2>&1
  if not errorlevel 1 goto pronto
  timeout /t 1 /nobreak >nul
)
goto errore
:pronto
start "" "http://127.0.0.1:8766/"
echo Backend avviato. Puoi chiudere questa finestra.
echo Per fermare il backend apri FERMA.bat. I dati rimangono salvati.
pause
exit /b 0
:errore
echo Avvio non completato. Non cancellare cartelle o volumi Docker.
echo Copia il messaggio di errore qui sopra e invialo nella chat.
pause
exit /b 1
