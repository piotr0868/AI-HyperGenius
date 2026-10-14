"""Apre l'assistente Officina, riutilizzando un'istanza gia' attiva.

Non avvia i backend generati, nuove prove IA o nuovi progetti.
"""
import os
from pathlib import Path
import socket
import sys
import threading
import time
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener
import webbrowser

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def is_officina(url):
    """Richiede la vera interfaccia, non basta una porta o una risposta 200."""
    try:
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(url + '/', timeout=2) as response:
            if response.status != 200 or response.headers.get_content_type() != 'text/html':
                return False
            html = response.read(131073)
            if len(html) > 131072:
                return False
            return all(marker in html for marker in
                       (b'Officina', b'id="goal-form"', b'id="new-project"'))
    except (OSError, URLError, ValueError):
        return False


def port_in_use(port):
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=1):
            return True
    except OSError:
        return False


def open_browser(url):
    print('Apro Officina: descrizione del programma, progetti e pulsanti.', flush=True)
    print('Indirizzo:', url, flush=True)
    try:
        opened = webbrowser.open(url)
    except (OSError, webbrowser.Error):
        opened = False
    if not opened:
        print('Browser non aperto automaticamente. Incolla l\'indirizzo nel browser.', flush=True)
    return opened


def open_when_ready(url, stop, timeout=45):
    deadline = time.monotonic() + timeout
    while not stop.is_set() and time.monotonic() < deadline:
        if is_officina(url):
            open_browser(url)
            return
        stop.wait(0.25)
    if not stop.is_set():
        print('La pagina di Officina non risponde ancora. Conserva questa finestra e leggi gli errori.', flush=True)


def main():
    try:
        os.chdir(ROOT)
        from app.config import load_settings
        settings = load_settings()
        url = f'http://127.0.0.1:{settings.port}'
        if is_officina(url):
            print('Officina e\' gia\' attiva: riuso il server esistente.', flush=True)
            return 0 if open_browser(url) else 1
        if port_in_use(settings.port):
            print(f'La porta {settings.port} e\' occupata da una pagina diversa da Officina.', flush=True)
            print('Nessun processo e\' stato fermato. Non apro la pagina tecnica del backend.', flush=True)
            return 1

        from scripts.avvio_automatico import ensure_docker, load_local_credentials
        load_local_credentials()
        if not ensure_docker():
            print('Apro l\'interfaccia. L\'esecuzione del codice resta disabilitata finche\' Docker non e\' pronto.', flush=True)

        import avvia
        stop = threading.Event()
        browser = threading.Thread(target=open_when_ready, args=(url, stop), daemon=True)
        previous_arguments = sys.argv[:]
        try:
            # Il browser viene aperto dopo la risposta HTML, non dopo un tempo fisso.
            sys.argv.append('--no-browser')
            browser.start()
            avvia.main()
        finally:
            stop.set()
            browser.join(timeout=3)
            sys.argv[:] = previous_arguments
        return 0
    except KeyboardInterrupt:
        print('Officina fermata. Progetti e memoria restano sul disco.', flush=True)
        return 0
    except Exception as exc:
        # Gli errori possono contenere configurazione: mostrare solo il tipo.
        print(f'Avvio di Officina non completato ({type(exc).__name__}). File e credenziali conservati.', flush=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
