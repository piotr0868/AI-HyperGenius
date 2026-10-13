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
Il prompt locale per la chiave Groq è stato raggiunto. Un successivo log conferma
casella grafica, chiave salvata e autenticazione/modello riusciti. Nessuna chiave
è stata fornita alla chat.

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
Casella Windows, salvataggio credenziale, SDK/modello Groq, Docker Linux e verifica
senza IA sono confermati dal log del PC. Installazione/aggiornamento winget restano
da provare. I risultati in .data/setup/RESULTS.json appartengono alla macchina che li
ha eseguiti: non trasferire esiti Linux come se fossero verifiche Windows.

### Quota Groq osservata sul PC Windows

Il log dell'utente conferma immagine verificata al digest
python@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1,
backend di riferimento VERIFICATO, difetto RILEVATO e ripristino VERIFICATO.
La generazione con IA è stata tentata ma interrotta da HTTP 429 con Retry-After
48 secondi. Il tipo esatto di quota non era registrato: non attribuirlo con certezza
a RPM/TPM o alla fatturazione. La correzione IA separata non è stata eseguita.
Il server dell'app è partito; una screenshot mostra invece Docker con motore attivo
e avviso di versione non supportata. L'aggiornamento Docker è quindi necessario.

Correzione predisposta: intervallo Groq 60 secondi, output del profilo massimo
3000 token, reasoning low per GPT-OSS secondo la documentazione del SDK installato,
meno duplicati nella richiesta conservando tutta la memoria originale. Su attese
429 brevi fino a 120 secondi sono possibili due riprese automatiche, conteggiate
nel limite totale delle chiamate e persistenti via registro eventi; nessun reset
dei budget e nessun cambio a servizi a pagamento.

La prova di accettazione riprende i progetti già salvati, importa la documentazione
ufficiale nello Store dedicato, conserva esiti precedenti, non reintroduce il
difetto dopo correzione e ricontrolla in Docker i progetti già pronti. Il helper
aggiorna_quota scarica quattro sorgenti da un commit esplicito, con checksum prima
di ogni modifica e copie ripristinabili. Mantiene chiave e memoria; configura il
profilo e può tentare l'aggiornamento Docker con winget prima di riprendere.
La correzione deve ancora essere applicata e verificata sul PC Windows; non
dichiarare completata la generazione finché non arrivano esiti effettivi positivi.
Suite corrente: **65 verifiche passate su Linux**, zero fallimenti/skipped.
I nuovi controlli coprono ripresa della vecchia prova senza reset, correzione
già eseguita conservata, ricontrollo dei pronti, quota breve/lunga e copie con checksum.

L'utente non riesce a identificare il terminale nelle finestre aperte: vede due
finestre di chat, la pagina delle chiavi e il browser Officina. L'aggiornatore ora
accetta --ferma-pid con il PID riportato dal log (18348). Prima controlla con
Windows la porta loopback, il comando di avvio Python e il proprietario del
processo; arresta tramite l'API gli eventuali lavori attivi, poi ricontrolla e
chiude soltanto quel PID. Se non lo identifica, non ferma altri processi e non
modifica sorgenti. Il ramo PowerShell resta da verificare sul PC Windows; nei
test Linux sono verificati i rifiuti, l'ordine delle operazioni e la riservatezza
del token di sessione. Chiave, database e file dei progetti non vengono rimossi.

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

Pausa predefinita di 60 secondi tra le chiamate Groq, contatori persistenti e retry SDK
automatici disabilitati. Le attese brevi 429 sono gestite dall'agente al massimo
due volte; le altre fermano il progetto. Riprendi non azzera i budget. Le procedure
su esempi usano il fornitore scelto.

Restano: obiettivo, piano/criteri prima del codice, Avvia/Pausa/Riprendi/Ferma,
chiarimenti, documenti con fonte/data, ricerca FTS5, procedure versionate e adottabili
solo dopo test su esempi, snapshots ripristinabili, registro e ZIP del solo progetto.
Pronto richiede unittest non vuoti, contratto indipendente e hash dei file invariato.
Docker non ha rete, segreti, cartelle host o socket Docker; niente ripiego sull'host.

## Verifiche effettive

Su Linux, Python 3.12.14, Docker 28.4.0 e Chromium di sistema:

- **65 test passati** nella suite corrente, 0 errori/fallimenti/skipped.
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

Nel **cloud** `GROQ_API_KEY` è ancora assente: zero chiamate live da questo ambiente.
Sul **PC Windows** la credenziale e il modello sono verificati dal log; la prova
con IA è tentata e non completata per quota. Generazione/correzione complete e
procedure con il modello reale restano da verificare. Non richiedere nuovamente
una chiave locale già salvata; usare avvio_automatico che carica il file fuori OneDrive.

Il piano Free e le quote non sono rilevabili affidabilmente dall'app. L'utente deve
controllarli nella console Groq; non è garantito accesso illimitato o assenza di
addebiti se l'account ha già fatturazione attiva. Nessun cambio automatico a OpenAI.

Windows 11: setup, casella, SDK/modello, Docker, prova senza IA e avvio server
confermati da log dell'utente. Nuova correzione della quota e aggiornamento Docker
ancora da verificare. Le verifiche automatiche dell'assistente restano su Linux.
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
