@echo off
setlocal
cd /d "%~dp0"
title Backend attivita - Avvio
set "OFFICINA_FASE=controllo Docker Desktop"
docker info >nul 2>&1
if errorlevel 1 (
  echo Apri Docker Desktop dal menu Start e attendi la scritta Engine running.
  echo Poi apri di nuovo questo file AVVIA.bat.
  pause
  exit /b 1
)
docker container inspect officina-attivita-e32ae57b >nul 2>&1
if not errorlevel 1 goto esistente
echo Preparo il backend. La prima volta servono alcuni secondi.
set "OFFICINA_FASE=costruzione immagine"
docker build --network=none --pull=false -t officina-attivita-e32ae57b:1 .
if errorlevel 1 goto errore
set "OFFICINA_FASE=preparazione rete"
docker network inspect officina-attivita-e32ae57b >nul 2>&1
if not errorlevel 1 goto controlla_rete
docker network create officina-attivita-e32ae57b
if errorlevel 1 goto errore
:controlla_rete
set "OFFICINA_NETWORK_DRIVER="
for /f "delims=" %%d in ('docker network inspect --format={{.Driver}} officina-attivita-e32ae57b 2^>nul') do set "OFFICINA_NETWORK_DRIVER=%%d"
if /i not "%OFFICINA_NETWORK_DRIVER%"=="bridge" goto errore
set "OFFICINA_FASE=creazione container"
docker run -d --pull=never --name officina-attivita-e32ae57b --label officina_delivery=e32ae57b --network officina-attivita-e32ae57b -p 127.0.0.1:8766:8000 --read-only --cap-drop=ALL --security-opt=no-new-privileges --memory=256m --memory-swap=256m --cpus=0.5 --pids-limit=64 --tmpfs /tmp:rw,noexec,nosuid,size=16m -v officina-attivita-e32ae57b-dati:/data officina-attivita-e32ae57b:1
if errorlevel 1 goto errore
goto attendi
:esistente
set "OFFICINA_FASE=controllo container esistente"
set "OFFICINA_CONTAINER_LABEL="
for /f "delims=" %%d in ('docker container inspect --format={{.Config.Labels.officina_delivery}} officina-attivita-e32ae57b 2^>nul') do set "OFFICINA_CONTAINER_LABEL=%%d"
if not "%OFFICINA_CONTAINER_LABEL%"=="e32ae57b" goto errore
set "OFFICINA_FASE=riavvio container"
docker start officina-attivita-e32ae57b >nul
if errorlevel 1 goto errore
:attendi
set "OFFICINA_FASE=attesa risposta delle API sulla porta 8766"
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
echo Fase: %OFFICINA_FASE%
docker container inspect officina-attivita-e32ae57b >nul 2>&1
if not errorlevel 1 docker container logs --tail 20 officina-attivita-e32ae57b
echo Copia il messaggio di errore qui sopra e invialo nella chat.
pause
exit /b 1
