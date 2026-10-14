# Correggere il collegamento principale di Officina sul PC

L'utente ha segnalato che il doppio clic apre una pagina vuota. Il launcher
AVVIA_PROGETTO_VERIFICATO.bat creato dalla sessione locale apre sulla porta 8767
il backend API verificato: `/activities` mostra `[]` se non ci sono attivita'.
L'utente vuole aprire l'assistente italiano, gia' visto sulla porta 8765.
Lavorare autonomamente nella cartella Officina gia' autorizzata, conservando
dati, credenziali, file e modifiche locali. Non leggere chiavi con strumenti IA.

## Applicazione minima

1. Dalla stessa revisione GitHub fissata indicata nell'incarico, leggere
   `resources/avvio_officina_manifest.json`. Scaricare **soltanto** i due file
   elencati: `APRI_OFFICINA.bat` e `scripts/apri_officina.py`. Usare HTTPS e
   verificare i SHA256 del manifest prima di installarli. Se un file locale
   omonimo differisce, salvarlo prima in una nuova cartella `.data/updates/`.
   Non sostituire .env, .data, STATO_PROGETTO.md o altri sorgenti locali con copie
   del repository. Il nome della cartella puo' provenire da uno ZIP senza .git.
2. APRI_OFFICINA.bat usa la .venv esistente e apre l'assistente. Se e' gia'
   attivo, riconosce la pagina HTML con i veri controlli goal-form/new-project
   e la riapre senza creare un altro server. Se una porta e' occupata da un'altra
   applicazione, si ferma senza arrestarla. All'avvio da zero carica la chiave
   locale con lo script esistente, prepara Docker e apre la pagina soltanto
   dopo la risposta HTML. Non riesegue accettazioni o generazioni IA.
3. Creare sul Desktop un collegamento chiamato **Apri Officina** che punti a
   APRI_OFFICINA.bat nella cartella del progetto, con directory di lavoro uguale
   alla cartella progetto. Ricavare il Desktop dal percorso noto di Windows,
   non enumerare cartelle personali. Se un collegamento omonimo gia' presente
   differisce, conservarne una copia prima di aggiornarlo.
4. Aprire il collegamento e verificare su Windows che la destinazione sia la
   radice di Officina (normalmente http://127.0.0.1:8765), con HTML, casella
   "Descrivi cosa vuoi ottenere" e pulsante "+ Nuovo obiettivo". Non usare
   /activities, 8766 o 8767 come interfaccia principale. Riaprire una seconda
   volta per controllare il riuso del server senza duplicazioni. Se il browser
   non e' ispezionabile, distinguere la verifica HTTP/HTML dall'osservazione
   visiva; non dichiarare quest'ultima eseguita.
5. Conservare le istanze backend sulle porte 8766/8767 e i loro dati. Il vecchio
   launcher del progetto rimane un avvio tecnico delle API. Non creare nuovi
   obiettivi o richieste Groq, non azzerare/aumentare contatori e non ripetere
   le prove IA gia' passate. Non disattivare sandbox, TLS o verifiche; usare
   l'esecuzione autorizzata supportata se i permessi Windows lo richiedono.
6. Aggiornare lo STATO_PROGETTO.md locale con i risultati effettivi. Alla fine
   indicare all'utente soltanto il nome del collegamento da aprire: **Apri
   Officina**. Chiedere un suo clic soltanto per un requisito realmente mancante,
   con il nome preciso della finestra e del pulsante.

## Prove effettuate sul cloud

Sei verifiche mirate passate su Linux: avvio dell'app FastAPI con HTTP reale,
attesa della pagina HTML prima dell'apertura del browser, due aperture della
stessa istanza senza toccare memoria/credenziali, rifiuto di JSON [] o di un altro
sito su porta occupata, rifiuto dei reindirizzamenti e gestione del browser non
disponibile. Nessun modello chiamato, nessun codice generato eseguito sull'host.
Report: resources/evidence/open-officina.xml. Il batch Windows resta da provare
effettivamente con questa sessione locale; non attribuirgli le prove Linux.
