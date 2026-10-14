# Ripresa di Officina sul PC dell'utente

Nella sessione precedente l'utente ha chiesto lavoro autonomo sui file e sui
processi necessari al progetto, istruzioni italiane e una sola decisione alla volta.
Ridurre i comandi da copiare. Questo documento trasferisce il contesto: la nuova
sessione deve avere l'incarico dell'utente e le proprie autorizzazioni effettive.
Ispezionare il progetto prima di agire.

Codex CLI 0.161.0 è già installato sul PC Windows tramite il pacchetto
OpenAI.Codex di WinGet, ambito utente. Il log dell'utente conferma hash verificato,
installazione riuscita e alias codex aggiunto. Usare questa sessione locale per il
lavoro; il contesto precedente nella chat rimaneva su una macchina cloud distinta.

## Ambito e dati

Lavorare nella cartella Windows
`%USERPROFILE%\OneDrive\Desktop\OFFICINA\AI-HyperGenius-main`.
Conservare codice, `.data`, `.env`, cronologia e progetti esistenti. Non enumerare
file personali estranei né riportare chiavi o credenziali nei messaggi o nei log.
La chiave Groq è già configurata sul PC: avvio_automatico.py la carica localmente
da `%LOCALAPPDATA%\Officina\credentials.env`. Non richiederla di nuovo e non
leggerla con gli strumenti del modello; avviare gli script già predisposti.
Usare il sandbox dell'agente locale e limitare gli accessi alla cartella progetto.
Non disattivare verifiche TLS, checksum o controlli di sicurezza per procedere.
Non accedere a denaro/portafogli, inviare messaggi, pubblicare il prodotto o usare
repository di Nodveta. GitHub conserva il codice, non è il runtime Windows.

## Stato verificato

Repository remoto: https://github.com/piotr0868/AI-HyperGenius, branch main.
Ultima modifica del controller pronta sul cloud:
`f91612f60773c836926419a6282b4331b8a9e55c`.
148 test passati su Linux, zero errori/fallimenti/skipped. SDK ufficiale nei test,
HTTP simulato e Docker reale: nessuna inferenza reale fatta dal cloud.
L'applicazione di questa revisione al PC non è ancora confermata.

Il progetto dell'interfaccia da riprendere è
`e32ae57b463c406381faa8efec493542`, nella memoria principale `.data/memory.sqlite3`.
12 chiamate modello e 12 operazioni consumate; 34765 token input e 7394 output,
677.437 secondi, 1 fonte consultata. main.py manca: la richiesta originale di
scrittura (4485 caratteri, SHA256
601af0b8f715094a50decf7cd208ae3bb2c51988cd66edd400e54dd5769a800e)
fu respinta perché la documentazione non era ancora stata consultata. La
consultazione riuscì dopo, ma l'agente consumò le richieste riscrivendo i test.
Quel codice esiste nella storia locale; non è stato trasmesso al cloud.

La modifica f91612f porta nella UI il recupero protetto già usato dalla prova CLI:
ripete esattamente quella scrittura, con versione/rollback e attribuzione al
sistema, soltanto se piano/criteri/documentazione sono presenti e il file non è
mai stato salvato/eliminato intenzionalmente. Conserva limiti e contatori e
controlla in Docker. Nessuna nuova generazione per la ripresa a 12 chiamate.
Pronto dipende dalle prove reali sui file correnti, non da una risposta del modello.
Il codice originale sul PC potrebbe avere difetti: va realmente verificato.

La prova di accettazione CLI separata è già PASSATA su Windows, con 20 richieste
complessive conservate. Non confonderla col progetto UI. Non ricreare la prova,
non reintrodurre il difetto della copia e non azzerare/aumentare i budget.

Esiste anche un backend separato completato da Codex, non dal modello Groq:
container `officina-attivita-e32ae57b`, porta locale 8766, volume
`officina-attivita-e32ae57b-dati`. L'utente ha verificato pagina, salvataggio di
«Prova di salvataggio» e permanenza dopo docker restart e ricarica. Conservarlo.
I vecchi AVVIA.bat/FERMA.bat di questa consegna avevano un difetto; le versioni
corrette sul repository non sono ancora confermate sul PC. Non dichiararle provate.

## Lavoro da completare autonomamente

1. Ispezionare il progetto e le istruzioni AGENTS.md disponibili, senza sovrascrivere
   modifiche dell'utente. Il progetto Windows potrebbe essere uno ZIP senza .git.
2. Controllare se la revisione f91612f è applicata. Lo script esistente
   scripts/aggiorna_quota.py aggiorna quattro file da una revisione fissata,
   verifica checksum/sintassi e salva copie precedenti. Non tocca chiavi o memoria.
   Il limite --chiamate-prova 20 riguarda la sola prova CLI già passata; la UI
   conserva il limite ordinario di 12. Evitare nuove generazioni a pagamento.
3. Gestire solo il processo Officina identificato (porta 8765 e relativo percorso),
   senza arrestare genericamente Python o Docker. Il backend sulla 8766 è distinto.
   Avviare scripts/avvio_automatico.py, così carica la credenziale già presente.
4. Riprendere lo stesso progetto UI e verificare recupero e prove in Docker. Non
   creare un altro obiettivo e non sostituire il main recuperato con la fixture di
   riferimento. Controllare il rapporto effettivo, i contatori e i test eseguiti.
5. Se il sorgente reale non passa, leggere gli errori e correggere l'implementazione
   in modo versionato, attribuendo gli interventi all'agente locale/Codex. Conservare
   i test e usare il contratto API indipendente; nessuna esecuzione del codice
   generato sull'host. Non dichiarare successo senza prove passate e hash corrente.
6. Completare istruzioni e avvio semplice, verificare le modifiche necessarie sul
   vero Windows, aggiornare STATO_PROGETTO.md e riferire risultato/problemi/prossimo
   passo in italiano. Chiedere soltanto credenziali/autorizzazioni indispensabili
   realmente mancanti, attraverso l'interfaccia locale, mai segreti nella chat.

La nuova sessione locale è distinta dalla precedente chat cloud. Questo documento
trasferisce il contesto; non attribuisce alla chat cloud accesso remoto al PC e
non garantisce assenza di elaborazione del contesto da parte del servizio IA.
