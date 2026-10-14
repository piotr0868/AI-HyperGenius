# Risultati della consegna

Suite rieseguita il 14 ottobre 2026, su **Linux**, Python 3.12.14, Docker 28.4.0,
Chromium di sistema. I risultati completi sono in `resources/evidence/`.
Le prove precedenti di browser, riavvio, installazione e riferimento con difetto
restano quelle del 12 ottobre; il nuovo avvio è stato verificato il 13, la suite il 14.

**Windows, 14 ottobre: ACCETTAZIONE IA PASSATA e Verifica agente PASSATA**, secondo
il log finale dell'utente sulla revisione 899e0cb. Conclusione dopo ricontrollo
dei file salvati, senza nuove generazioni e con le 20 richieste conservate.
La correzione della porta e la certificazione sono del sistema; il modello reale
ha corretto il difetto nella copia separata. Non è una prova interamente autonoma
né una verifica di ogni futuro programma; l'esito riguarda il contratto attività.

| Prova | Esito effettivo |
| --- | --- |
| Suite applicazione pytest | **129 passati**, 0 falliti, 0 errori, 0 skipped |
| Nuovo avvio automatico | **12 controlli passati su Linux**, API simulate: protezione chiave, posizione fuori dal progetto, annullamento, blocco su errori, tentativi limitati, prove perse/modificate invalidate |
| Avvio automatico → applicazione e API locali | **Passato su Linux** dopo annullamento chiave, nessuna chiamata IA; interfaccia italiana e risposta salute effettive |
| Backend di riferimento in Docker | **8 test passati**, 0 falliti, 0 skipped |
| Contratto esterno backend | **5 verifiche passate**: creazione, consultazione, input, idempotenza, riavvio |
| Errore deliberato in una copia | **Rilevato**: 3 fallimenti unitari e input invalido accettato; non dichiarato Pronto |
| Ripristino del riferimento | **8 test e 5 verifiche nuovamente passati**; ripristino deterministico, senza IA |
| Protocollo SDK Groq/OpenAI → file → Docker → correzione → nuove prove | **Passato per entrambi offline**: SDK e Docker reali, risposte del provider predisposte dal test |
| Isolamento Docker | **Passato**: utente 65534, nessuna credenziale/mount host/socket Docker, rete esterna bloccata, filesystem di sistema non scrivibile |
| Timeout e cleanup container | **Passato**: processo interrotto e container eliminato |
| Memoria, percorsi e versioni | **Passati**: riapertura DB, recupero, rifiuto traversal/symlink, rollback e invalidazione prove |
| Limiti e controlli | **Passati offline**: budget prima della chiamata, pausa tra operazioni, cancellazione di una richiesta attiva, utilizzo persistente |
| Procedure | **Passati i controlli locali**: versionamento, blocco adozione senza prove, requisiti degli esempi |
| Browser | **Passato**: italiano, obiettivo, credenziale assente → intervento, ricarica, documenti persistenti, layout 390px, nessun errore JavaScript |
| Riavvio reale dell’assistente | **Passato**: processo arrestato e riavviato, progetto ritrovato e API locali verificate |
| Installazione uv bloccata | **Passata e ripetibile** tramite `scripts/install_cloud.sh` |
| Installazione pip separata con `--require-hashes` | **Passata su Linux**, dipendenze Groq incluse; import SDK verificati |
| Sintassi Python e JavaScript | **Passata**; verifiche supplementari, non sostituiscono le prove funzionali |
| Generazione e correzione con Groq reale nel cloud | **NON ESEGUITA**, exit code 2: manca `GROQ_API_KEY`; zero chiamate live dal cloud |
| Primi tentativi sul PC Windows, prima del successo finale | **Log storici dell'utente**: accesso al modello riuscito; prima generazione interrotta da HTTP 429, poi HTTP 400, poi riserva token locale. Errori conservati nella cronologia; prova successivamente conclusa e passata |
| Correzione quota e ripresa | **Controlli locali passati**: testo ridotto senza perdere memoria, attesa breve limitata e persistente, nessun nuovo difetto dopo ripresa, progetti pronti ricontrollati in Docker; correzione applicata e prova ripresa secondo il log Windows; accettazione ancora incompleta per HTTP 400, dettaglio originario non registrato |
| Rifiuto HTTP 400 e rigenerazione tool | **9 nuovi test passati nella suite Linux**, SDK ufficiale con HTTP simulato: diagnostica senza segreti, una sola rigenerazione riconosciuta, altri 400 fermano il lavoro, richieste contate; modello reale sul PC ancora da verificare |
| Limite complessivo della prova | **7 nuovi controlli passati**: opzione esplicita valida, invalidi rifiutati senza chiamate, contatori/token/tempo conservati, budget condiviso e consumi precedenti della copia riservati |
| Riserva token basata sulla richiesta SDK | **4 nuovi casi passati su Linux**: memoria originale preservata, storico non reinviato escluso dalla riserva, limiti invariati, consumo esaurito blocca API; rapporto Windows letto: 69159 token usati, nuova riserva ancora da applicare |
| Verifica dei file prima della ripresa IA | **3 casi passati con Docker reale e SDK simulato**: riferimento certificato senza ulteriore API, zero test e input invalido respinti; contatori preservati e tempo conteggiato |
| Recupero scrittura IA bloccata | **10 nuovi casi passati su Linux**: solo main.py assente e mai versionato da richiesta bloccata sui prerequisiti; codice esatto, versione/rollback, verifiche in Docker e nessuna nuova API nel caso valido; Windows ancora da provare |
| Diagnosi del progetto senza IA | **4 controlli passati nella suite Linux**: database e file invariati, codice analizzato senza import/exec, riferimenti esterni rifiutati, mascheramento chiavi, invocazione Notepad simulata |
| Diagnosi breve della copia, 14 ottobre | **8 controlli passati su Linux**, inclusi nella suite: selezione della copia, contatori/motivo/operazioni pertinenti, database e file invariati, nessuna importazione/esecuzione del codice generato, chiavi mascherate, copia non avviata e riferimenti invalidi gestiti, apertura Notepad simulata. Rapporto ricevuto dal PC |
| Rapporto finale Windows, 14 ottobre | **ACCETTAZIONE IA PASSATA, Verifica agente PASSATA** dal log dell'utente. Backend verificato dopo la procedura del sistema; copia corretta dal modello e ricontrollata. Rapporti dettagliati precedenti: 6 unittest originali e 7 nella copia, nessun errore. Tutte le 20 chiamate conservate, zero nuove generazioni per concludere; PID comunicato 3668 |
| Diagnosi reale Windows del 13 ottobre | **5 controlli API passati**, **5 di 6 unittest passati**; errore di riavvio `Address already in use`. main.py presente. 16 chiamate IA, 85454 token usati; ultima risposta del modello: rifiuto testuale, causa sconosciuta. Accettazione completa ancora incompleta |
| Procedura di chiusura server del sistema | **9 nuovi controlli passati su Linux**: difetto della porta riprodotto in Docker, implementazione corretta senza modificare test, 9 unittest e 5 API passati, rollback, nessuna esecuzione del codice sull'host, strutture non riconosciute rifiutate |
| Prova separata dopo correzione del sistema | **Passata offline**: SDK Groq reale con risposte HTTP simulate e Docker reale; 10 unittest e 5 API passati, originale e test invariati; sia finish esplicito sia testo finale gestiti. **Passata anche sul PC con modello reale**, confermata dal log dell'utente, con interventi del sistema attribuiti |
| Conclusione dopo messaggio finale | **6 nuovi casi passati nella suite Linux**: successo registrato solo con piano, fonti, prove e hash valido; messaggi di successo con prove mancanti/fallite o file modificati non certificano. SDK simulato e Docker reale riproducono scrittura → lettura → verifiche → testo finale |
| Pausa e Ferma alla conclusione | **2 ulteriori casi passati nella suite Linux**: pausa richiesta durante la risposta finale impedisce di registrare Pronto; Riprendi permette la conclusione e Ferma la impedisce, senza nuove chiamate al modello |
| Ripresa con tutte le 20 chiamate usate | **Passata con Docker reale** nella prova integrata: consumi conservati, nuove prove e conclusione senza chiamate al modello. **Confermata dal log Windows** dopo aggiornamento alla revisione 899e0cb |
| Avvio dopo correzione HTTP 400 | **Passato su Linux**: pagina italiana, API, Docker disponibile, creazione progetto e credenziale assente dichiarata; limite ordinario app ancora 12, zero chiamate live |
| Aggiornamento con checksum e copie precedenti | **Passato offline**: rifiuto checksum errato prima di modifiche, chiave conservata, sorgenti precedenti archiviati, app attiva impedisce l'aggiornamento |
| Prova di procedure con Groq reale | **NON ESEGUITA**, stessa credenziale mancante |
| Quota Groq HTTP 429 | **Passato offline**: stop, indicazione Retry-After, nessuna chiamata a OpenAI |
| Credenziali separate e cronologia preesistente | **Passato**: la chiave OpenAI non viene usata per Groq; chiamate e risultati preservati |
| Configurazione locale della chiave | **Passata su Linux con chiave fittizia**: input non stampato, chiave precedente preservata, permessi 0600 |
| Accesso/modello e piano Free Groq | **Accesso/modello confermati dal log Windows**. Piano Free e fatturazione non rilevabili dal controllo: quote da consultare nell'account |
| Windows: Python e dipendenze | **Confermati dal log dell'utente**: Python 3.12.10, venv e installazione completata; non eseguiti dall'assistente |
| Windows: casella grafica, salvataggio chiave, Docker Linux, API e server | **Confermati dal log dell'utente**, inclusa prova senza IA e avvio server; apertura pagina Officina confermata dall’utente, flusso completo ancora da verificare |
| Aggiornamento Docker Desktop sul PC | **RIUSCITO secondo il log Windows**: winget, Docker Desktop 4.95.0, hash installer verificato; non eseguito dall'assistente |
| Nuovo task cloud e pubblicazione | **NON VERIFICATI**: bozza salvata, pubblicazione a cura dell’utente |

Le risposte simulate compaiono soltanto nei test del protocollo. L’applicazione usa
gli SDK ufficiali del fornitore scelto (Groq predefinito, OpenAI opzionale): nessuna sostituzione con risposte prestabilite in produzione.
Il backend di riferimento è scritto per questa consegna e dichiarato come tale.

La suite ha rilevato e permesso di correggere una regressione transitoria nel commit
delle transazioni SQLite introdotta durante la gestione delle connessioni. Il report
finale registra l’ultima esecuzione, senza ignorare o indebolire gli assert.

Configurazione cloud persistita: `install_script`, `start_skill`, requisito personale
`GROQ_API_KEY` per `api.groq.com`, variabili AI_PROVIDER/GROQ_MODEL e domini di
documentazione inclusa console.groq.com. La precedente opzione OpenAI è conservata. Bozza
confermata dal servizio. Nessun valore di credenziale è stato salvato nel codice,
nel pacchetto o nei report. **Revisionare e salvare nelle impostazioni, poi pubblicare**
restano azioni dell’utente e non sono state eseguite dall’assistente.
