# Officina — assistente personale, v0.2

Interfaccia italiana nel browser, memoria SQLite e agente di programmazione integrato
con l’SDK ufficiale Groq, scelta predefinita per usare un account Free. OpenAI resta
un’opzione esplicita, con credenziale separata. Questa prima versione si concentra su
un piccolo backend attività in Python: è il traguardo verificabile da cui partire,
prima di estendere l’assistente ad altri backend e alle infrastrutture blockchain.

L’applicazione si avvia anche senza credenziale, ma non inventa risposte IA: mostra
**Serve il tuo intervento**. Le prove con un vero modello richiedono una chiave API.
Le quote gratuite non sono illimitate: controlla il piano e i limiti nella console Groq.
L’app non attiva la fatturazione e non passa automaticamente a un altro fornitore.

## Codice su GitHub

Il repository di destinazione è <https://github.com/piotr0868/AI-HyperGenius>,
branch `main`. GitHub conserva codice e cronologia; non sostituisce il computer,
Docker o le API IA necessari per eseguirlo. Per scaricarlo con Git:

```text
git clone https://github.com/piotr0868/AI-HyperGenius.git
```

Poi apri `installa.bat` nella cartella `AI-HyperGenius` e segui i passaggi sotto.
Credenziali, memoria locale e dipendenze installate sono escluse dal repository.

## Avvio su Windows 11

Per una copia con le dipendenze già installate, apri **avvio_automatico.bat**.
Se manca la credenziale compare una casella locale mascherata: incolla la chiave
e premi **Salva e continua**. Il programma controlla l'accesso API e il modello,
avvia Docker Desktop (o tenta l'installazione per il solo utente tramite winget),
prepara l'immagine con digest e timeout, esegue le prove senza IA e poi la prova
con il modello reale. Infine apre l'app nel browser. Lascia aperta la finestra di avvio.
Su Windows questo avvio conserva la chiave in
`%LOCALAPPDATA%\Officina\credentials.env`, con permessi del tuo account, fuori dalla
cartella del progetto e da Desktop/Documenti sincronizzati con OneDrive. Per
riutilizzarla avvia sempre **avvio_automatico.bat**; il percorso manuale descritto
sotto usa invece il file `.env` del progetto.

Windows può richiedere intervento per Docker, WSL 2, condizioni del fornitore o
autorizzazioni di sistema. Questi requisiti non vengono aggirati; se Docker Linux
non è pronto, il codice generato non viene eseguito. Il log dell'utente conferma
casella grafica, chiave salvata, accesso Groq, Docker Linux, aggiornamento Docker
tramite winget, immagine a digest e prova senza IA riusciti sul suo PC. La
generazione con il modello è stata tentata: primo arresto HTTP 429, secondo HTTP
400 dopo la ripresa; **NON COMPLETATA**. La correzione del rifiuto è verificata
con SDK e HTTP simulato su Linux, ancora da provare con il modello reale sul PC.

I risultati effettivi sono in `.data/setup/RESULTS.json` e
`.data/live-acceptance/RESULTS.json`. La prova IA usa i limiti configurati e può
esaurire una quota Free. Non viene ripetuta automaticamente a ogni apertura dopo
fallimento o interruzione. Una prova passata viene riutilizzata solo se fonti,
configurazione del modello/immagine ed evidenze dei progetti verificati sono ancora
validi. Per un nuovo tentativo esplicito:
`.venv\Scripts\python.exe scripts\avvio_automatico.py --riprova-verifica`. I risultati negativi precedenti
restano nel registro dei progetti di accettazione; nessun cambio a un provider a pagamento.

Per usare il percorso manuale:

Procedi un passo alla volta. Estrai il pacchetto in una cartella del tuo profilo
personale, per esempio `Documenti\Officina`.

1. Installa **Python Install Manager** ufficiale da
   <https://apps.microsoft.com/detail/9NQ7512CXL7T> e il runtime **Python 3.12**.
   Dal Prompt dei comandi: `pymanager install 3.12`.
2. Apri **installa.bat**. Installa le dipendenze bloccate con verifica degli hash.
3. Apri **avvia.bat**. Il browser si apre automaticamente e puoi vedere interfaccia,
   documenti e progetti salvati. La chiusura del browser non ferma l’app: usa Ctrl+C
   nella finestra di avvio per chiuderla.

L'installer preferisce `pymanager exec -V:3.12` per evitare conflitti con vecchi
launcher o registrazioni Python preesistenti. Mantiene il launcher tradizionale
come alternativa se il manager manca. Non elimina runtime o voci del registro.
Se usi una copia precedente di Officina, dalla cartella che contiene `installa.bat`
puoi creare l'ambiente con `pymanager exec -V:3.12 -m venv .venv`, poi riaprire
`installa.bat`: le dipendenze vengono installate con gli hash del lockfile.

Per attivare il lavoro autonomo dell’agente:

1. Installa **Docker Desktop** da <https://docs.docker.com/desktop/setup/install/windows-install/>.
   Avvialo con il motore WSL 2 e i container Linux.
2. Apri **prepara_isolamento.bat**. Scarica l’immagine Python, conserva il digest
   verificato da Docker e prepara l’esecuzione isolata.
3. Apri **configura_ia.bat**. Lo script apre la pagina delle chiavi Groq. Crea un account Free e inserisci
   la tua chiave API nella finestra locale con input
   nascosto; il valore viene salvato soltanto in `.env`, escluso da Git e dal pacchetto.
   In alternativa copia `.env.example` in `.env` e imposta `AI_PROVIDER=groq` e `GROQ_API_KEY` manualmente.
4. Riavvia **avvia.bat**, descrivi il risultato e premi **Avvia**. Se avevi iniziato un
   progetto senza credenziale, selezionalo e premi **Riprendi**.

Il log condiviso dall'utente conferma su Windows Python 3.12.10, creazione di `.venv`
e installazione delle dipendenze con `installa.bat`, poi salvataggio della chiave,
accesso/modello Groq, Docker e prove senza IA. Il server dell'applicazione è partito.
Il log finale del **14 ottobre 2026** conferma **ACCETTAZIONE IA: PASSATA** e
**Verifica agente: PASSATA**, inclusa correzione del difetto nella copia separata
con il modello reale. La correzione precedente della porta e la certificazione
conclusiva sono interventi del sistema esplicitamente registrati. La ripresa
finale ha conservato le 20 richieste già usate senza altre generazioni.
Le verifiche eseguite direttamente dall'assistente restano su Linux: 129 passate.

## Cosa puoi provare subito senza chiave

Con Docker preparato, apri **verifica_senza_ia.bat**. Controlla il backend di riferimento,
introduce un errore in una copia in memoria, rileva il fallimento e verifica il ripristino.
L’originale non viene modificato. Il ripristino è deterministico, non una correzione IA.

Il riferimento in `examples/activity_backend` è stato scritto per questa consegna;
non è presentato come codice generato dal modello. Usa SQLite, HTTP e unittest della
libreria standard. Il contratto indipendente verifica:

- Creazione e consultazione tramite `POST /activities` e `GET /activities`.
- `title`: stringa non vuota dopo la rimozione degli spazi ai bordi, massimo 200 caratteri.
- `Idempotency-Key`: ripetizione senza duplicati; stessa chiave con dati diversi restituisce 409.
- Conservazione delle attività **e della chiave di idempotenza** dopo il riavvio del processo.
- Test del progetto non vuoti, senza skip o expectedFailure.

Per verificare la generazione e correzione con Groq reale, dopo la configurazione:

```powershell
.venv\Scripts\python.exe scripts\prova_agente.py
```

Lo script chiede all’agente di costruire il backend da zero e verificarlo. Poi crea
un **secondo progetto**, copia il risultato e introduce un difetto in
`regression_target.py`. Richiede che l’agente riproduca il fallimento prima di correggere,
ripeta le prove e conservi il progetto originale. I risultati vengono salvati in
`.data/live-acceptance/RESULTS.json`. L’assenza della chiave produce exit code 2,
**NON ESEGUITA**, senza simulazioni o addebiti API. Un risultato fallito produce exit code 1.
Una nuova esecuzione riprende i progetti e i contatori precedenti; non reintroduce
un difetto già corretto. `RUN.json` registra gli identificativi anche prima delle
chiamate al modello. Gli esiti precedenti restano in `runs/`. I progetti già pronti
vengono ricontrollati in Docker. Per una prova separata esplicita: `--nuova-prova`.

Per aggiornare una copia precedente dopo un errore di quota, il helper
`scripts/aggiorna_quota.py REVISIONE_GITHUB` scarica soltanto quattro sorgenti
predefiniti, verifica SHA-256 e sintassi prima di modificarli, conserva copie in
`.data/updates/`, applica il profilo Groq e riprende la prova. Non sostituisce `.data`
o credenziali. `--aggiorna-docker` tenta l'aggiornamento ufficiale con winget e
interrompe l'avvio IA se il gestore non lo completa. Nessuna verifica TLS/firma/checksum
o autorizzazione Windows viene aggirata.
Se il terminale precedente non è visibile, `--ferma-pid PID_DAL_LOG` consente un
arresto controllato della sola istanza identificata: verifica processo/porta e
proprietario, chiude eventuali lavori con l'API Ferma e controlla di nuovo prima
di arrestare il processo. Questo passaggio Windows non è ancora stato eseguito
dall'assistente; un'identità non riconosciuta interrompe l'aggiornamento.

## Controllo della chiave e compatibilità

Dopo aver configurato Groq, puoi verificare accesso e disponibilità del modello
senza avviare una generazione:

```powershell
.venv\Scripts\python.exe scripts\controlla_ia.py
```

Questo controllo non certifica il piano gratuito o le capacità dell’agente. La prova
completa resta `scripts/prova_agente.py`. Crea l’account e la chiave personalmente:
l’app non gestisce registrazioni, accettazione di condizioni o dati di fatturazione.

Le installazioni precedenti conservano `.env` e `.data`: aggiorna il codice con
`git pull`, esegui `installa.bat`, poi `configura_ia.bat` e riavvia. Le vecchie
cronologie Responses vengono convertite nel formato Chat Completions senza perdere
le chiamate agli strumenti e i risultati salvati.

Per scegliere esplicitamente l’opzione OpenAI: `AI_PROVIDER=openai`,
`AI_PROVIDER_KEY` e `AI_MODEL` in `.env`, oppure esegui
`python scripts/configura_ia.py --openai`. Richiede API OpenAI a pagamento, separate
da ChatGPT; la chiave Groq non viene inviata a OpenAI e viceversa.

## Interfaccia e memoria

L’obiettivo è l’unica decisione iniziale. Piano, risultato atteso, criteri, file,
correzioni, utilizzo e prove restano nella cartella `.data`. Dopo un’interruzione,
**Riprendi** riutilizza i file e la conversazione salvati e richiede nuove prove quando
necessario. **Pausa** sospende tra operazioni: una chiamata API già inviata può concludersi.
**Ferma** annulla il processo locale e rimuove il container avviato; non può annullare
un addebito del provider già avvenuto.

**Pronto** è consentito soltanto con test riusciti e contratto indipendente passato sui
file correnti. Le modifiche successive invalidano le prove. Dai dettagli puoi
ripristinare una versione precedente e scaricare un ZIP del progetto con i risultati.
L’esportazione non comprende `.env`, credenziali o memoria di altri progetti.

Puoi aggiungere file `.md` e `.txt`, testi e trascrizioni con fonte e data. SQLite FTS5
recupera estratti pertinenti, fino a quattro fonti diverse. Sono già incluse copie
datate della documentazione ufficiale Python e dei README degli SDK Groq/OpenAI, consultate
durante lo sviluppo. Il tool di consultazione HTTPS può aggiornare le fonti consentite.
Documenti, tutorial, repository e output restano **dati non fidati**, subordinati alle
regole e ai limiti dell’agente.

Una correzione può diventare una procedura. Le modifiche creano nuove versioni. Una
versione diventa adottabile soltanto dopo una prova con il modello su esempi e termini
attesi definiti dall’utente. È una verifica limitata del piano prodotto: non certifica
da sola il software. Puoi modificare o disattivare ogni procedura. Non viene riaddestrato
alcun modello.

## Limiti operativi

`.env.example` descrive i limiti: chiamate IA, operazioni, correzioni, token, tempo
complessivo e timeout di ogni comando. I contatori sono persistenti per progetto:
premere Riprendi non azzera il budget. Per modificare i limiti, cambia `.env` e riavvia.
Il fornitore predefinito è `groq` e il modello è `openai/gpt-oss-20b`, indicato
nel README ufficiale dell’SDK Groq 1.7.0 consultato il 12 ottobre 2026. Il prefisso
`openai/` è parte del nome del modello ospitato da Groq: con questa configurazione
le richieste vanno soltanto a `api.groq.com`, senza richiedere un account OpenAI.
Disponibilità del modello, quota e piano Free vanno verificati sul tuo account.
`GROQ_MODEL` seleziona il modello; `AI_MIN_INTERVAL_SECONDS` imposta una pausa tra
richieste, **60 secondi** per il profilo Groq. Le copie precedenti con valore 6
devono essere aggiornate esplicitamente. Il profilo riduce `MAX_OUTPUT_TOKENS` a
3000 preservando limiti inferiori scelti dall'utente. Per GPT-OSS usa il livello
`reasoning_effort=low`, supportato dall'SDK ufficiale 1.7.0. Le scritture riuscite
non ripetono tutto il codice nelle richieste successive; gli estratti di documenti
e log sono ridotti, con fonti/date ed errori conservati. La memoria originale resta intatta.

Con HTTP 429 e `Retry-After` fino a 120 secondi, l'agente può aspettare e riprendere
automaticamente, al massimo `MAX_RATE_LIMIT_RETRIES=2` volte per progetto. Ogni
richiesta conta comunque in `MAX_MODEL_CALLS`; attese e tentativi restano persistenti
e non si azzerano con Riprendi. Quota lunga, attesa non comunicata o budget esaurito
producono **Serve il tuo intervento**. I limiti effettivi del tuo account possono
ancora impedire la prova; il profilo non li aumenta.

Il registro conserva token effettivi quando il provider li restituisce. Il costo è
una **stima** soltanto se imposti entrambi i prezzi per milione di token. Il limite
facoltativo `MAX_ESTIMATED_COST_USD` prenota prudentemente il costo prima di chiamare
l’API. Prezzi, cache e fatturazione effettiva dipendono dal provider: configura anche
il budget nell’account del fornitore. Mantieni il piano Free di Groq per evitare addebiti. Un errore di rete può impedire di conoscere l’utilizzo
di una chiamata già ricevuta dal provider.

Il backend dell’assistente ascolta solo su loopback. Le modifiche API richiedono un
token di sessione e un’origine locale; non è un servizio pubblico. La chiave rimane
nel processo locale dell’assistente. Obiettivi, documenti pertinenti, codice e risultati
dei tool sono trasmessi al fornitore scelto per il lavoro: non inserire dati che non vuoi inviare.

Il codice generato usa container temporanei senza rete, bind mount, segreti o socket
Docker, con utente non privilegiato, filesystem di sistema in sola lettura, capacità
rimosse e limiti a memoria, CPU, processi, output e tempo. Se Docker o l’immagine fissata
non sono disponibili, l’esecuzione autonoma è **disabilitata**. Nessun ripiego esegue
il codice generato sull’host. Docker è isolamento pratico, non una garanzia contro
qualsiasi vulnerabilità del kernel: mantienilo aggiornato.

Non sono implementati gestione di denaro, portafogli, chiavi blockchain, invio ai
clienti, pubblicazione automatica o accesso a repository/test Nodveta. L’accesso a
Internet del tool documentazione è limitato alle fonti ufficiali indicate nel codice.

## Sviluppo su Linux

L’ambiente cloud dispone di Python 3.12, uv e Docker. Nel checkout esistente:

```bash
UV_CACHE_DIR=/workspace/shared/uv-cache uv sync --frozen
.venv/bin/python scripts/prepara_isolamento.py
.venv/bin/python avvia.py --no-browser
```

In un altro terminale:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/verifica_locale.py
.venv/bin/python scripts/verifica_browser.py
```

Il test browser richiede Chromium di sistema o il browser installato da Playwright;
le sue dipendenze sono nel gruppo dev. Le prove Docker, se il servizio manca, risultano
**skipped**: non costituiscono una conferma dell’isolamento. I test con trasporto SDK
simulato sono identificati come offline e non convalidano un modello IA reale.

Usa il checkout già presente: ogni task cloud è già isolato; non creare un worktree
aggiuntivo salvo richiesta esplicita. Consulta `STATO_PROGETTO.md` per riprendere.

### Riprendere la prova con un limite complessivo esplicito

Dalla cartella del progetto,
`.venv\Scripts\python.exe scripts\avvio_automatico.py --riprova-verifica --chiamate-prova 20`
riprende la prova
con massimo 20 richieste IA complessive tra generazione e correzione. Le richieste
già consumate nelle due fasi rimangono contate. Questa opzione non cambia `.env`,
i limiti dell'app o i budget di token/tempo. Il rapporto include i limiti effettivi
e le categorie sicure degli eventuali errori del provider. Un errore 400 di formato
riconosciuto può essere rigenerato una volta per progetto entro questi limiti;
gli altri rifiuti fermano il lavoro. Una prova interrotta non certifica l'agente.

La riserva dei token usa i byte della richiesta costruita per il fornitore, con
un margine prudente; non è un tokenizer ufficiale. La cronologia originale resta
in memoria e il consumo riportato viene sempre sommato alla riserva. Un limite
raggiunto ferma l'agente prima dell'API: leggere `last_token_budget` nel rapporto
prima di decidere se cambiare un limite. L'app non aumenta il budget da sola.
Per comandi Windows lunghi: Windows+R → `cmd` → Invio, poi incollare il comando
nel Prompt; non incollare l'intero comando lungo nella finestra Esegui.

La prova ripresa ricontrolla i file già salvati in Docker prima di usare un'altra
risposta del modello, se piano, criteri e documentazione sono presenti. Può
certificarli automaticamente soltanto dopo test non vuoti e contratto indipendente
passati sui file correnti. Il registro distingue questa verifica del sistema da
una chiamata IA. Un controllo fallito viene consegnato al modello per la correzione
entro i limiti; non viene presentato come riuscito.

Se il modello conclude con un messaggio di testo dopo run_checks, il controller
può registrare finish senza un'altra risposta IA. Richiede piano, criteri,
documentazione e verifiche passate sui file correnti, con hash ancora valido.
La conclusione viene attribuita al sistema nel registro; il solo testo del modello
non certifica il risultato. Una prova già corretta può essere ricontrollata e
conclusa alla ripresa anche quando le chiamate IA disponibili sono esaurite.
La conclusione automatica rispetta Pausa e Ferma prima di registrare Pronto.

Nel progetto ordinario dell'interfaccia, il limite di chiamate IA non impedisce
il controllo dei file già creati: se piano, criteri e fonti sono presenti, il
sistema può eseguire run_checks e concludere senza altre risposte del modello,
entro gli altri limiti. Riprendi applica lo stesso controllo ai progetti fermi
sul limite. Prove fallite o assenti impediscono Pronto; un fallimento invariato
non viene rieseguito automaticamente più volte. I contatori restano conservati.

Se `main.py` manca durante la ripresa e non è mai stato versionato, la prova può
recuperare il codice esatto di una precedente risposta IA la cui scrittura era
stata bloccata soltanto dai prerequisiti di piano/documentazione. Richiede che
questi siano ora soddisfatti, registra origine e hash, conserva il risultato
fallito storico e permette rollback. Non recupera file eliminati o esiti ignoti
e non inserisce codice di riferimento al posto del modello. I file recuperati
devono comunque superare le verifiche in Docker. Nessun budget viene azzerato.

Per il difetto riconosciuto di riavvio (`Address already in use` con gli altri
controlli API passati), la prova può applicare una procedura del sistema che
rilascia il listener dopo `shutdown()`. Conserva la versione precedente, lascia
invariati i test e ripete le prove in Docker. Il rapporto `system_corrections`
attribuisce questa modifica a Codex/sistema, senza presentarla come correzione Groq.
La copia con difetto deliberato ha un contesto separato: piano e documentazione
sono preparati dal sistema, ma la correzione deve essere scritta dal modello.
L'accettazione richiede l'errore `test_strip` iniziale, una scrittura IA riuscita
corrispondente al file finale, tutti i controlli passati, test e originale invariati.
## Backend separato del progetto e32ae57b

La consegna in `examples/attivita_consegna` completa il programma mancante nello
ZIP dell'utente, con una pagina italiana, SQLite, API e avvio isolato in Docker.
È completata da Codex dal riferimento dichiarato, non generata dall'agente Groq.
18 test e 5 controlli API passati in Docker Linux, smoke Chromium e persistenza
del volume passati. Leggere `LEGGIMI.txt` e `RISULTATI.json` nella cartella.
Sul PC Windows l'utente ha confermato avvio diretto, salvataggio e permanenza dei
dati dopo docker restart e ricarica. I nuovi AVVIA.bat/FERMA.bat corretti restano da
provare sul PC. Il progetto originario
nell'interfaccia Officina rimane distinto e incompleto; nessun contatore azzerato.

Per leggere lo stato del progetto originale senza chiamate IA o esecuzione di
codice generato, usare `scripts/leggi_diagnosi.py --progetto ID`. Questo modo
seleziona la memoria principale dell'interfaccia; senza l'opzione il diagnostico
legge la prova di generazione CLI, mentre `--correzione` legge la relativa copia.
