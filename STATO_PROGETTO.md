# Stato progetto — Officina v0.1

Aggiornato il 12 ottobre 2026. Il repository iniziale era vuoto, senza commit o branch
remoti. È stata creata una nuova applicazione nella cartella esistente conservando
i metadati Git; non è stato eliminato alcun repository GitHub o ambiente cloud.

## Obiettivo del primo traguardo

Assistente personale in italiano per un backend attività Python, con memoria
persistente, pianificazione, documentazione, file versionati e verifiche Docker.
Architettura: FastAPI, SQLite/FTS5, SDK ufficiale OpenAI 3.29.0, Responses API,
frontend HTML/CSS/JavaScript senza build Node e container Python 3.12.

## Implementato

- Obiettivo, Avvia/Pausa/Riprendi/Ferma, chiarimenti indispensabili, stati e prossimo passo.
- Piano e criteri prima del codice; consultazione di fonti ufficiali e retrieval con fonte/data.
- Memoria del lavoro, decisioni, correzioni, risultati e cronologia del protocollo IA.
- Limiti persistenti, timeout, token e costo stimato quando i prezzi sono configurati.
- Workspace separati, versioni ripristinabili, esportazione del solo progetto.
- Esecuzione Docker senza rete, segreti, cartelle host o socket Docker; nessun ripiego sull’host.
- Pronto subordinato ai test e al contratto indipendente sui file correnti.
- Documenti e trascrizioni; procedure versionate, testate su esempi con il modello prima di adottarle.
- Recupero dopo chiusura; chiamate tool interrotte segnate come risultato ignoto.
- Avvio Windows tramite file .bat, inserimento della chiave con input nascosto, lockfile con hash.

## Verifiche effettive

Eseguite su Linux, Python 3.12.14 e Docker 28.4.0. Consultare
`RISULTATI_VERIFICHE.md` e `resources/evidence/` per gli esiti aggiornati.

- Backend di riferimento: 8 test unitari, nessun fallimento/skip.
- Contratto indipendente: creazione, consultazione, input, idempotenza e persistenza dopo riavvio.
- Difetto deliberato in copia: rilevato da test e contratto; ripristino deterministico verificato.
- App: **35 test passati**, 0 falliti/errori/skipped; API, memoria, sicurezza, budget, SDK, controlli e Docker.
- Chromium: interfaccia italiana, intervento per credenziale assente, recupero, documenti, layout mobile.
- Installazione separata con pip e hash: riuscita su Linux.

I test del protocollo usano un trasporto HTTP simulato e lo dichiarano: non dimostrano
capacità di un modello. Il test completo offline collega SDK, scrittura, Docker,
fallimento, correzione predisposta dal test e nuova verifica.

## Bloccato / non verificato

`AI_PROVIDER_KEY` manca sia nell’ambiente iniziale sia nella configurazione locale.
`scripts/prova_agente.py` ha restituito exit code 2, NON ESEGUITA: nessuna chiamata IA.
La generazione reale, la correzione autonoma del modello, la prova di procedure con IA
e l’autenticazione/modello/fatturazione OpenAI restano da verificare.

Windows 11, Python Windows, Docker Desktop/WSL 2 e i .bat non sono stati eseguiti:
sono predisposti per la verifica sul PC dell’utente. Non è stata verificata la
restaurazione in un nuovo task cloud o la pubblicazione dell’ambiente.

Questa versione supporta il contratto backend attività Python con libreria standard.
Altri backend, installazione di dipendenze nel codice generato e infrastrutture
blockchain sono traguardi successivi. Nessuna gestione di denaro, portafogli,
pubblicazione automatica o accesso a repository/test Nodveta.

## Ripresa

1. Usa il checkout esistente `/workspace/AI-HyperGenius`; ogni task cloud è già isolato.
   Non creare un worktree aggiuntivo salvo richiesta esplicita.
2. Installa dipendenze con `uv sync --frozen`; prepara Docker con
   `.venv/bin/python scripts/prepara_isolamento.py` se l’immagine non è disponibile.
3. Avvia `.venv/bin/python avvia.py --no-browser`; verifica la pagina e `/api/health`
   tramite richieste locali. Non interpretare una porta aperta come prova funzionale.
4. Sulla macchina locale l’utente può eseguire `configura_ia.bat`; nel cloud usa le
   impostazioni dell’ambiente per la credenziale, mai la chat. Riavvia dopo la modifica.
5. Esegui `scripts/prova_agente.py` con il provider reale. Verifica generazione e
   correzione nella copia separata. Conserva gli esiti falliti e non cambiare test per farli passare.
6. Aggiorna questo file con risultati effettivi, senza proclamare riuscite non verificate.

Il progetto è preparato per il versionamento Git sul branch `main`, con origine
`https://github.com/piotr0868/AI-HyperGenius.git`. L’invio remoto va confermato
con `git ls-remote origin refs/heads/main`; non equivale a pubblicare l’ambiente cloud.
Il pacchetto e il repository escludono credenziali, `.data` e `.venv`; il pacchetto
esclude anche `.git`. La configurazione cloud è stata salvata con install_script, start_skill, requisito
personale AI_PROVIDER_KEY per api.openai.com e domini ufficiali di documentazione.
È una bozza confermata: non implica aggiornamento runtime o pubblicazione.
L’utente deve revisionare e salvare nelle impostazioni, poi pubblicare se desidera usarla.
