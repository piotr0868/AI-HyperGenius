# Stato progetto — Officina v0.2 (Groq)

Aggiornato il 12 ottobre 2026. Il nuovo obiettivo è usare il piano gratuito Groq,
con quote operative, senza passaggio automatico a servizi a pagamento.

### Aggiornamento Windows del 13 ottobre 2026

Il log dell'utente conferma Python Install Manager e Python 3.12.10 installati,
con firma dell'indice ufficiale verificata. Il registro contiene un runtime
PythonCore\\3.12 preesistente che impedisce la registrazione del nuovo runtime;
il launcher tradizionale usato dall'installer iniziale non lo rilevava.
installa.bat ora preferisce pymanager exec -V:3.12 e distingue il mancato avvio
di Python dagli errori di installazione delle dipendenze. Non modifica il registro
o elimina installazioni esistenti. Questa modifica è revisionata sul codice;
l'esecuzione dell'installer corretto e dell'app sul PC Windows resta da confermare.
Per la copia già scaricata: creare .venv con il manager nella cartella del progetto,
poi riaprire installa.bat. Le precedenti 44 verifiche Linux riguardano il codice
dell'app, rimasto invariato; non convalidano questo script Windows.

### Avvio automatico del 13 ottobre 2026

Un successivo log dell'utente conferma la creazione di .venv tramite pymanager,
l'installazione delle dipendenze e "Installazione completata" sul PC Windows.
Il prompt locale per la chiave Groq è stato raggiunto; non è arrivata conferma
del salvataggio o dell'autenticazione. Nessuna chiave è stata fornita alla chat.

L'utente ha chiesto di automatizzare tutti i passaggi successivi. Aggiunti
scripts/avvio_automatico.py e avvio_automatico.bat: casella mascherata su Windows,
salvataggio locale, controllo API, avvio Docker Desktop e tentativo winget per-user,
immagine a digest con timeout, prova Docker senza IA, generazione e correzione
separate con il modello reale, risultati persistenti e apertura del browser.
Su Windows l'avvio automatico conserva la credenziale in
LOCALAPPDATA/Officina/credentials.env, fuori dal Desktop OneDrive usato dall'utente,
e la carica soltanto nel processo locale. Non copia nuove chiavi nel repository.
Può essere aggiunto alla copia già scaricata senza sovrascrivere .env, .data o
i sorgenti preesistenti. Non gestisce registrazioni o accettazione di contratti,
non aggira autorizzazioni Windows, non forza WSL o riavvii e non esegue codice
generato sull'host. Un fallimento o un'interruzione IA non scatena nuovi tentativi
a ogni avvio. Una prova dichiarata passata richiede ancora i file verificati.

Suite completa rieseguita su Linux: **56 test passati**, zero falliti/skipped.
Dodici controlli nuovi del flusso sono passati con API simulate,
compresi credenziali preservate, annullamento, errori API/Docker, fallimento
essenziale, limiti ai nuovi tentativi, invalidazione di prove perse o modificate e
salvataggio Windows fuori dal progetto (ramo verificato simulando l'OS, non su Windows).
Avviato realmente anche il nuovo flusso dopo annullamento della chiave: richieste
alla pagina italiana e all'API salute passate, credenziale assente dichiarata,
Docker Linux disponibile rilevato. Nessuna chiamata IA. Esito in
resources/evidence/automatic-start.json. Il servizio di prova è stato arrestato.
La casella Windows, winget, Docker Desktop e l'accesso Groq reale restano da provare
sul PC. I risultati in .data/setup/RESULTS.json appartengono alla macchina che li
ha eseguiti: non trasferire esiti Linux come se fossero verifiche Windows.

## Architettura e cambiamenti

FastAPI, SQLite/FTS5, interfaccia italiana HTML/CSS/JavaScript e Docker per eseguire
il codice generato. Groq è il fornitore predefinito: SDK ufficiale 1.7.0,
Chat Completions con tool calling, modello `openai/gpt-oss-20b` indicato nel README
ufficiale. Il prefisso openai è il nome del modello; il servizio è api.groq.com.
OpenAI resta un'opzione esplicita con SDK 3.29.0 e Responses API.

`AI_PROVIDER=groq` usa soltanto `GROQ_API_KEY` e `GROQ_MODEL`.
`AI_PROVIDER=openai` usa soltanto `AI_PROVIDER_KEY` e `AI_MODEL`.
Le chiavi non vengono riutilizzate tra fornitori. Sono nascoste anche nel repr delle
impostazioni. Nessuna credenziale viene inclusa nel container o nella consegna.

Il protocollo interno persistente è conservato: le vecchie cronologie Responses
sono convertite in messaggi Chat Completions, mantenendo chiamate e risultati dei
tool. Le istruzioni restano prioritarie rispetto a documenti e output non fidati.
Gli argomenti dei tool sono validati sull'host oltre ai vincoli del filesystem.

Pausa predefinita di 6 secondi tra le chiamate Groq, contatori persistenti e retry SDK
automatici disabilitati. HTTP 429 ferma il progetto e mostra Retry-After quando
presente. Riprendi non azzera i budget. Le procedure su esempi usano il fornitore scelto.

Restano: obiettivo, piano/criteri prima del codice, Avvia/Pausa/Riprendi/Ferma,
chiarimenti, documenti con fonte/data, ricerca FTS5, procedure versionate e adottabili
solo dopo test su esempi, snapshots ripristinabili, registro e ZIP del solo progetto.
Pronto richiede unittest non vuoti, contratto indipendente e hash dei file invariato.
Docker non ha rete, segreti, cartelle host o socket Docker; niente ripiego sull'host.

## Verifiche effettive

Su Linux, Python 3.12.14, Docker 28.4.0 e Chromium di sistema:

- **44 test passati**, 0 errori/fallimenti/skipped.
- SDK ufficiali Groq e OpenAI con trasporto HTTP simulato e Docker reale: scrittura,
  difetto rilevato, correzione predisposta dal test e nuova verifica passata.
- Quota Groq, credenziali separate, migrazione cronologie, argomenti non fidati,
  prova/adozione procedure e configurazione locale della chiave (valore fittizio).
- Backend di riferimento: 8 unittest e 5 verifiche indipendenti, inclusi idempotenza
  e riavvio; difetto deliberato respinto e ripristino deterministico verificato.
- Browser: italiano, Groq selezionato, credenziale assente -> intervento,
  recupero, documenti persistenti e layout 390px, nessun errore JavaScript.
- Riavvio reale del servizio con configurazione Groq e progetti preservati.
- Setup uv congelato ripetuto e pip separato con verifica degli hash, SDK Groq incluso.

Vedi RISULTATI_VERIFICHE.md, VERIFICHE.json e resources/evidence.
Il backend di riferimento è scritto per la consegna, non attribuito al modello.
Le risposte simulate esistono solo nei test: non convalidano capacità di un'IA reale.

## Requisiti esterni ancora mancanti

`GROQ_API_KEY` assente. scripts/controlla_ia.py e scripts/prova_agente.py hanno
restituito exit 2, NON ESEGUITI: zero chiamate live. Autenticazione, disponibilità
per l'account del modello, generazione/correzione autonome e procedure con il modello
reale restano da verificare. La creazione dell'account e della chiave spetta all'utente.

Il piano Free e le quote non sono rilevabili affidabilmente dall'app. L'utente deve
controllarli nella console Groq; non è garantito accesso illimitato o assenza di
addebiti se l'account ha già fatturazione attiva. Nessun cambio automatico a OpenAI.

Windows 11, Docker Desktop/WSL 2 e i .bat sono predisposti ma non eseguiti su Windows.
Pubblicazione dell'ambiente e ripristino in un nuovo task cloud non verificati.
Questa versione supporta il contratto backend attività Python con libreria standard;
altri backend e blockchain sono traguardi successivi. Nessuna gestione di denaro,
portafogli, pubblicazione automatica o uso di repository/test Nodveta.

## Ripresa

1. Usa il checkout esistente /workspace/AI-HyperGenius: ogni task è già isolato.
   Non creare un worktree salvo richiesta esplicita; preserva .env e .data.
2. `uv sync --frozen`, poi prepara l'immagine con scripts/prepara_isolamento.py.
3. Avvia `.venv/bin/python avvia.py --no-browser`; verifica / e /api/health tramite
   richieste locali, separando disponibilità del servizio, chiave e Docker.
4. L'utente crea la chiave nel proprio account Free su https://console.groq.com/keys.
   Su Windows: configura_ia.bat (input nascosto). Nel cloud: impostazioni sicure
   dell'ambiente per GROQ_API_KEY, mai valori in chat. Riavvia dopo la configurazione.
5. `scripts/controlla_ia.py` verifica accesso/modello; `scripts/prova_agente.py`
   verifica generazione e correzione nella copia separata. Conserva gli esiti
   negativi e aggiorna questo file con risultati effettivi.

## Git e configurazione cloud

Repository: https://github.com/piotr0868/AI-HyperGenius, branch main.
Ogni invio viene verificato confrontando HEAD con git ls-remote origin refs/heads/main.
La consegna esclude .env, .data, .venv e .git; Git esclude credenziali e dati locali.

Bozza cloud aggiornata e confermata: istruzioni d'avvio, requisito personale
GROQ_API_KEY per api.groq.com, variabili AI_PROVIDER/GROQ_MODEL e dominio console.groq.com.
Installazione congelata conservata; opzione OpenAI precedente preservata.
Salvare la bozza non applica né pubblica: revisionare/salvare nelle impostazioni,
poi pubblicare se desiderato. La prova live Groq resta bloccata dalla chiave mancante.
