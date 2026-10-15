# Ripresa di Officina sul PC

Aggiornato il 15 ottobre 2026. L'utente vuole lavoro autonomo: descrivere il
risultato in italiano e lasciare all'agente pianificazione, decisioni tecniche,
file, prove e correzioni. Ha gia' autorizzato le operazioni necessarie al progetto.
Leggere AGENTS.md e lo STATO_PROGETTO.md locale prima di agire. Ridurre le
richieste all'utente alle sole informazioni o autorizzazioni indispensabili
realmente mancanti. Non chiedere riconferme per il lavoro ordinario autorizzato.

## Priorita' attuale: recuperare il lavoro locale senza ricominciare

Leggere resources/INCARICO_E_RIPRESA_OFFICINA.md. L'obiettivo e' un assistente
backend/blockchain per richieste diverse; il backend attivita' e' soltanto una
prova. Il Codex Windows avrebbe lavorato circa cinque ore sul nuovo mandato.
Queste modifiche non sono disponibili nella copia cloud: ispezionare prima lo
stato locale, conservarlo e non sostituirlo con i vecchi sorgenti del repository.

La cronologia e gli archivi di Codex risultano sani secondo Doctor. Il blocco
segnalato e' il provisioning del sandbox elevated con helper_unknown_error;
non trattarlo come prova di memoria cancellata. WinGet non offre ancora la
0.162.1 segnalata da Doctor. Il successivo setup amministrativo ufficiale
della 0.161.0 e' riuscito per melon in C:\Users\melon\.codex secondo il log
ricevuto. Riaprire Codex con l'account ordinario, nella cartella del progetto,
e verificare la lettura dei file. Ripresa operativa e recupero dopo riavvio
Windows restano da verificare sul PC.

Una volta ripristinati gli strumenti, recuperare richieste e autorizzazioni
dalla cronologia locale, aggiornare checkpoint e registro delle decisioni e
continuare dal primo requisito incompleto. Non chiedere all'utente di
ricostruire il mandato. Distinguere permessi tecnici temporanei e consenso
persistente; non tentare di aggirare controlli o convertire il consenso in
accesso illimitato. Le sezioni successive descrivono prove storiche.

## Ambiente e dati

- Repository: https://github.com/piotr0868/AI-HyperGenius, branch main.
- Cartella Windows: `%USERPROFILE%\OneDrive\Desktop\OFFICINA\AI-HyperGenius-main`.
  Puo' provenire da uno ZIP senza Git: ispezionarla e preservare modifiche locali.
- Python 3.12 e .venv installati; Docker Desktop con container Linux gia' usato
  con successo. Codex CLI 0.161.0 installato tramite OpenAI.Codex/WinGet, accesso
  ChatGPT riuscito e lavoro locale avviato. Il flag verificato della versione
  e' --approve-for-me (revisione automatica con sandbox), non --full-auto.
- La chiave Groq e' gia' configurata fuori da OneDrive, in
  `%LOCALAPPDATA%\Officina\credentials.env`. Riutilizzare il caricamento locale
  di scripts/avvio_automatico.py; non leggerla con gli strumenti del modello,
  non stamparla e non richiederla in chat. Conservare .env, .data e cronologia.
- Non enumerare dati personali estranei, non disattivare sandbox/TLS/firme e
  non usare Nodveta, denaro, portafogli, invii a clienti o pubblicazioni automatiche.
- Eseguire il codice generato soltanto nel sandbox Docker di Officina, senza
  rete, cartelle personali, segreti o socket Docker. Il codice dell'assistente
  e i relativi controlli di sviluppo possono essere eseguiti nell'ambiente host.

## Stato effettivo gia' riportato dal PC

Il progetto UI **e32ae57b463c406381faa8efec493542**, in `.data/memory.sqlite3`,
e' **Pronto**: 5 test e controlli API/validazione/idempotenza/persistenza passati.
La foto dell'utente mostra questo esito nell'interfaccia. Il Codex locale ha
confermato l'hash corrente uguale al rapporto salvato. Il precedente main.py
mancante e' stato recuperato: non trattarlo ancora come assente e non ricreare
quel progetto. Contatori e file vanno conservati.

La prova CLI separata e' gia' **PASSATA**: generazione e correzione nella copia,
20 richieste complessive conservate. Non ricrearla o reintrodurre il difetto.

Esistono backend distinti da conservare:
- Porta 8766: consegna scritta da Codex, container officina-attivita-e32ae57b,
  volume officina-attivita-e32ae57b-dati. L'utente ha provato salvataggio e
  permanenza di "Prova di salvataggio" dopo docker restart e ricarica.
- Porta 8767: progetto verificato con AVVIA_PROGETTO_VERIFICATO.bat, avvio/riuso
  e HTTP 200 verificati dal Codex locale. /activities puo' mostrare JSON `[]`:
  e' una lista vuota, non l'interfaccia dell'assistente.

Il collegamento principale corretto e' **Apri Officina** sul Desktop, verso
APRI_OFFICINA.bat nella cartella progetto. Il Codex locale l'ha gia' applicato
e ha verificato HTTP/HTML e riuso del server su 8765. La finestra del server
deve restare aperta durante l'uso. Non far scaricare nuovamente ZIP o ricopiare
comandi tecnici all'utente per passaggi che l'agente puo' completare.

Il controllo computer-use di Chrome ha avuto un blocco per identificazione
incerta dell'URL anche dopo il permesso all'app. Rispettarlo e distinguere
visione automatica non eseguita, foto fornita dall'utente e prove HTTP/HTML.
Non eludere il blocco o chiedere altre foto per controlli che non sono visivi.

## Ultima prova reale: riuscita su Windows

Il successivo rapporto del Codex locale, incollato dall'utente il 14 ottobre
2026, conferma aggiornamento applicato con checksum e backup e **82 test Windows
passati**. La nuova prova reale con Groq e' **Pronto**, con **8 chiamate su 12**:
il modello ha corretto il backend dopo gli errori; cinque test e contratto
indipendente superati in Docker. I test di base sono attribuiti al sistema,
l'implementazione e le correzioni al modello.

Dati, credenziali, limiti e progetti precedenti, inclusa la prova negativa,
sono conservati secondo il rapporto. Il Codex locale ha aggiornato stato e
istruzioni e riaperto Officina. Usare **Apri Officina**: non ripetere installazione
o prove di regressione per il semplice avvio. Leggere prima lo stato locale per
gli ID, i contatori e gli hash effettivi: il riepilogo trasmesso alla chat cloud
non li contiene. Non confondere questa prova reale con le fixture Linux e non
considerarla una garanzia per altri programmi. Procedere dal prossimo obiettivo
dell'utente senza rimettergli la gestione tecnica.

## Cronologia della correzione delle scritture ripetute

Il Codex locale ha applicato 2d18bd2 con backup/checksum e riportato 55 test
Windows passati con Docker reale. La nuova prova Groq si e' fermata a 12
richieste: main.py riscritto senza creare test, verifica fallita. L'autonomia
reale di quella versione non e' dimostrata. ID e sorgente della prova sono nella
memoria e nello stato locali, non nel rapporto trasmesso alla chat cloud.

app/agent.py ora verifica e prosegue automaticamente quando il modello conclude
in testo senza file o prove completi. Conclude soltanto da prove passate e hash
corrente; evita prove fallite duplicate sui file invariati; rispetta domande
indispensabili, Pausa/Ferma e tutti i budget, senza reset o aumenti.
AGENTS.md conserva il mandato di autonomia per Codex. La prima versione
dell'agente resta specializzata nel backend attivita' Python del contratto.

Il nuovo app/progress.py recupera lo stallo delle scritture ripetute: prepara
una base dichiarata di cinque test HTTP quando mancano, senza cambiare il
backend o sostituire test esistenti/rimossi. README e package solo se mancanti.
Autore del sistema e hash registrati, base protetta; prove subito in Docker e
rapporto al modello per correggere il backend. Una scrittura identica non crea
versioni o invalida prove valide. Nessun reset o aumento dei limiti.

**183 test passati su Linux**, zero errori/fallimenti/skipped. Le nuove prove
coprono recupero a 12 chiamate senza inferenza, backend valido e difettoso,
scritture ripetute, protezione dei file e controlli. SDK HTTP simulato, Docker reale:
nessuna nuova inferenza reale sul cloud. Non attribuire questi esiti a una nuova
prova con il modello sul PC.

resources/RISOLVI_CICLO_SCRITTURE_PC.md documenta l'applicazione mirata e la
singola nuova prova reale richieste dopo la precedente prova negativa. Il
rapporto Windows successivo ne conferma l'esito riportato sopra: non rilanciare
quelle istruzioni come se l'aggiornamento fosse ancora da applicare. Conservare
entrambi gli esiti e l'attribuzione dei file. Un eventuale futuro blocco di quota
resta un esito non completato, senza reset o aumento automatico dei budget.

La sessione locale e' distinta dalla chat cloud che ha preparato questo file.
Il documento trasferisce contesto, non concede accesso remoto al PC alla chat
cloud e non garantisce assenza di elaborazione dei dati da parte del servizio IA.
