# Fonti ufficiali consultate e incluse

Consultazione: 12 ottobre 2026. Le copie sono materiale di riferimento non fidato,
con URL e data nel file `official_docs.json`; non sostituiscono aggiornamenti futuri.

- SDK OpenAI 3.29.0: <https://github.com/openai/openai-python>.
  Consultati README e tipi ufficiali `FunctionToolParam`, `ResponseFunctionToolCall`,
  `ResponseUsage` e `ResponseCreateParams`. Licenza in `licenses/OpenAI-SDK.txt`.
- SDK Groq 1.7.0: <https://github.com/groq/groq-python>. Consultati README,
  schema Chat Completions e metodo ufficiale, inclusi tools, max_completion_tokens e
  parallel_tool_calls. Licenza in `licenses/Groq-SDK.txt`.
- Cookbook Groq: <https://github.com/groq/groq-api-cookbook>, chiave gratuita e tool use.
  Le quote correnti della pagina console.groq.com/docs/rate-limits non sono state
  verificabili nella rete iniziale; controllarle nell’account.
- Python 3.12: documentazione ufficiale `http.server`, `sqlite3`, `unittest`,
  da <https://github.com/python/cpython/tree/3.12/Doc/library>.
  Licenza in `licenses/Python.txt`.
- Le pagine `developers.openai.com` e `docs.docker.com` erano bloccate dalla policy
  di rete iniziale; per l’integrazione sono stati usati README e schema SDK ufficiali.
  I domini di documentazione sono stati aggiunti alla bozza cloud; propagazione
  runtime e consultazione delle pagine dopo pubblicazione non sono state verificate.

L’SDK e le altre dipendenze sono installati dal registro PyPI tramite i lockfile.
Docker ha verificato le somme degli strati dell’immagine scaricata; l’esecuzione usa
il digest fissato in `.env`, senza disabilitare TLS, firme o checksum.

## Aggiornamento 13 ottobre 2026

Consultata anche la documentazione contenuta nel SDK ufficiale `groq==1.7.0`,
modulo `groq.resources.chat.completions.AsyncCompletions.create`: per
`openai/gpt-oss-20b` e `openai/gpt-oss-120b`, reasoning_effort supporta low/medium/high,
con medium predefinito. Sorgente ufficiale:
https://github.com/groq/groq-python/blob/main/src/groq/resources/chat/completions.py
Lettura installata da lockfile con hash; nessuna nuova dipendenza aggiunta.

Consultati gli errori ufficiali di winget nel repository Microsoft:
https://raw.githubusercontent.com/microsoft/winget-cli/master/src/AppInstallerSharedLib/Public/AppInstallerErrors.h
Un esito "nessun aggiornamento applicabile" non viene dichiarato dal helper come
aggiornamento effettuato; l'utente può usare il comando Update di Docker.

Consultate il 13 ottobre 2026 anche le pagine attuali:

- https://console.groq.com/docs/tool-use/overview: GPT-OSS supporta tool locali,
  senza tool paralleli; il risultato deve essere restituito al modello.
- https://console.groq.com/docs/tool-use/local-tool-calling: errori 400 di tool
  generation e failed_generation, rigenerazione limitata con temperatura ridotta.
  Il nostro codice non esegue né registra failed_generation; classifica il rifiuto
  ed evita tentativi automatici su 400 non riconosciuti come generazione tool.
- https://console.groq.com/docs/errors: significato distinto di 400, 401 e 429.
- https://console.groq.com/docs/rate-limits: tabella generale Free per GPT-OSS 20b
  consultata (30 RPM, 1K RPD, 8K TPM, 200K TPD). I limiti effettivi dell'account
  dell'utente non sono stati consultati; fare riferimento alla sua console e ai
  metadati numerici registrati, senza attribuire il precedente 400 alla quota.
