# Salvataggio completo e ripresa del lavoro di Officina sul PC

## Richiesta dell'utente, 15 ottobre 2026

L'utente vuole salvare tutto il lavoro pertinente svolto dal Codex locale,
incluse richieste, decisioni, autorizzazioni e punto di ripresa, per continuare
domani senza dover ricordare o riscrivere i dettagli. Eseguire il salvataggio
adesso, prima di ulteriori sviluppi. Non spegnere o riavviare il PC.

Queste istruzioni non sono un backup e la copia cloud non contiene gli ultimi
sorgenti Windows. Operare sui file locali piu' recenti, senza sostituirli con
vecchi sorgenti GitHub. Non chiedere all'utente di raccogliere dati tecnici.

## 1. Ispezionare e conservare

- Leggere AGENTS.md, STATO_PROGETTO.md, .data/CONTINUA_SUL_PC.md, la matrice
  delle capacita' e i riferimenti ai rapporti locali. Integrare il mandato
  resources/INCARICO_E_RIPRESA_OFFICINA.md con la conversazione corrente.
- Ispezionare gli strumenti gia' disponibili. La sessione locale ha mostrato
  scripts/salva_versione_officina.py: leggerlo e riutilizzarlo se appropriato.
  Non assumerlo completo senza controllare quali file e dati include.
- Rilevare eventuali lavori attivi; ottenere un checkpoint coerente mediante
  i controlli supportati. Non terminare processi per nome o PID vecchi e non
  cancellare sessioni, archivi o progetti. Preservare Pausa/Ferma e contatori.
- Operare con l'account ordinario dell'utente. La precedente preparazione
  amministrativa di Codex non autorizza l'esecuzione generale come amministratore.

## 2. Scrivere una consegna persistente prima del backup

Aggiornare stato e istruzioni di continuazione locali, conservando i contenuti
validi. Il prossimo avvio deve poter recuperare almeno:

- Obiettivo: assistente di ingegneria backend/blockchain per progetti diversi;
  il backend attivita' e' un esempio di regressione, non il requisito universale.
- Richieste originali pertinenti, correzioni di obiettivo, scelte tecniche e
  autorizzazioni esplicite con ambito. Nessun segreto nei testi o nei registri.
- Traguardi conclusi, prove passate/fallite/non eseguite, ID dei progetti,
  percorsi dei rapporti e hash pertinenti, versioni e contatori correnti.
- Lavori interrotti o processi pertinenti ancora attivi e come identificarli
  nuovamente, senza presumere che i vecchi PID siano validi domani.
- Il prossimo passo tecnico concreto, ricavato dalla matrice locale aggiornata,
  e i blocchi che non devono essere ritentati senza un cambiamento significativo.
- Modalita' di ripresa e ripristino del backup, percorso effettivo e riferimenti
  alla conversazione Codex corrente. Prevedere una consegna utilizzabile anche
  da una nuova sessione se quella precedente diventasse indisponibile.

Ultimo stato riferito alla chat: riavvio Windows verificato senza ripetere la
sonda, memoria conservata, 13 test Docker passati e contatori invariati;
migrazioni SQLite documentate confermate. Nuova prova reale Go/PostgreSQL con
6 test e controllo indipendente di concorrenza/idempotenza/recupero del database.
Suite locale 145 test passati. Solana ancora bloccata con protezioni attive;
architetture con piu' microservizi richiedono prove dedicate. Verificare questi
riferimenti nei file locali e preservare eventuali progressi piu' recenti.

Registrare separatamente il consenso persistente dell'utente e i permessi
tecnici effettivi con la loro durata. Un file non rende permanenti permessi
Windows temporanei. Non richiedere nuovamente il consenso gia' documentato per
le normali operazioni pertinenti. Mantenere le protezioni e i controlli supportati.

Integrare AGENTS.md affinche' legga la consegna all'avvio e imponga checkpoint
durante il lavoro, dopo i traguardi, prima delle operazioni lunghe e in chiusura.
Non affidare il salvataggio soltanto alla memoria della conversazione o all'uscita.

## 3. Creare il backup locale versionato

- Scegliere una destinazione separata dalla cartella del progetto e dai file
  sorgente, per esempio una sottocartella datata di
  %LOCALAPPDATA%\Officina\backups. Applicare i permessi appropriati all'utente.
  Non includere ricorsivamente backup precedenti o la destinazione stessa.
- Includere sorgenti attuali, test, lockfile/configurazioni riproducibili,
  launcher, documentazione, incarico, consegna e modifiche non ancora committate.
- Salvare memoria e dati pertinenti di .data: progetti generati, registri,
  contatori, procedure, fonti, rapporti e versioni ripristinabili. Per SQLite
  usare una copia consistente tramite backup API o strumento equivalente;
  non limitarsi a copiare un file database in scrittura ignorandone il WAL.
- Identificare i dati persistenti dei soli servizi Docker di Officina. Se devono
  essere conservati, usare esportazioni consistenti appropriate al servizio,
  senza copiare alla cieca file di database in esecuzione. Non toccare servizi
  estranei. Distinguere dati utili e ambienti di test interamente ricreabili.
- Non copiare inutilmente .venv, file temporanei o tutte le immagini Docker:
  conservare lock, digest e istruzioni di ricostruzione degli ambienti ricreabili.
- Preservare le credenziali nelle posizioni protette esistenti. Non leggerne
  i valori con strumenti del modello, stamparli o inserirli in consegne/GitHub.
  Un eventuale backup delle credenziali deve usare un meccanismo locale protetto
  adatto a Windows, eseguito senza esporre i valori al modello. Dichiarare le
  dipendenze da account/macchina per il ripristino. Non creare un archivio
  esportabile con chiavi in chiaro e non copiare l'intera configurazione Codex
  contenente autenticazione per salvare una sola conversazione.
- Salvare il riferimento e, tramite meccanismi supportati, gli artefatti della
  conversazione Codex pertinente al progetto, senza includere altre conversazioni
  personali o file di autenticazione. Registrare l'ID effettivo, senza inventarlo.

## 4. Verificare il backup

- Produrre un manifest con percorsi relativi, dimensioni, hash, data, ambito ed
  esclusioni, senza segreti. Registrare esplicitamente eventuali elementi mancanti.
- Provare apertura/estrazione in una directory temporanea separata, confrontare
  file e hash e verificare integrita' dei database copiati, progetti e contatori
  rispetto al checkpoint. Non ripristinare sopra gli originali.
- Verificare che consegna, stato e riferimenti ai rapporti esistano nel backup.
  Mantenere coerenti snapshot e manifest dopo gli ultimi aggiornamenti ai file.
- Non eseguire i programmi generati sul PC durante queste verifiche. I controlli
  di archivi/database possono usare gli strumenti fidati dell'assistente;
  l'esecuzione dei progetti resta nei sandbox Docker previsti.
- Non ripetere le 145 prove, le generazioni IA o la sonda di riavvio solo per
  copiare i file. Eseguire i controlli pertinenti al backup e alle eventuali
  modifiche realmente necessarie agli strumenti di salvataggio.
- Non dichiarare "tutto salvato" se dati necessari o verifiche essenziali mancano.
  Completare il lavoro indipendente e indicare il limite concreto.

## 5. Preparare un solo collegamento per domani

Creare sul Desktop effettivo dell'utente **Riprendi lavoro Officina**. Conservare
Apri Officina, che serve ad avviare l'applicazione, senza cambiarne il significato.

Il nuovo collegamento deve aprire il Codex locale nella cartella corretta e
riprendere la conversazione identificata per questo lavoro, leggendo incarico,
stato e consegna. Preferire l'ID della conversazione effettiva a una generica
"ultima sessione" che potrebbe essere diversa domani. Se la versione permette
un messaggio iniziale di ripresa, verificarne la sintassi con l'help locale e
predisporlo in modo da evitare all'utente di riscrivere il mandato.

Riutilizzare login e configurazioni esistenti; gestire i normali permessi gia'
autorizzati con i meccanismi supportati. La 0.161.0 locale ha gia' richiesto
--no-daemon e supporta --approve-for-me: verificarne disponibilita' nella versione
effettiva. Non introdurre bypass del sandbox o dei controlli di accesso.

Validare eseguibile, cartella, ID e argomenti senza aprire una seconda sessione
attiva che duplichi i lavori correnti. Distinguere le verifiche eseguite dal primo
utilizzo che avverra' domani. Nessun nuovo riavvio del PC per questa operazione.

## 6. Copia Git se l'accesso e' gia' disponibile

Se il progetto e' gia' collegato a GitHub con accesso funzionante, salvare anche
sorgenti e istruzioni in un commit/branch identificabile. Ispezionare Git e le
modifiche, escludere credenziali, memoria privata, .data, backup, log e conversazioni.
Non usare add indiscriminati, reset/checkout distruttivi o push forzati. Non
applicare vecchi sorgenti remoti sopra il lavoro locale. Destinazione autorizzata:
piotr0868/AI-HyperGenius; conservare eventuali modifiche remote compatibili.

Usare l'autenticazione gia' disponibile senza estrarre token o chiedere segreti
in chat. Se GitHub non e' utilizzabile, il backup locale verificato e la consegna
devono essere comunque completati: indicare separatamente la copia remota non
eseguita, senza bloccare il salvataggio per un nuovo login non indispensabile.

## Conclusione richiesta

Aggiornare lo stato effettivo e dare all'utente un riepilogo italiano breve:
1. Percorso del backup e verifiche eseguite, oppure limite preciso.
2. Conferma dei file di incarico/consegna e dell'ID della conversazione registrato.
3. Conferma del collegamento Riprendi lavoro Officina e verifiche effettuate.
4. Nome del commit/branch se la copia Git e' riuscita.
5. Se il lavoro e' in uno stato salvato coerente e puo' essere chiuso senza
   interrompere operazioni ancora necessarie. Non spegnere il computer.

Non iniziare nuovi sviluppi: lo scopo immediato e' chiudere il lavoro in modo
recuperabile e documentare il primo passo concreto da eseguire domani.
