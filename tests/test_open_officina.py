"""Avvio dell'interfaccia: HTTP reale, nessun modello o codice generato."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import threading

import pytest

from app.config import Settings
from scripts import apri_officina as launcher

HTML = (Path(__file__).resolve().parents[1] / 'app/static/index.html').read_bytes()


@contextmanager
def page(body=HTML, content_type='text/html', redirect=False):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            self.send_response(302 if redirect else 200)
            self.send_header('Content-Type', content_type)
            if redirect:
                self.send_header('Location', '/must-not-open')
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port, requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def configure(monkeypatch, tmp_path, port):
    import app.config
    settings = Settings(data_dir=tmp_path / '.data', port=port)
    monkeypatch.setattr(launcher, 'ROOT', tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(app.config, 'load_settings', lambda: settings)
    return settings


def test_reopens_existing_interface_twice_without_starting_servers_or_touching_memory(monkeypatch, tmp_path):
    from scripts import avvio_automatico as setup

    def forbidden():
        raise AssertionError('Il riuso non deve caricare chiavi o avviare Docker.')

    monkeypatch.setattr(setup, 'ensure_docker', forbidden)
    monkeypatch.setattr(setup, 'load_local_credentials', forbidden)
    memory = tmp_path / 'saved-memory'
    memory.write_bytes(b'preserve projects and limits')
    opened = []
    monkeypatch.setattr(launcher.webbrowser, 'open', lambda url: opened.append(url) or True)
    with page() as (port, requests):
        configure(monkeypatch, tmp_path, port)
        assert launcher.main() == launcher.main() == 0
        assert opened == [f'http://127.0.0.1:{port}'] * 2
        assert requests == ['/', '/']
        assert not (tmp_path / '.data').exists()
    assert memory.read_bytes() == b'preserve projects and limits'


@pytest.mark.parametrize('body,content_type', [
    (b'[]', 'application/json'),
    (b'<html><title>Another application</title></html>', 'text/html'),
])
def test_occupied_backend_or_other_site_is_not_opened_or_stopped(monkeypatch, tmp_path, capsys, body, content_type):
    opened = []
    monkeypatch.setattr(launcher.webbrowser, 'open', lambda url: opened.append(url))
    with page(body, content_type) as (port, requests):
        configure(monkeypatch, tmp_path, port)
        assert launcher.main() == 1
        assert not opened
        assert launcher.port_in_use(port)
    assert 'occupata' in capsys.readouterr().out
    assert not (tmp_path / '.data').exists()


def test_redirect_does_not_open_another_page():
    with page(redirect=True) as (port, requests):
        assert not launcher.is_officina(f'http://127.0.0.1:{port}')
        assert requests == ['/']


def test_browser_failure_is_reported_without_claiming_success(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(launcher.webbrowser, 'open', lambda url: False)
    with page() as (port, requests):
        configure(monkeypatch, tmp_path, port)
        assert launcher.main() == 1
    assert 'Browser non aperto automaticamente' in capsys.readouterr().out


def test_starts_real_officina_and_waits_for_html_before_opening_browser(monkeypatch, tmp_path):
    import avvia
    import uvicorn
    from app.main import create_app
    from scripts import avvio_automatico as setup

    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        port = reservation.getsockname()[1]
    settings = configure(monkeypatch, tmp_path, port)
    calls = []
    monkeypatch.setattr(setup, 'load_local_credentials', lambda: calls.append('credentials loaded locally'))
    monkeypatch.setattr(setup, 'ensure_docker', lambda: False)
    server = uvicorn.Server(uvicorn.Config(create_app(settings), host='127.0.0.1', port=port,
                                         log_level='error', access_log=False))

    def browser(url):
        assert launcher.is_officina(url)
        calls.append(url)
        server.should_exit = True
        return True

    def run():
        assert '--no-browser' in launcher.sys.argv
        server.run()

    monkeypatch.setattr(launcher.webbrowser, 'open', browser)
    monkeypatch.setattr(avvia, 'main', run)
    watchdog = threading.Timer(12, lambda: setattr(server, 'should_exit', True))
    previous_arguments = launcher.sys.argv[:]
    watchdog.start()
    try:
        assert launcher.main() == 0
    finally:
        watchdog.cancel()
    assert calls == ['credentials loaded locally', f'http://127.0.0.1:{port}']
    assert launcher.sys.argv == previous_arguments
    assert not launcher.port_in_use(port)
    assert (settings.data_dir / 'memory.sqlite3').exists()
