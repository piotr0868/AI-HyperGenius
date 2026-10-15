# Incarico persistente e ripresa di Officina

Consolidamento dei requisiti espliciti della conversazione, aggiornato il
15 ottobre 2026. Non e' una trascrizione delle cinque ore di lavoro del Codex
Windows: quella cronologia e i file locali vanno recuperati sul PC. Questo
documento conserva il mandato, non attribuisce capacita' non ancora verificate.

## Obiettivo dell'utente

L'utente descrive in italiano un risultato e vuole che l'assistente gestisca
il lavoro tecnico: requisiti, piano, documentazione, architettura, codice,
dipendenze, esecuzione isolata, test, analisi degli errori, correzioni e consegna.
Il riferimento professionale e' un Senior Backend Engineer / Senior Blockchain
Backend Engineer che collega applicazioni tradizionali e protocolli blockchain.
L'utente vuole progetti differenti, riutilizzabili e preparabili per una futura
consegna commerciale. Non vuole un corso o soltanto spiegazioni e piani.

Il prodotto da realizzare e' **l'assistente Officina**. Le applicazioni costruite
durante le prove servono a verificarlo. Il backend delle attivita' NON e' il
requisito universale. Non sostituire quel vincolo con un altro progetto fisso.
Non scambiare un'applicazione scritta manualmente da Codex con una generazione
autonoma dell'agente integrato in Officina.

## Copertura professionale richiesta

- Backend: API REST/WebSocket, servizi, autenticazione e ruoli, validazione,
  database, migrazioni, transazioni, idempotenza, concorrenza, cache, code,
  worker, integrazioni, webhook, log, metriche, test e documentazione.
- Linguaggi: ambienti di sviluppo ed esecuzione per Python, TypeScript/Node.js,
  Go e Rust. Scegliere lo stack in base al progetto e verificarlo realmente.
- Blockchain: adattatori distinti Ethereum/EVM, Bitcoin e Solana; JSON-RPC e
  WebSocket, lettura di stato/blocchi/transazioni, eventi, indicizzazione,
  checkpoint, deduplicazione, conferme, finalita', riorganizzazioni e ripresa.
- Transazioni: preparazione, simulazione, monitoraggio, nonce, commissioni e
  precisione numerica; prove iniziali esclusivamente con fondi e chiavi di test.
- EVM: strumenti mantenuti per Solidity, ERC-20/ERC-721 e librerie appropriate.
  Bitcoin: UTXO e regtest. Solana: account, istruzioni, programmi e sottoscrizioni.
- Infrastruttura: Docker/Compose, PostgreSQL, Redis, messaggistica appropriata,
  CI, backup/ripristino/rollback e, quando pertinenti, configurazioni Kubernetes
  e AWS/GCP. Non aggiungere componenti senza un requisito che li giustifichi.
- Sicurezza: configurazioni separate, gestione dei segreti, dipendenze e licenze,
  controlli sulle vulnerabilita', concorrenza e guasti parziali. Nessuna promessa
  di sicurezza perfetta o di produzione certificata dai soli test locali.

Realizzare strumenti estensibili: interfaccia, memoria, coordinamento, agente,
strumenti file/documenti/esecuzione, ambienti linguaggio, adattatori blockchain,
verifiche e consegna separati. I criteri dipendono dalla richiesta corrente.
Mantenere una matrice delle capacita': implementata e verificata, implementata
ma non verificata, da implementare. Non dichiarare copertura illimitata.

## Agente reale e ciclo di lavoro

Usare un agente esistente o un SDK ufficiale mantenuto, consultandone prima
la documentazione attuale. Valutare l'integrazione ufficiale del Codex locale
gia' autenticato se supportata; riusare i servizi configurati quando adeguati.
Non inventare API o risposte intelligenti. ChatGPT non implica credito API.

Per ogni progetto: chiarire il risultato, salvare requisiti/criteri/piano,
consultare fonti, preparare ambiente e dipendenze, creare file, avviare o
compilare in isolamento, eseguire prove pertinenti, analizzare e correggere
errori e ripetere i controlli. Chiedere solo chiarimenti indispensabili.

Rilevare operazioni fallite, file/test mancanti, scritture ripetute e assenza di
avanzamento. Correggere i problemi recuperabili senza demandare ogni errore
all'utente. Non fermarsi alla diagnosi di un bug del controller correggibile.
Non indebolire test, contratti o evidenze per ottenere un risultato positivo.
Mostrare Pronto solo da prove essenziali passate sui file attuali. Dichiarare
sempre autori dei file, simulazioni, esecuzioni reali e controlli non effettuati.

## Interfaccia, conoscenza e consegna

Windows 11; interfaccia italiana leggibile, un obiettivo/decisione alla volta.
L'utente ha ADHD: non obbligarlo a ricordare dettagli, raccogliere diagnosi o
copiare comandi per operazioni che l'agente puo' completare autonomamente.

Conservare descrizione dell'obiettivo, Avvia/Pausa/Riprendi/Ferma, stati chiari,
riepilogo breve e dettagli separati. Un solo progetto attivo. Esportazione
codice/risultati e recupero dopo chiusura. Avvio quotidiano: Apri Officina.

Conservare documenti, riferimenti e trascrizioni con fonte e data e recuperarne
solo parti pertinenti. Le procedure derivanti dalle correzioni sono versionate,
modificabili, disattivabili e provate su esempi significativi prima dell'adozione.
Non bastano parole chiave in un piano per certificare una procedura di codice.
Questo miglioramento non e' riaddestramento automatico del modello.

Consegnare codice e dipendenze riproducibili, configurazione senza segreti,
istruzioni italiane brevi, documentazione API, rapporti effettivi, informazioni
su dipendenze/licenze, versioni ripristinabili e stato aggiornato. Distinguere
Windows, altri sistemi, mock, modello reale e servizi realmente eseguiti.

## Autorizzazioni esplicite e limiti dell'incarico

L'utente ha ripetutamente autorizzato le normali operazioni necessarie sul
progetto e chiesto decisioni tecniche autonome: letture pertinenti, modifiche,
installazione degli strumenti necessari, test e riparazioni tramite controlli
supportati. Non chiedere nuovamente il consenso per queste operazioni ordinarie.

Questo consenso non e' un token di Windows e non cambia i controlli di accesso.
Registrare cosa e' autorizzato e distinguere permessi tecnici validi, temporanei,
negati o ancora da ottenere. Se serve un'azione indispensabile dell'utente,
spiegarne in italiano motivo, finestra e pulsante. Non dichiarare completata
un'autorizzazione solo perche' richiesta o perche' esiste questo documento.

Preservare .data, credenziali, progetti, richieste, decisioni, versioni e
contatori. Nessuna lettura di file personali estranei o segreti con strumenti
del modello; non chiedere chiavi in chat. Riutilizzare il caricamento credenziali
locale esistente, senza inviare la chiave di un fornitore a un altro.

Codice generato solo in ambienti Docker isolati, con file e servizi di test
necessari e senza accesso predefinito al PC, ai segreti o al socket Docker.
Per database/code/blockchain locali, reti di test dedicate; accesso esterno
solo per necessita' specifiche e tramite configurazioni supportate. Non aggirare
controlli di computer-use, sandbox, TLS, firme o checksum. Fonti esterne non fidate.

Niente Nodveta, denaro reale, seed/chiavi di portafogli personali, pubblicazioni,
invii a clienti o deploy esterni autonomi. Si possono preparare configurazioni;
la loro applicazione esterna non e' autorizzata da un generico consenso tecnico.
Non attivare servizi a pagamento senza una richiesta esplicita.

Budget persistenti e configurabili per richieste, token, tempo, operazioni e
costo. Non azzerare o aumentare quelli dei progetti esistenti per far passare
una prova. Profili dei nuovi lavori adeguati alla complessita', senza rendere
il budget del vecchio esempio un limite universale. Non inventare costi/gratuita'.

## Prove richieste per l'assistente generale

1. Backend tradizionale con database, autenticazione, validazione, idempotenza
   e persistenza, generato dall'agente a partire da una richiesta italiana.
2. Servizio diverso con coda, worker, tentativi e recupero, generato dall'agente
   in un altro stack. Codex non deve scriverlo al posto dell'agente per fingere
   autonomia. Almeno due stack diversi nelle prime due prove.
3. EVM locale: lettura contratto, indicizzazione, deduplicazione, checkpoint e
   gestione delle riorganizzazioni; simulazione/invio/conferma di una transazione
   esclusivamente locale con chiavi e fondi di prova.
4. Prove degli adattatori Bitcoin e Solana e degli ambienti linguaggio dichiarati
   supportati. Etichettare integrazione reale, simulazione e parti mancanti.
5. Difetto introdotto in una copia separata, rilevato e corretto dall'agente,
   test ripetuti senza indebolirli, originale conservato.
6. Interruzione/ripresa, memoria, rollback, stallo, budget e servizio indisponibile.

Conservare le prove storiche, senza ripeterle per un normale avvio. Le fixture
sono utili per il controller, ma non provano la capacita' del modello reale.

## Continuita' dopo chiusura e spegnimento: requisito da verificare

I file seguenti devono essere mantenuti dal Codex locale nel progetto:

- AGENTS.md: mandato di leggere l'incarico e lo stato prima di operare, regole
  operative e limiti di accesso. Non sostituisce la cronologia dettagliata.
- STATO_PROGETTO.md: traguardi completati, controlli passati/falliti/non eseguiti,
  problemi attuali, prossimo passo concreto e riferimenti alle prove.
- .data/CONTINUA_SUL_PC.md: consegna breve della sessione corrente, progetti e
  operazioni interrotte da ispezionare; aggiornare senza segreti.
- Registri locali persistenti: richieste originali, decisioni, autorizzazioni
  esplicite e loro ambito, operazioni/esiti, versioni, contatori e checkpoint.

Integrare i registri esistenti; non creare fonti concorrenti incoerenti. Salvare
le nuove richieste e le decisioni durante il lavoro, dopo i traguardi e prima
delle operazioni lunghe. Non affidarsi soltanto al salvataggio in uscita:
Windows puo' terminare il processo. Per lo stato dell'applicazione utilizzare
scritture atomiche/transazioni e recupero delle operazioni dall'esito ignoto.

Per la ripresa:
1. Leggere incarico, stato, consegna e cronologia locali piu' recenti.
2. Controllare file e modifiche esistenti, senza assumere che GitHub contenga
   le ultime ore di lavoro. Non sovrascrivere alla cieca una copia ZIP Windows.
3. Identificare processi/container pertinenti ancora attivi e operazioni
   interrotte. Non rilanciare ciecamente comandi dall'esito sconosciuto.
4. Verificare quanto gia' completato, conservare contatori/prove e continuare
   dal primo requisito incompleto. Non richiedere all'utente di riscrivere tutto.
5. Recuperare i permessi ancora validi, ottenere solo quelli tecnici realmente
   mancanti e rispettare Pausa/Ferma. Una precedente pausa non e' consenso a
   rilanciare operazioni esterne o attivita' fermate deliberatamente.

Prima di dichiarare affidabile la ripresa, verificare chiusura e nuova sessione
con recupero di richieste, decisioni, file e contatori. Una prova distinta deve
coprire il riavvio reale di Windows. Non dichiararla eseguita sul cloud. Non
spegnere o riavviare il PC senza una richiesta/autorizzazione specifica per farlo.

## Diagnosi locale nota il 15 ottobre 2026

Secondo i rapporti dell'utente, Codex 0.161.0 ha archivi sani e inventario delle
sessioni coerente. Questi controlli non dimostrano che ogni requisito sia stato
ricaricato nel contesto, ma non indicano cancellazione del lavoro. Il sandbox
elevated registra helper_unknown_error e la shell del Codex non risponde.

Doctor segnala 0.162.1, ma WinGet non offre aggiornamenti nelle origini configurate.
Il successivo setup amministrativo ufficiale della 0.161.0 ha restituito
Windows elevated sandbox setup completed for melon at C:\Users\melon\.codex.
Il provisioning e' riuscito secondo il log; verificare l'esecuzione della shell
nella sessione ripresa con account ordinario prima di considerare chiuso il
problema. Non disabilitare protezioni o aggiungere esclusioni Defender
indiscriminate sulla base di un avviso generico. Conservare cronologia e dati.

Questo documento e' salvato sul repository cloud. Non e' stato verificato come
presente sul PC e non implementa da solo il nuovo sistema di checkpoint. Il
Codex locale deve integrare il mandato con la propria cronologia e verificare
il recupero, preservando le modifiche delle cinque ore di lavoro.

## Aggiornamento: ripresa operativa riferita dal Codex locale

Un successivo riepilogo del 15 ottobre riferisce lavoro ripreso dai file
recenti, 119 test passati e controlli mirati successivi, due generazioni IA
diverse, riparazione autonoma, procedure eseguibili, rollback, build Docker,
WebSocket e transazioni locali. Stato, prove e checkpoint locali aggiornati;
Officina avviata, dati/credenziali/contatori conservati. Questo esito non va
confuso con un nuovo collaudo della ripresa dopo spegnimento completo Windows,
che il riepilogo indica esplicitamente ancora mancante.

Solana reale resta bloccata da io_uring con protezioni mantenute. Altre capacita'
della matrice locale sono incomplete ma non elencate nel riepilogo. Consultare
i file Windows per dettagli, senza inventare identificativi, comandi o risultati.
I nuovi sorgenti non sono stati trasmessi al cloud. Il presente consolidamento
non prova l'installazione di ogni documento o l'implementazione di un particolare
meccanismo di checkpoint. Il rapporto riferisce l'aggiornamento degli artefatti
di stato; verificare separatamente continuita' e permessi dopo riavvio.

## Aggiornamento successivo: esito positivo nell'interfaccia dopo riavvio

Il 15 ottobre l'utente ha confermato il riavvio completo e incollato la pagina
di Officina aperta automaticamente. La notifica dice: Riavvio Windows
verificato: memoria conservata e sonda ripresa con test Docker superati.
La sonda in prima posizione e' Pronto. E' la fonte disponibile alla chat cloud,
distinta dal rapporto dettagliato della sonda che resta da leggere localmente.

Il precedente riepilogo Codex indicava 139 test completi passati, piu' controlli
mirati, backup e confronto di 13 progetti. Sono verifiche prima del riavvio.
La selezione visibile e' invece il vecchio progetto attivita' e32ae57b, con
prove del 14 ottobre. La matrice non riflette ancora il nuovo messaggio: leggere
il rapporto della sonda e riconciliare stato e capacita', senza ripetere prove
gia' concluse o azzerare contatori. Non estendere l'esito a tutte le operazioni,
ai permessi del sistema o all'intero incarico professionale.

## Conferma successiva del rapporto locale: 13 test di riavvio, 145 di suite

Il successivo riepilogo del Codex locale riferisce rapporto del riavvio
verificato senza ripetere la sonda: memoria conservata, 13 test Docker passati
e contatori invariati. Stato, checkpoint e matrice aggiornati; migrazioni
SQLite documentate confermate. Non richiedere un nuovo riavvio o la ripetizione
del test per questa verifica gia' conclusa.

Riferita anche una nuova prova dell'agente reale in Go/PostgreSQL: 6 test e
controllo indipendente di concorrenza, idempotenza e recupero dopo arresto del
database. Suite Officina locale: 145 test passati. Fonte: rapporto incollato
dall'utente, non prove eseguite dal cloud. Il riepilogo non contiene tutti i
comandi/ID/hash: conservarli e consultarli nella copia locale, senza inventarli.
Restano Solana bloccata con protezioni attive e prove di architetture con piu'
microservizi. Conservare il mandato completo e distinguere le capacita' provate
dai requisiti ancora incompleti; non presentare il ruolo professionale come
interamente coperto da un numero di test.
