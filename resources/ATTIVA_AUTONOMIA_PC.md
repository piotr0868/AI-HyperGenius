# Applicare e provare il lavoro autonomo di Officina sul PC

L'utente ha ribadito che vuole l'agente capace di lavorare autonomamente: una
descrizione del risultato, poi pianificazione, file, prove e correzioni, senza
dover suggerire i passaggi tecnici. Questo e' il mandato gia' autorizzato sul
progetto. Continua il lavoro e fai le normali scelte tecniche senza riconferme.
Il mandato non modifica i permessi del sistema operativo o i blocchi di sicurezza.

## Stato da conservare

Officina sulla porta 8765 e il progetto e32ae57b463c406381faa8efec493542 sono
gia' verificati. Il Codex locale ha installato APRI_OFFICINA.bat e il collegamento
Desktop **Apri Officina**, con controlli HTTP/HTML e riuso del server riusciti.
I backend sulle porte 8766/8767 e i dati restano intatti. Il controllo automatico
della finestra Chrome non ha identificato l'URL ed e' stato interrotto: non
eludere quel blocco. La foto gia' inviata dall'utente nella chat separata mostra
Officina con stato Pronto e 5 test passati; non attribuirsela come osservazione
diretta di questa sessione. Non chiedere altre foto per controlli API o del codice.

## Modifica pronta da applicare

La modifica app/agent.py elimina l'arresto evitabile quando il modello conclude
in testo senza avere completato i file o le prove. Il sistema tenta le verifiche
sui file salvati, entro il budget delle operazioni. Se passano certifica l'hash
corrente. Se falliscono o mancano prerequisiti, rimanda al modello il rapporto e
gli chiede di continuare automaticamente, nello stesso progetto e con gli stessi
limiti. Non ripete prove strutturate fallite sui file invariati. Pausa, Ferma,
domande indispensabili e limiti restano rispettati; nessuna riuscita dal solo testo.
Il limite delle operazioni blocca anche ulteriori richieste al modello.

AGENTS.md rende persistente il mandato per Codex: decisioni tecniche autonome,
comunicazione italiana, prove reali, protezione dei dati e domande soltanto
indispensabili. La prima versione dell'agente resta specializzata nel backend
attivita' Python descritto nel contratto; non e' una prova di autonomia generale
per tutti i linguaggi o infrastrutture blockchain.

## Procedura autonoma

1. Dalla revisione fissata indicata nell'incarico, scaricare VERIFICHE.json e
   verificare source_sha256 dei seguenti file prima dell'installazione:
   `app/agent.py`, `AGENTS.md`, `tests/test_autonomous_completion.py`.
   Prima salvare copie dei file locali in una nuova directory `.data/updates/`.
   Non sostituire .env, memoria, launcher, STATO_PROGETTO.md o altri file locali.
2. La base del controller prima di questa modifica e' la revisione
   da935ebb9731711e1ed90ee202bad389dce34a4b. Confrontare il sorgente locale anche
   normalizzando i fine riga. Se contiene altre modifiche effettive, integrare
   la differenza preservandole e registrare hash e attribuzione del risultato.
   Se AGENTS.md esiste gia', integrarvi le istruzioni senza cancellare quelle
   locali compatibili. Leggere e seguire le istruzioni una volta installate.
3. Eseguire gli 11 casi in tests/test_autonomous_completion.py nella .venv del
   progetto, con Docker reale. I client SDK di questi test usano HTTP simulato:
   non consumano richieste Groq e non vanno dichiarati prove di un modello reale.
   I file di fixture sono il riferimento dichiarato, non una generazione IA.
   Se servono dipendenze di test, usare manifest/lockfile esistenti e verifica hash.
   Analizzare gli errori e correggere soltanto cio' che serve, mantenendo i test.
4. Riavviare soltanto il processo Officina identificato su 8765, nel percorso
   del progetto. Se ci sono lavori attivi, conservarne checkpoint e controllo
   prima di riavviare. Non arrestare genericamente Python, Docker o i backend
   separati. Usare APRI_OFFICINA.bat, che carica la credenziale locale esistente.
   Controllare HTML, API e presenza del vecchio progetto Pronto con hash invariato.
5. Per provare l'autonomia reale eseguire **una sola prova** in un nuovo progetto
   UI chiaramente chiamato "Verifica autonomia", con il backend attivita' del
   contratto. Usare il provider Groq e la credenziale locale gia' configurati,
   entro i limiti ordinari esistenti. Usare le API locali previste e il token
   della sessione senza mostrarlo nei log. Questa e' una nuova attivita'
   esplicitamente limitata: non azzerare o aumentare i contatori dei progetti
   esistenti, non avviare nuovamente la prova CLI separata gia' passata e non
   passare a un provider a pagamento. Se la configurazione non consente la prova
   gratuita con Groq o la quota e' esaurita, registrare quel blocco preciso.
6. Durante questa prova lasciare che sia l'agente di Officina a costruire i
   file e correggerli con i suoi strumenti. Codex puo' correggere il controller
   con prove e versioni, ma non scrivere un backend sostitutivo nel progetto
   facendolo passare per riuscita autonoma dell'agente. Attendere l'esito entro
   il timeout effettivo, conservando piano, storia, chiamate, token e prove.
   Se il lavoro si ferma su un limite reale, non creare altre prove in sequenza.
7. Aggiornare lo STATO_PROGETTO.md locale e `.data/CONTINUA_SUL_PC.md` con i risultati effettivi, l'eventuale
   hash verificato e l'uso riportato. Distingui i test del controller, la prova
   del modello reale, i blocchi di quota e i controlli visivi non eseguiti.
   Mostrare all'utente soltanto risultato, problema rimasto e prossimo passo in
   italiano. Aprire Officina e indicare **Apri Officina** come unico collegamento
   principale. Chiedere soltanto un'azione indispensabile con finestra e pulsante
   precisi. Nessuna richiesta ripetuta di permessi gia' concessi per il progetto.
