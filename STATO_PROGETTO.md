# Stato progetto — Officina v0.2 (Groq)

Aggiornato il 14 ottobre 2026. Il nuovo obiettivo è usare il piano gratuito Groq,
con quote operative, senza passaggio automatico a servizi a pagamento.

### ZIP del progetto ordinario ricevuto: backend mancante, consegna separata

**Esito attuale sul PC: il backend separato funziona per creazione, consultazione
e persistenza dopo riavvio del container**, secondo i messaggi dell'utente.
Il comando docker run dall'immagine esistente ha restituito il container
bf60f3d1a45f66f9dd5124f36bb6f803a03681021b5ef72a3950072f9b38d2e5.
La pagina «Le mie attività» ha mostrato il database vuoto; l'utente ha salvato
«Prova di salvataggio», ricevuto «Attività salvata» e visto l'elemento nella lista.
Dopo `docker restart --time 2 officina-attivita-e32ae57b`, concluso con successo,
ha ricaricato la pagina con Ctrl+R e confermato «rimasta». L'avviso deprecated
sull'opzione --time non è un fallimento; usare --timeout nei prossimi comandi.
Validazione e idempotenza sono verificate in Docker Linux, non ancora provate
direttamente su Windows. Nuovi AVVIA/FERMA corretti non ancora applicati/provati
sul PC: **non fargli usare i vecchi batch come se fossero aggiornati**.

Il problema da risolvere rimane il progetto originale nell'assistente Officina,
non il backend separato. Esteso scripts/leggi_diagnosi.py con `--progetto ID`:
legge il DB principale e la storia di quel progetto, senza API, test, import o
esecuzione dei file generati; restituisce ricevute/somme hash delle scritture
main.py e motivi degli errori senza riportare il codice della storia. Chiavi
mascherate e rapporto nuovo in Blocco note, distinto dai rapporti CLI già passati.
**14 controlli diagnostici passati su Linux**, incluso DB principale distinto
dall'accettazione, DB invariati, ID invalidi respinti e apertura Notepad simulata.
Prossima azione: leggere il rapporto del progetto e32ae57b463c406381faa8efec493542
sul PC con questo nuovo helper; il vecchio helper Windows va prima scaricato
dalla revisione fissata. Aprire solo CMD con Win+R, poi incollare il lungo comando
nella finestra nera: NON incollare comandi lunghi nella casella Esegui.

Cronologia del problema iniziale di avvio della consegna:

Aggiornamento Windows successivo alla consegna: l'utente ha scaricato ed estratto
Backend-attivita.zip ed eseguito AVVIA.bat. Docker Desktop ha completato il build
di tutti i 10 passaggi in 5.6 secondi, compresi COPY --chown e immagine fissata.
Poi compare un solo ID Docker (944ee300…) e «Avvio non completato».
Il controllo successivo dell'utente conferma **No such container** per
`docker container inspect` e **bridge** per la rete. L'avvio si è fermato al
controllo della rete, prima di docker run. Trovato inoltre un errore nel ramo
di ripresa: `docker inspect` senza tipo trova la rete omonima e la scambia per
un container. Corretto AVVIA.bat con inspect specifico per container e rimosse
le pipe FINDSTR dai confronti di rete/label in AVVIA e FERMA: ora FOR /F legge
il valore, IF lo confronta. Aggiunti fase dell'errore e ultimi log del container.
Revisione Windows dei nuovi batch soltanto statica; esecuzione ancora da provare.
Non cancellare container, rete o volume e non fare ricostruzioni alla cieca.
Questa fase è superata dal successivo avvio diretto con docker run, descritto sopra.
L'utente chiede poche finestre aperte: riutilizzare la stessa CMD, Docker Desktop
ridotto a icona e questa chat. Non chiedere chiavi né ripetere la prova IA.

L'utente ha caricato `progetto-e32ae57b.zip`. Il rapporto identifica il progetto
`e32ae57b463c406381faa8efec493542`: 12 chiamate modello, 12 operazioni,
34765 token input, 7394 output, 677.437 secondi, 1 fonte consultata.
Contiene soltanto `tests/__init__.py`, `tests/test_api.py` e il rapporto;
**main.py manca**, `last_check=null`, `verified_hash=null`, zero verifiche
registrate. Non attribuire la causa della scrittura mancante al modello o al
controller senza leggere la storia. L'aggiornamento eecd1d6 sul PC non è ancora
confermato. Il suo controllo dei file non può far passare un programma mancante.

Completata una **consegna separata da Codex**, `examples/attivita_consegna`, dal
backend di riferimento dichiarato: main.py, pagina italiana per salvare/listare
attività, Dockerfile con base fissata e file AVVIA.bat/FERMA.bat. Nessuna API usata,
nessuna modifica al progetto o ai contatori sul PC. Non presentarla come risultato
autonomo dell'agente Groq. ZIP originale e test conservati come evidenza immutata.
I test originali dipendono dall'ordine (3 fallimenti eseguendoli al contrario su
backend valido); sostituiti nella sola consegna con 18 prove isolate e più ampie.
**18 test e 5 controlli indipendenti API passati in Docker senza rete**; anche tutti
i 18 test in ordine inverso passano. Smoke con immagine costruita, container non
root e volume reale: attività e idempotenza conservate dopo stop/start, browser
Chromium reale a 390px, salvataggio/ricarica, testo HTML non interpretato, zero
errori JavaScript. La pagina di prova usa una rete bridge dedicata con porta solo
loopback; può consentire traffico uscente. Le verifiche del codice restano senza
rete e senza mount host. File .bat non eseguiti su Windows, ancora da provare.

L'utente ha già scaricato, estratto e provato la consegna separata. La nuova
pagina si chiama «Le mie attività», distinta da Officina (porta 8766, Officina 8765).
Non fargli ricreare chiavi, aumentare budget o creare un altro obiettivo per questa
prova. Il flusso del progetto originale dentro Officina **rimane incompleto**.
Per correggerlo ulteriormente serve la sua storia/eventi, assenti dallo ZIP:
non usare la diagnosi CLI della copia di accettazione, che è un progetto diverso.

### Primo progetto dall'interfaccia Windows: limite richieste raggiunto

Il nuovo screenshot dell'utente mostra **Serve il tuo intervento — Limite di
chiamate IA raggiunto. Conservati tutti i risultati**, con file scaricabili.
È un progetto ordinario dell'interfaccia, distinto dalla prova di accettazione
già PASSATA. Tre progetti sono visibili nella lista; non crearne altri per riprovare.
Conteggi e ultima verifica ora ricevuti nello ZIP: vedere la sezione iniziale.
Il limite predefinito ordinario è 12; non attribuirlo alla quota del provider
e non aumentarlo automaticamente. Ultimo PID del servizio comunicato: 3668.

Corretto Agent.run: a limite modello raggiunto, conclude da prove già valide
oppure controlla i file esistenti in Docker, entro tempo/operazioni/correzioni,
senza altre richieste IA. Pronto richiede prove passate e hash corrente. Registra
il digest delle prove e non ripete automaticamente un fallimento sugli stessi
file; nessun reset di consumi o modifica dei test. Il messaggio «Prossimo passo»
durante il lavoro usa ora istruzioni italiane per l'utente; il piano tecnico
originale rimane nei dettagli. Evita che «Definire schema DB» sembri un compito
che l'utente deve svolgere.

**135 test passati su Linux**, zero errori/fallimenti/skipped. Sei nuovi casi
con Docker reale e SDK simulato che rifiuta qualsiasi richiesta: file validi
senza prove, prove già valide, file cambiati, input invalido, zero test e
fallimento invariato. Aggiornamento sul PC **ancora da applicare**; dopo
l'aggiornamento, Riprendi attiva il controllo del progetto selezionato.

### Osservazioni precedenti dell'interfaccia

Dopo l'accettazione passata l'utente ha aperto Officina e premuto Avvia:
riferisce un lampeggio senza un cambiamento visibile. Nessun errore o stato
della pagina ancora fornito: la causa sul PC **non è confermata**. Non ripetere
alla cieca l'avvio e non creare altri progetti o nuove prove di accettazione.
Verificato su Linux con Chromium reale: una sessione precedente viene rifiutata
con messaggio visibile; ricaricando la pagina si ottiene una sessione valida e
Avvia crea un solo progetto, zero errori JavaScript, zero chiamate IA (chiave
volutamente assente). Servizio di prova temporaneo arrestato, dati eliminati.
Esito locale in `.data/verification/ui-start-session.json`. Prossima azione sul
PC: ricarica con Ctrl+R e osserva la pagina; conserva il terminale aperto.

### Ultimo esito Windows: 14 ottobre 2026

**ACCETTAZIONE IA: PASSATA — Verifica agente: PASSATA.**

Il nuovo log dell'utente dopo l'aggiornamento alla revisione
899e0cb2319912ac211d869175aca00273c1b541 conferma la conclusione della prova
sul suo PC Windows, build 10.0.26300.9711. Sorgenti aggiornati con checksum e
backup, accesso Groq/modello verificato, prova senza IA superata, copia ripresa
senza reintrodurre il difetto e file ricontrollati in Docker. Le **20 richieste
già usate sono conservate**: nessuna nuova generazione per la conclusione.
L'IA aveva corretto il difetto della copia; la precedente correzione della porta
e la registrazione conclusiva sono interventi del sistema dichiarati nel registro.
I precedenti rapporti dettagliati mostrano 6 unittest nel backend e 7 nella copia.
L'ultimo log conferma l'esito complessivo, senza ripetere i conteggi dei test.

Officina è stata avviata; PID comunicato **3668**. Lasciare aperto il terminale
durante l'uso. **Non chiedere ulteriori rapporti né ripetere la prova già passata**
senza nuove modifiche o errori. Prossimo passo dell'utente: aprire la finestra di
Officina nel browser e iniziare un progetto. Percorso ordinario di avvio successivo:
`.venv\Scripts\python.exe scripts\avvio_automatico.py` dalla cartella del progetto,
che carica la chiave salvata e conserva dati e prove. Il pacchetto attuale include
anche avvio_automatico.bat; non presumere che sia presente nella vecchia copia
Windows aggiornata in precedenza scaricando soltanto il sorgente Python.
Nessun nuovo aggiornamento dell'app è richiesto per queste sole note di consegna.

### Cronologia precedente alla conclusione della prova

**Ultimo rapporto breve ricevuto:** la copia `f00000d61e0f4b019025cc9f62a0aaea`
ha rilevato il difetto, ricevuto una scrittura IA riuscita su regression_target.py
e superato **7 unittest, zero errori/fallimenti**, con `checks_passed=true`.
Originale e test invariati. Il modello ha poi risposto soltanto in testo
"Tutti i test passano…", senza chiamare finish. Il controller precedente ha
lasciato lo stato su Serve il tuo intervento e `corrected_and_retested=false`
pur avendo prove passate: è un difetto nella conclusione del flusso.
La copia ha usato 4 chiamate, 18917 token input e 422 output; con le 16 chiamate
di generazione il limite complessivo di 20 è già consumato. Il vecchio valore
used_tokens=12916 è la riserva precedente all'ultima risposta, non il consumo finale.

Corretto app/agent.py: dopo una risposta senza strumenti, il sistema registra
finish soltanto se piano, criteri, documentazione, verifiche passate e hash dei
file correnti sono presenti. Registra attore system e trigger separato dal
messaggio IA; nessuna fiducia nel solo testo di successo. Le prove mancanti,
fallite o invalidate continuano a impedire Pronto. Il percorso di ripresa già
esistente ricontrolla in Docker e conclude anche con budget di chiamate esaurito.
La conclusione automatica attende una pausa e rispetta Ferma, verificato con
due casi aggiuntivi. Suite finale del 14 ottobre: **129 passati** senza skipped.
Verificato su Linux con SDK reale/HTTP simulato e Docker reale, incluso il
caso 16+4 richieste e ripresa senza altre generazioni. **Applicazione del nuovo
controller e chiusura formale della prova sul PC ancora da confermare.**
Prossimo comando: aggiornamento mirato con PID comunicato 18028, limite 20
conservato; non creare nuove prove e non aumentare i budget.

L'utente ha riavviato il PC ed eseguito l'aggiornamento alla revisione
405a9e1e3f154bfe4c49080c713bc0e3c7f51ecf, senza il PID precedente. Il log
conferma checksum e backup, accesso Groq/modello, avvio Docker e prova senza IA
(riferimento, difetto rilevato, ripristino) superata. La procedura del sistema
per rilasciare la porta è stata applicata sul PC: **i file del backend hanno
superato le verifiche senza un'altra chiamata IA**. Non attribuire questa
correzione al modello Groq.

Il frammento RESULTS.json successivamente incollato conferma `generation.state`
Pronto, hash verificato, **6 unittest eseguiti, zero fallimenti/errori/skipped**,
16 chiamate e gli stessi 74968 token input/10486 output. Il testo incollato si
interrompe prima della sezione repair: non contiene la causa del nuovo arresto.

La copia della prova di correzione IA è stata creata e verificata, con fallimento
iniziale, poi il lavoro IA è proseguito. Esito complessivo ancora **NON COMPLETATA**.
Il log non include la causa dell'arresto della copia né i contatori finali;
non attribuirla a quota, budget o modello senza leggere il RESULTS.json aggiornato.
16 richieste già usate all'inizio, limite complessivo 20 conservato. PID attuale
del server comunicato dall'utente: **18028** (ricontrollarne l'identità prima
di qualunque arresto). Prossimo passo: leggere soltanto il rapporto in
`.data/live-acceptance/RESULTS.json`; nessuna nuova esecuzione o aumento dei limiti.

Aggiunta a scripts/leggi_diagnosi.py l'opzione `--correzione`: riepilogo breve
della copia da RESULTS.json e ultimi eventi via SQLite mode=ro, chiavi mascherate,
file diagnostico nuovo a ogni apertura in Notepad. Evita di copiare il rapporto
completo e le schede precedenti con modifiche non salvate. **8 controlli mirati
passati su Linux**; invocazione Notepad Windows simulata, nessuna API o esecuzione
di codice generato. A quel punto la suite completa era di 117 del 13 ottobre;
ora è stata rieseguita il 14: **129 passati**, zero fallimenti/errori/skipped.

### Situazione attuale: diagnosi Windows e correzione del riavvio

Il rapporto aggiornato dell'utente conferma che **main.py esiste** e che tutti
i **5 controlli indipendenti delle API passano**. Dei 6 unittest generati, 5
passano e quello del riavvio fallisce con `Address already in use`: il listener
precedente non viene rilasciato prima di creare il successivo sulla stessa porta.
16 richieste IA, 74968 token input e 10486 output, 3 verifiche fallite; contatori
conservati. L'ultima risposta del modello è un rifiuto testuale, senza strumenti;
la sua causa non è determinata. La riserva token del rapporto precede quell'ultima
risposta e non dimostra che il nuovo arresto sia dovuto al budget.

Predisposta una procedura del **sistema/Codex**, versione 1, che aggiunge
`server_close()` dopo `shutdown()` solo per questo errore riconosciuto e per
un'importazione standard non personalizzata di ThreadingHTTPServer. Nessun test
modificato, codice mai importato/eseguito sull'host, precedente main.py versionato
e ripristinabile. La procedura non viene attribuita al modello Groq.
Docker Linux ha riprodotto l'errore e poi superato gli stessi 9 test della fixture
e i 5 controlli API dopo la modifica; rollback verificato. Applicazione sul PC
Windows e nuova prova con il modello reale **ancora da confermare**.

La prova separata usa una copia, un contesto nuovo limitato al difetto deliberato,
piano e riferimenti ufficiali realmente preparati dal sistema. Il modello deve
scrivere la correzione; certificazione solo con difetto `test_strip` prima rilevato,
scrittura IA riuscita corrispondente al file finale, test invariati, nuove prove
passate e originale invariato. SDK reale con risposte HTTP simulate e Docker reale:
flusso passato con 3 chiamate della copia, 16 precedenti conservate (19 su 20).
Questa prova offline **non verifica le capacità dell'IA reale**. Nessun aumento
dei limiti token/tempo, nessuna nuova chiave richiesta, nessun ripiego a pagamento.
Il PID Windows più recente comunicato è 21380; usare soltanto il controllo mirato
del programma di aggiornamento, senza fermare tutti i processi Python.

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
La correzione è stata applicata sul PC Windows secondo il successivo log;
la prova ripresa è ancora NON COMPLETATA. Non dichiarare completata la
generazione finché non arrivano esiti effettivi positivi.
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

### Esito aggiornamento e seconda prova Windows

Il nuovo log conferma sorgenti aggiornati con checksum e copie precedenti,
profilo Groq applicato, installer Docker Desktop 4.95.0 scaricato con hash
verificato e "Installazione riuscita" da winget. Nessun riavvio imposto.
Accesso Groq/modello e prove del riferimento (backend, difetto, ripristino) sono
nuovamente passati. L'accettazione IA ha ripreso la generazione salvata, mantenendo
file, storia e contatori, ma è terminata con NON COMPLETATA. Il motivo dell'ultimo
arresto non compare nella coda incollata: leggere RESULTS.json della prova attuale
prima di attribuirlo alla quota o modificare i limiti. Il precedente 429 rimane
un risultato storico, non una diagnosi del secondo tentativo.
Il server riavviato riporta PID 12136; l'utente conferma apertura della pagina.
Non richiedere una nuova chiave, non azzerare i contatori e non dichiarare riuscita
la generazione o la correzione separata. I risultati Windows sono log dell'utente,
non comandi eseguiti dall'assistente nel cloud.

### Rapporto Windows letto e correzione del rifiuto HTTP 400

Il RESULTS.json incollato dall'utente identifica il progetto di generazione
4e61bd1e66894d04bb1993000a90a634, fermo per HTTP 400 dopo 8 chiamate IA e 6 tool.
Il precedente codice non conservava il dettaglio del rifiuto: la causa specifica
non è recuperabile da questo rapporto e non va attribuita con certezza al formato.
La consultazione documenti risulta ancora 0. L'ultimo run_checks è fallito prima
dell'esecuzione di unittest: "Start directory is not importable: tests".
La correzione separata non è stata avviata. Non mostrare Pronto.

Consultata la documentazione Groq attuale su tool calling, errori e quote.
Aggiunti diagnostica per categorie riconosciute, parametro/codice in lista consentita,
registro e rapporto della prova. Messaggi grezzi, failed_generation e argomenti
rifiutati non sono conservati o eseguiti. Solo gli errori di generazione tool
riconosciuti consentono una rigenerazione, con prompt corretto e temperatura più
bassa, al massimo una per progetto anche dopo Riprendi. Gli altri 400 fermano il
lavoro. Ogni richiesta rimane nel budget; nessun passaggio a un altro servizio.
La ripresa ricorda i documenti mancanti e le istruzioni includono tests/__init__.py
ed esame del risultato di ogni scrittura prima di presumere il file presente.

Per il prossimo comando Windows: --chiamate-prova 20 imposta un limite esplicito
COMPLESSIVO per generazione e correzione; conserva le 8 richieste già usate e
riserva anche quelle già consumate dalla copia separata. Non cambia .env o il
limite ordinario dell'app (12). I budget di token e tempo restano invariati.
L'arresto mirato riconosce anche il server avviato da aggiorna_quota.py; il PID
attuale è 12136, da ricontrollare con porta, script e proprietario prima dell'arresto.
Il nuovo ramo nativo Windows non è ancora stato eseguito dall'assistente.

Suite finale: **87 test passati su Linux**, zero fallimenti/errori/skipped,
compresi 16 nuovi controlli del rifiuto/recupero e del limite complessivo della prova.
SDK ufficiale con trasporto simulato; non convalida capacità del modello reale.
Nuovo avvio reale, pagina italiana, API, creazione progetto e stop per credenziale
assente verificati; zero chiamate IA, servizio di prova arrestato.
La correzione è pronta da applicare sul PC; generazione e correzione con IA
restano NON COMPLETE fino a risultati effettivi del PC Windows.

### Terza prova Windows: stop per riserva token

Il successivo comando completo nel Prompt è riuscito: sorgenti con checksum e
copie precedenti, credenziale/modello disponibili, riferimento/difetto/ripristino
nuovamente verificati. La generazione è ripresa con limite complessivo 20,
partendo da 8 chiamate già usate. Dopo vari cicli si è fermata per il controllo
locale "Budget token insufficiente per un'altra chiamata". Non è un nuovo errore
429 dimostrato. Il nuovo RESULTS.json conferma 14 chiamate, 12 tool, 60306 token input e 8853
output: 69159 usati, con 50841 residui prima della riserva. Documenti consultati 1;
l'ultimo check è ancora quello fallito prima dell'esecuzione dei test. Non compaiono
nuovi errori del provider in questo rapporto. Il server ora riporta PID 23792.
Il primo comando era incompleto (.venv\Scri); il successivo comando nel Prompt
è partito. Per evitare comandi lunghi nella finestra Esegui, usare Windows+R,
scrivere soltanto cmd, poi incollare il comando lungo dentro il Prompt.

Individuato un errore indipendente: il preflight prenotava byte/token di tutta
la cronologia persistente, anche codice che il messaggio Groq non reinviava.
La richiesta è ora costruita da un'unica funzione usata dall'SDK e dalla riserva,
con un margine prudente di 4096 e il massimo output. La memoria rimane integrale;
consumo effettivamente riportato e limite di 120000 token non vengono azzerati
o aumentati. OpenAI usa il proprio payload completo; scritture fallite restano
nel conteggio della richiesta. Un consumo realmente esaurito continua a fermare
le chiamate prima dell'SDK. Il rapporto distingue consumo, riserva e limite.

**91 test passati su Linux**, zero fallimenti/errori/skipped. Quattro nuovi casi
coprono vecchia prenotazione eccessiva, conservazione del consumo/cronologia,
payload specifici e stop su consumo esaurito; SDK con HTTP simulato, non prova IA.
Il rapporto aggiornato è stato ricevuto dopo aver semplificato il comando di
apertura del Blocco note. Non modificare .env alla cieca e non chiedere nuovamente
la chiave già salvata. La correzione è pronta, non ancora provata sul PC.

### Ripresa con verifica dei file salvati

Restano 6 delle 20 richieste complessive. Prima di chiamare di nuovo il modello,
la prova ricontrolla in Docker i file di un progetto interrotto con piano, criteri
e documentazione già acquisiti. Usa gli stessi run_checks e finish con hash e
controlli obbligatori. Se passano, certifica i file come verifica AUTOMATICA DEL
SISTEMA, senza fingere una nuova risposta del modello; il consumo IA resta invariato.
Se falliscono, conserva il risultato come dato non fidato per il modello e aumenta
il contatore di verifiche fallite. Il tempo viene conteggiato e sono rispettati
limiti di operazioni/correzioni. Zero test o contratto fallito non consentono Pronto.
La correzione separata resta una prova distinta, con difetto e nuova verifica.

**94 test passati nella suite finale Linux**, zero fallimenti/errori/skipped.
Tre nuovi casi con riferimento dichiarato, Docker reale e SDK HTTP simulato:
passaggio alla certificazione senza nuova API, zero test respinto e difetto di
validazione respinto prima di riprendere il modello. Non provano la qualità di una
nuova generazione IA. Il prossimo comando aggiorna i sorgenti, arresta soltanto
Officina dopo aver ricontrollato il PID 23792, conserva 14 richieste e 69159 token,
e mantiene 20 richieste totali/120000 token. Nessuna nuova chiave richiesta.

### Quarta prova Windows: verifica file fallita e nuovo stop token

Il log dopo c6ba62e conferma arresto mirato dell'istanza precedente, sorgenti
aggiornati con checksum, SDK/modello disponibili e riferimento/difetto/ripristino
verificati. La generazione riprende da 14 chiamate su 20. Il nuovo controllo in
Docker dei file salvati NON PASSA: nessuna certificazione automatica o Pronto.
La ripresa IA termina poi sul controllo token basato sul payload. Consumo, riserva
e ultimo errore dei file sono nel nuovo RESULTS.json, ancora da ricevere.
Non attribuire questo stop allo stesso errore di calcolo già corretto senza leggere
i numeri. Non aumentare limiti o azzerare contatori alla cieca. Server corrente
PID 11016. Nessuna reinstallazione o nuova chiave necessarie per leggere il rapporto.

### Errore concreto letto: main.py mancante

L'estratto nuovo del rapporto Windows mostra test_backend.py che importa main,
ma il file /work/main.py manca. Il contratto esterno non riesce ad avviare il
backend. Uso 78422 token; riserva input 40544 più output 3000: totale prudente
121966 contro 120000, eccedenza 1966. Tempo già usato 711.188 secondi, documenti
consultati 1. Numero corrente di chiamate non incluso nell'estratto: non inventarlo.

Aggiunto un recupero limitato della scrittura IA: solo main.py assente, mai
versionato, con piano/criteri/documenti presenti e limiti rispettati. Usa soltanto
l'ultima richiesta write_file per main.py con argomenti validi, il cui risultato
precedente era ESATTAMENTE il blocco sui prerequisiti. Non recupera negazioni di
sicurezza/dimensioni, esiti ignoti o file eliminati; non sovrascrive file esistenti.
Passa attraverso l'ordinario tool write_file e registra provenienza, hash e versione
ripristinabile. Il codice è quello della risposta archiviata, non un backend di
riferimento sostitutivo. L'originale risultato fallito resta nella cronologia.
La verifica successiva rimane in Docker, con test e contratto obbligatori.

La richiesta Groq non ripete corpi di scritture precedenti se una scrittura più
recente o un recupero documentato ha salvato quel file. Hash e ordine sono controllati;
le modifiche fallite più recenti restano nel contesto. OpenAI non riceve il campo
interno di provenienza. Il budget rimane 120000 token/20 richieste complessive.
Il rapporto ora include nomi dei file e scritture recuperate, senza contenuti o chiavi.

**104 test passati su Linux**, zero fallimenti/errori/skipped. Dieci nuovi casi:
recupero del riferimento dichiarato e 8 test/5 controlli in Docker reale senza nuova
API, rollback disponibile, rifiuti di ripristini indebiti, memoria preservata e
corpi superati omessi soltanto con provenienza verificata. Trasporto SDK simulato;
non convalida nuove capacità del modello reale. Il recupero sul PC deve ancora
essere tentato; se non esiste una richiesta archiviata idonea, non inventare main.py.
PID Windows corrente 11016, da ricontrollare prima del prossimo aggiornamento.

### Quinta prova Windows: risposta senza strumenti, diagnosi necessaria

Il log dopo 917f1e3 conferma arresto mirato, aggiornamento con checksum e prove
senza IA passate. Generazione ripresa da 15 chiamate; il recupero main.py non è
riportato. I file non passano il nuovo controllo e l'agente termina con testo
senza strumenti/certificazione. Il contenuto di questa risposta e il nuovo errore
non sono ancora disponibili. PID del server corrente 21380.
L'errore main.py mancante apparteneva a un controllo precedente a una nuova
scrittura: non trattarlo come prova dello stato attuale senza inventario aggiornato.

Aggiunto scripts/leggi_diagnosi.py: legge SQLite in mode=ro, file attuali, firma
sintattica dei moduli senza importarli, ultime operazioni/errori e ultimo messaggio
IA. Non chiama API, non esegue test o codice generato, non cambia il database o i
file del backend e non ferma Officina. Produce soltanto un rapporto diagnostico
nuovo e su Windows lo apre nel Blocco note. Non legge il vault delle credenziali;
maschera schemi di chiavi e salta collegamenti simbolici del workspace.
**4 test indipendenti passati su Linux**: dati/file invariati, nessuna esecuzione
del codice del progetto, rifiuto riferimenti esterni, output Windows nuovo e
argomenti Notepad simulati. La suite funzionale resta quella effettiva di 104;
non dichiarare una nuova suite completa 108 eseguita.
Il prossimo comando serve solo a raccogliere questa diagnosi. Non rilanciare
ancora l'accettazione o aumentare limiti prima di leggere lo stato corrente.

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

- **135 test passati** nella suite corrente, 0 errori/fallimenti/skipped.
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
Sul **PC Windows** accesso, modello e accettazione generazione/correzione sono
confermati dai rapporti e dal log finale PASSATA del 14 ottobre. Conservare
l'attribuzione della correzione della porta al sistema e del difetto separato
al modello. Le procedure riutilizzabili con il modello reale restano da provare.
Non richiedere nuovamente una chiave locale già salvata; usare avvio_automatico
che carica il file fuori OneDrive. Il flusso completo del browser su Windows
resta distinto dalla prova automatica passata; non è stato verificato da remoto.

Il piano Free e le quote non sono rilevabili affidabilmente dall'app. L'utente deve
controllarli nella console Groq; non è garantito accesso illimitato o assenza di
addebiti se l'account ha già fatturazione attiva. Nessun cambio automatico a OpenAI.

Windows 11: setup, casella, SDK/modello, Docker, prova senza IA e avvio server
confermati da log dell'utente. Correzione della quota applicata e aggiornamento Docker
riuscito secondo il log; chiusura del server corretta, difetto separato corretto
con IA e accettazione finale **PASSATA** secondo il log Windows del 14 ottobre.
Le verifiche eseguite direttamente dall'assistente restano su Linux, 129 passate.
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
4. Sul PC Windows la chiave è già salvata: usare avvio_automatico per caricarla.
   Soltanto se manca, configurarla localmente; mai chiedere valori in chat.
   Nel cloud la chiave resta assente: impostazioni sicure dell'ambiente per
   GROQ_API_KEY soltanto se si richiede una prova live anche in quell'ambiente.
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
