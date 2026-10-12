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
