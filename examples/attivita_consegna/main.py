"""Backend completato da Codex; non attribuito all'agente Groq di Officina."""
import argparse
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3


class ActivityStore:
    def __init__(self, filename):
        self.filename = str(filename)
        with self.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS activities(
                id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
                request_key TEXT NOT NULL UNIQUE)''')

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.filename, timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def create(self, title, key):
        if not isinstance(title, str) or not title.strip() or len(title.strip()) > 200:
            raise ValueError('title deve essere un testo da 1 a 200 caratteri.')
        if not isinstance(key, str) or not key.strip() or len(key) > 200:
            raise ValueError('Idempotency-Key è obbligatoria, massimo 200 caratteri.')
        title = title.strip()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            previous = db.execute('SELECT id,title FROM activities WHERE request_key=?', (key,)).fetchone()
            if previous:
                if previous['title'] != title:
                    return 409, {'error': 'Chiave già utilizzata con dati diversi.'}
                return 200, dict(previous)
            cursor = db.execute('INSERT INTO activities(title,request_key) VALUES(?,?)', (title, key))
            return 201, {'id': cursor.lastrowid, 'title': title}

    def all(self):
        with self.connect() as db:
            return [dict(row) for row in db.execute('SELECT id,title FROM activities ORDER BY id')]


def make_handler(store):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def send_json(self, status, data):
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                      '/app.js': ('app.js', 'text/javascript; charset=utf-8')}
            if self.path in assets:
                filename, content_type = assets[self.path]
                body = (Path(__file__).parent / 'web' / filename).read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(body)))
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
                self.end_headers()
                self.wfile.write(body)
                return
            if self.path != '/activities':
                return self.send_json(404, {'error': 'Percorso non trovato.'})
            try:
                self.send_json(200, store.all())
            except sqlite3.Error:
                self.send_json(503, {'error': 'Database temporaneamente non disponibile.'})

        def do_POST(self):
            if self.path != '/activities':
                return self.send_json(404, {'error': 'Percorso non trovato.'})
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + self.headers.get('Host', ''):
                return self.send_json(403, {'error': 'Origine della richiesta non consentita.'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 4096:
                    raise ValueError('Corpo della richiesta non valido.')
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError('Serve un oggetto JSON.')
                status, body = store.create(data.get('title'), self.headers.get('Idempotency-Key'))
                self.send_json(status, body)
            except (ValueError, UnicodeError):
                self.send_json(422, {'error': 'Input non valido. Controlla title e Idempotency-Key.'})
            except sqlite3.Error:
                self.send_json(503, {'error': 'Database temporaneamente non disponibile.'})

        def log_message(self, *args):
            pass
    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--host', choices=('127.0.0.1', '0.0.0.0'), default='127.0.0.1')
    parser.add_argument('--db', default='activities.sqlite3')
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(ActivityStore(args.db)))
    print(f'Backend attività sulla porta {server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
