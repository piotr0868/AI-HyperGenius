"""Smoke della consegna separata: Docker reale, volume persistente e Chromium reale.

Non importa il progetto caricato e non usa credenziali o modelli IA.
Eseguire dalla radice dopo docker build -t officina-attivita-e32ae57b:1
examples/attivita_consegna (su cloud usare --config in una directory scrivibile).
"""
import http.client
import json
from pathlib import Path
import shutil
import subprocess
import time
import uuid

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def cli(*args):
    result = subprocess.run(['docker', *args], capture_output=True, text=True, timeout=15)
    if result.returncode:
        raise RuntimeError(result.stderr[:3000])
    return result.stdout.strip()


def main():
    name = 'officina-delivery-test-' + uuid.uuid4().hex[:12]
    network, volume = name + '-net', name + '-data'
    proof = {'platform': 'Linux', 'model_calls': 0, 'windows_batch_executed': False}
    try:
        cli('network', 'create', network)
        cli('run', '-d', '--name', name, '--label', 'officina_delivery=e32ae57b',
            '--network', network, '-p', '127.0.0.1::8000', '--read-only', '--cap-drop=ALL',
            '--security-opt=no-new-privileges', '--memory=256m', '--memory-swap=256m',
            '--cpus=0.5', '--pids-limit=64', '--tmpfs', '/tmp:rw,noexec,nosuid,size=16m',
            '-v', volume + ':/data', 'officina-attivita-e32ae57b:1')
        config = json.loads(cli('inspect', name))[0]
        if not config['State']['Running']:
            raise AssertionError('Avvio Docker fallito: ' + cli('logs', name))
        port = int(config['NetworkSettings']['Ports']['8000/tcp'][0]['HostPort'])

        def request(method='GET', body=None, key=None):
            headers = {'Content-Type': 'application/json'}
            if key:
                headers['Idempotency-Key'] = key
            connection = http.client.HTTPConnection('127.0.0.1', port, timeout=3)
            try:
                connection.request(method, '/activities', json.dumps(body) if body else None, headers)
                response = connection.getresponse()
                return response.status, json.loads(response.read())
            finally:
                connection.close()

        def ready():
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                try:
                    if request()[0] == 200:
                        return
                except (OSError, ValueError):
                    pass
                time.sleep(.1)
            raise AssertionError('Il container non risponde dopo 10 secondi.')

        ready()
        assert request() == (200, [])
        status, item = request('POST', {'title': 'Conserva dopo il riavvio'}, 'persistent-smoke')
        assert status == 201
        assert request('POST', {'title': item['title']}, 'persistent-smoke') == (200, item)
        cli('stop', '--time', '2', name)
        cli('start', name)
        restarted = json.loads(cli('inspect', name))[0]
        port = int(restarted['NetworkSettings']['Ports']['8000/tcp'][0]['HostPort'])
        ready()
        assert request() == (200, [item])
        assert request('POST', {'title': item['title']}, 'persistent-smoke') == (200, item)
        assert request('POST', {'title': 'diverso'}, 'persistent-smoke')[0] == 409
        proof['container_restart_persistence'] = True
        proof['idempotency_across_restart'] = True

        errors = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=shutil.which('chromium'), headless=True,
                args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{port}/')
            page.get_by_label('Cosa vuoi ricordare?').fill('Prova dal browser <b>testo</b>')
            page.get_by_role('button', name='Salva attività').click()
            page.get_by_role('status').filter(has_text='Attività salvata.').wait_for()
            assert page.locator('#items li').count() == 2
            assert page.locator('#items b').count() == 0
            page.reload()
            page.locator('#items li').filter(has_text='Prova dal browser <b>testo</b>').wait_for()
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            assert not errors, errors
            browser.close()
        assert len(request()[1]) == 2
        proof.update(browser='Chromium reale, viewport 390x844', browser_save_and_reload=True,
                     titles_rendered_as_text=True, javascript_errors=errors)
        assert config['Config']['User'] == '65534:65534'
        assert config['HostConfig']['ReadonlyRootfs'] is True
        assert config['HostConfig']['CapDrop'] == ['ALL']
        assert not any(mount['Type'] == 'bind' for mount in config['Mounts'])
        assert json.loads(cli('network', 'inspect', network))[0]['Driver'] == 'bridge'
        assert config['NetworkSettings']['Ports']['8000/tcp'][0]['HostIp'] == '127.0.0.1'
        proof['isolation'] = {'user': '65534:65534', 'readonly_root': True,
            'cap_drop_all': True, 'host_bind_mounts': False,
            'network': 'dedicated bridge; outbound traffic possible', 'published_on_loopback_only': True}
        proof['passed'] = True
    finally:
        for args in (('rm', '-f', name), ('volume', 'rm', volume), ('network', 'rm', network)):
            subprocess.run(['docker', *args], capture_output=True, timeout=15)
    destination = ROOT / 'resources/evidence/attivita-e32ae57b/container-browser-smoke.json'
    destination.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(proof, ensure_ascii=False))


if __name__ == '__main__':
    main()
