# Officina — assistente personale, v0.1

Interfaccia italiana nel browser, memoria SQLite e agente di programmazione integrato
con l’SDK ufficiale OpenAI e la Responses API. Questa prima versione si concentra su
un piccolo backend attività in Python: è il traguardo verificabile da cui partire,
prima di estendere l’assistente ad altri backend e alle infrastrutture blockchain.

L’applicazione si avvia anche senza credenziale, ma non inventa risposte IA: mostra
**Serve il tuo intervento**. Le prove con un vero modello richiedono una chiave API.
L’abbonamento ChatGPT non comprende automaticamente l’utilizzo delle API.

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

Procedi un passo alla volta. Estrai il pacchetto in una cartella del tuo profilo
personale, per esempio `Documenti\Officina`.

1. Installa **Python 3.12, 64 bit** da <https://www.python.org/downloads/windows/>.
   Mantieni il launcher `py` selezionato durante l’installazione.
2. Apri **installa.bat**. Installa le dipendenze bloccate con verifica degli hash.
3. Apri **avvia.bat**. Il browser si apre automaticamente e puoi vedere interfaccia,
   documenti e progetti salvati. La chiusura del browser non ferma l’app: usa Ctrl+C
   nella finestra di avvio per chiuderla.

Per attivare il lavoro autonomo dell’agente:

1. Installa **Docker Desktop** da <https://docs.docker.com/desktop/setup/install/windows-install/>.
   Avvialo con il motore WSL 2 e i container Linux.
2. Apri **prepara_isolamento.bat**. Scarica l’immagine Python, conserva il digest
   verificato da Docker e prepara l’esecuzione isolata.
3. Apri **configura_ia.bat**. Inserisci la chiave API nella finestra locale con input
   nascosto; il valore viene salvato soltanto in `.env`, escluso da Git e dal pacchetto.
   In alternativa copia `.env.example` in `.env` e imposta `AI_PROVIDER_KEY` manualmente.
4. Riavvia **avvia.bat**, descrivi il risultato e premi **Avvia**. Se avevi iniziato un
   progetto senza credenziale, selezionalo e premi **Riprendi**.

La compatibilità Windows è predisposta ma **non è stata verificata su Windows**.
Le verifiche registrate in questa consegna sono state eseguite su Linux.

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

Per verificare la generazione e correzione con l’IA reale, dopo la configurazione:

```powershell
.venv\Scripts\python.exe scripts\prova_agente.py
```

Lo script chiede all’agente di costruire il backend da zero e verificarlo. Poi crea
un **secondo progetto**, copia il risultato e introduce un difetto in
`regression_target.py`. Richiede che l’agente riproduca il fallimento prima di correggere,
ripeta le prove e conservi il progetto originale. I risultati vengono salvati in
`.data/live-acceptance/RESULTS.json`. L’assenza della chiave produce exit code 2,
**NON ESEGUITA**, senza simulazioni o addebiti API. Un risultato fallito produce exit code 1.

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
datate della documentazione ufficiale Python e del README dell’SDK OpenAI, consultate
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
Il modello predefinito è `gpt-5-mini`; disponibilità e autorizzazione vanno verificate
sul tuo account. L’SDK è bloccato alla versione 3.29.0 consultata il 12 ottobre 2026.

Il registro conserva token effettivi quando il provider li restituisce. Il costo è
una **stima** soltanto se imposti entrambi i prezzi per milione di token. Il limite
facoltativo `MAX_ESTIMATED_COST_USD` prenota prudentemente il costo prima di chiamare
l’API. Prezzi, cache e fatturazione effettiva dipendono dal provider: configura anche
il budget nell’account OpenAI. Un errore di rete può impedire di conoscere l’utilizzo
di una chiamata già ricevuta dal provider.

Il backend dell’assistente ascolta solo su loopback. Le modifiche API richiedono un
token di sessione e un’origine locale; non è un servizio pubblico. La chiave rimane
nel processo locale dell’assistente. Obiettivi, documenti pertinenti, codice e risultati
dei tool sono trasmessi a OpenAI per il lavoro: non inserire dati che non vuoi inviare.

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
