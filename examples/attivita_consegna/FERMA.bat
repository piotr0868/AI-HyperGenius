@echo off
setlocal
title Backend attivita - Arresto
set "OFFICINA_CONTAINER_LABEL="
for /f "delims=" %%d in ('docker container inspect --format={{.Config.Labels.officina_delivery}} officina-attivita-e32ae57b 2^>nul') do set "OFFICINA_CONTAINER_LABEL=%%d"
if not "%OFFICINA_CONTAINER_LABEL%"=="e32ae57b" (
  echo Il container di questo progetto non e disponibile. Nessun altro programma fermato.
  pause
  exit /b 1
)
docker stop --time 5 officina-attivita-e32ae57b
if errorlevel 1 (
  echo Arresto non completato. Leggi il messaggio qui sopra.
  pause
  exit /b 1
)
echo Backend fermato. I dati sono conservati.
pause
