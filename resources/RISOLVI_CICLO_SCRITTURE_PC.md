# Completare il lavoro autonomo sul PC: ciclo di main.py senza test

L'utente vuole che il lavoro venga completato dall'agente e ha gia' autorizzato
le normali operazioni necessarie al progetto, inclusi permessi indispensabili
tramite i controlli supportati. Non rimettergli decisioni tecniche o comandi da
eseguire. Leggere AGENTS.md e lo stato locale; preservare dati e modifiche.

## Stato effettivo ricevuto

Il Codex sul PC ha applicato la revisione 2d18bd2 con checksum/backup e riportato
55 test Windows passati con Docker reale. L'unica nuova prova Groq ha consumato
12 richieste riscrivendo main.py, senza produrre i test. La verifica Docker e'
fallita: quella prova non dimostra ancora autonomia. Il suo ID e i dettagli sono
nel tuo STATO_PROGETTO.md e nella memoria locale, non nel rapporto inviato alla
chat cloud. Trovarli localmente, senza chiedere all'utente di raccogliere dati.

Conservare il vecchio progetto Pronto e32ae57b463c406381faa8efec493542, la prova
CLI separata gia' passata, i backend 8766/8767, il collegamento **Apri Officina**,
credenziali, contatori e limiti. Il blocco computer-use sull'URL non va eluso e
non impedisce controlli del codice, API o HTML. Non chiedere altre immagini per
prove che non richiedono osservare lo schermo.

## Modifica pronta

- Una scrittura identica restituisce unchanged, consuma l'operazione prevista,
  ma non crea altre versioni e non invalida prove ancora valide.
- Se main.py viene riscritto e mancano test, oppure si raggiunge il limite delle
  chiamate senza test, il sistema prepara una base di cinque test HTTP del
  contratto. Aggiunge package e README solo se non esistono e non furono rimossi.
- Non sostituisce main.py. Non modifica test esistenti e non ricrea test rimossi
  intenzionalmente. La base predisposta dal sistema e' protetta dalle riscritture
  del modello, versionata e attribuita con eventi file_sistema e hash.
- Il sistema esegue subito le prove e il contratto indipendente in Docker.
  Se falliscono, restituisce il rapporto al modello per correggere il backend
  entro le richieste rimaste. Evita prove duplicate sui file invariati.
- La riuscita dichiara che i test di base sono predisposti dal sistema, non dal
  modello. Una prova respinta, un limite o un timeout non diventano Pronto.

## Applicazione autonoma

1. Dalla stessa revisione fissata di queste istruzioni scaricare VERIFICHE.json.
   Verificare source_sha256 per i seguenti sette file prima di applicarli:
   app/agent.py, app/providers.py, app/progress.py,
   app/templates/test_activity_api.py.txt, tests/test_progress.py,
   tests/test_agent.py, AGENTS.md. Salvare copie dei file locali esistenti in una nuova
   cartella .data/updates; verificare sintassi dei .py senza eseguire fixture.
   Non sostituire .env, .data, launcher, stato o istruzioni locali.
2. La base prima della modifica e' 2d18bd2dbb657babf4566fcf2e314794f8413ab5.
   Se sorgenti o test locali differiscono dalla base anche dopo normalizzazione
   dei fine riga, integrare la differenza preservando le modifiche. La modifica
   al vecchio test_agent aggiunge soltanto verify alla fixture OfflineSandbox:
   restituisce fallimento esplicito, senza indebolire le asserzioni.
   Integrare AGENTS.md conservando le istruzioni locali compatibili e leggerlo:
   contiene il mandato persistente di completare il lavoro senza riconferme inutili.
3. Eseguire tests/test_progress.py e i test di agente/limiti nell'ambiente locale,
   con Docker reale. Gli SDK usano HTTP simulato in questi test: zero nuove
   richieste Groq, nessuna capacita' del modello dimostrata da queste fixture.
   Risolvere gli errori di installazione o di codice necessari, mantenendo le prove.
4. Riavviare soltanto il processo Officina identificato su 8765, preservando i
   checkpoint. APRI_OFFICINA.bat carica la credenziale locale gia' configurata.
   Non leggere/stampare chiavi con gli strumenti IA e non chiederle nuovamente.
5. Individuare l'ultima prova reale a 12 richieste citata nello stato, registrarne
   ID, contatori, errori e hash di main.py. Provare la ripresa dello **stesso**
   progetto: il recupero dei test non richiede nuove generazioni e non modifica
   il backend. Conservare tutti i limiti. Se tempo, correzioni o operazioni sono
   esauriti, registrarlo senza reset; se il backend non passa, conservare gli errori.
   Una riuscita in questo passaggio e' recupero del sistema sul codice esistente,
   non una nuova generazione IA completa e non test generati dal modello.
6. Eseguire al massimo **una nuova prova di regressione reale** della versione
   corretta, in un nuovo progetto distinto e dichiarato, con Groq gia' configurato
   e il budget ordinario di 12 richieste. Non e' un reset della prova precedente:
   conservare entrambi gli ID e i risultati. Non ripetere prove in sequenza o
   passare a servizi a pagamento. La nuova prova serve a osservare dall'inizio
   scrittura IA, rilevamento dello stallo, test di sistema e correzioni automatiche.
7. Lasciare che l'agente di Officina scriva e corregga il backend con il modello.
   Codex non deve inserire un backend di riferimento o correggere manualmente
   main.py per dichiarare autonomia. Se emerge un difetto del controller, resta
   sul compito: correggilo, aggiungi una prova significativa e ripeti i controlli
   pertinenti. Una diagnosi di un difetto correggibile non e' la consegna finale.
   Rispetta i budget dei progetti; eventuali blocchi di quota/servizio o permessi
   realmente mancanti vanno conservati e indicati precisamente, senza finte riuscite.
8. Aggiornare STATO_PROGETTO.md e .data/CONTINUA_SUL_PC.md con gli esiti reali:
   test Windows, recupero della vecchia prova, nuova prova reale, hash di main,
   contatori, origine dei file e problemi rimasti. Aprire Officina e lasciare un
   riepilogo italiano breve. Chiedere all'utente solo un'azione indispensabile
   per un blocco effettivo, indicando finestra e pulsante; fare autonomamente
   tutto il lavoro indipendente e le normali scelte tecniche gia' autorizzate.

## Prove cloud

183 test passati su Linux, zero errori/fallimenti/skipped. Le nuove prove usano
SDK ufficiali con HTTP simulato e Docker reale. Il riferimento dichiarato e' una
fixture, non il sorgente della prova Windows: il codice reale del PC non e' stato
trasmesso alla chat cloud. Rilevati e respinti backend difettosi. Verificati riuso
al limite senza nuove richieste, deduplicazione, protezione dei test, nessuna
ricreazione di test eliminati, conservazione del README e rispetto dei controlli.
Report completo: resources/evidence/pytest.xml. La nuova prova del modello reale
e l'applicazione di questa modifica su Windows restano da registrare localmente.
