Questo backend è un riferimento scritto per la consegna. Non è il risultato di una chiamata IA.

Usa soltanto Python 3.12 e SQLite incluso in Python. Per provarlo manualmente:

```text
python main.py --port 8000 --db activities.sqlite3
```

API: `GET /activities`, `POST /activities` con JSON `{"title":"Studiare Python"}`
e intestazione `Idempotency-Key: richiesta-1`. Creazione: 201; ripetizione: 200;
riutilizzo della chiave con dati diversi: 409; input invalido: 422.

Per le prove isolate, dalla cartella principale di Officina esegui
`python scripts/verifica_locale.py`. Questo verifica anche il riavvio del processo.
