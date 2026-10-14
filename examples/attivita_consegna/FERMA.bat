@echo off
setlocal
title Backend attivita - Arresto
docker inspect --format "{{.Config.Labels.officina_delivery}}" officina-attivita-e32ae57b | findstr /x "e32ae57b" >nul
if errorlevel 1 (
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
