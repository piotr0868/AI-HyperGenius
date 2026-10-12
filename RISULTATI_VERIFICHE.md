# Risultati della consegna

Verifica finale del 12 ottobre 2026, su **Linux**, Python 3.12.14, Docker 28.4.0,
Chromium di sistema. I risultati completi sono in `resources/evidence/`.

| Prova | Esito effettivo |
| --- | --- |
| Suite applicazione pytest | **35 passati**, 0 falliti, 0 errori, 0 skipped |
| Backend di riferimento in Docker | **8 test passati**, 0 falliti, 0 skipped |
| Contratto esterno backend | **5 verifiche passate**: creazione, consultazione, input, idempotenza, riavvio |
| Errore deliberato in una copia | **Rilevato**: 3 fallimenti unitari e input invalido accettato; non dichiarato Pronto |
| Ripristino del riferimento | **8 test e 5 verifiche nuovamente passati**; ripristino deterministico, senza IA |
| Protocollo SDK → file → Docker → correzione → nuove prove | **Passato offline**: SDK e Docker reali, risposte del provider predisposte dal test |
| Isolamento Docker | **Passato**: utente 65534, nessuna credenziale/mount host/socket Docker, rete esterna bloccata, filesystem di sistema non scrivibile |
| Timeout e cleanup container | **Passato**: processo interrotto e container eliminato |
| Memoria, percorsi e versioni | **Passati**: riapertura DB, recupero, rifiuto traversal/symlink, rollback e invalidazione prove |
| Limiti e controlli | **Passati offline**: budget prima della chiamata, pausa tra operazioni, cancellazione di una richiesta attiva, utilizzo persistente |
| Procedure | **Passati i controlli locali**: versionamento, blocco adozione senza prove, requisiti degli esempi |
| Browser | **Passato**: italiano, obiettivo, credenziale assente → intervento, ricarica, documenti persistenti, layout 390px, nessun errore JavaScript |
| Riavvio reale dell’assistente | **Passato**: processo arrestato e riavviato, progetto ritrovato e API locali verificate |
| Installazione uv bloccata | **Passata e ripetibile** tramite `scripts/install_cloud.sh` |
| Installazione pip separata con `--require-hashes` | **Passata su Linux**, import FastAPI/OpenAI/uvicorn verificati |
| Sintassi Python e JavaScript | **Passata**; verifiche supplementari, non sostituiscono le prove funzionali |
| Generazione e correzione con OpenAI reale | **NON ESEGUITA**, exit code 2: manca `AI_PROVIDER_KEY`; zero chiamate live |
| Prova di procedure con OpenAI reale | **NON ESEGUITA**, stessa credenziale mancante |
| Windows 11 / Docker Desktop / file .bat | **NON ESEGUITI**: predisposti, da provare sul PC Windows |
| Nuovo task cloud e pubblicazione | **NON VERIFICATI**: bozza salvata, pubblicazione a cura dell’utente |

Le risposte simulate compaiono soltanto nei test del protocollo. L’applicazione usa
sempre l’SDK OpenAI: nessuna sostituzione con risposte prestabilite in produzione.
Il backend di riferimento è scritto per questa consegna e dichiarato come tale.

La suite ha rilevato e permesso di correggere una regressione transitoria nel commit
delle transazioni SQLite introdotta durante la gestione delle connessioni. Il report
finale registra l’ultima esecuzione, senza ignorare o indebolire gli assert.

Configurazione cloud persistita: `install_script`, `start_skill`, requisito personale
`AI_PROVIDER_KEY` per `api.openai.com` e domini ufficiali di documentazione. Bozza
confermata dal servizio. Nessun valore di credenziale è stato salvato nel codice,
nel pacchetto o nei report. **Revisionare e salvare nelle impostazioni, poi pubblicare**
restano azioni dell’utente e non sono state eseguite dall’assistente.
