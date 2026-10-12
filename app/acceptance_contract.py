"""Contratto indipendente per il backend generato. Eseguito solo dentro Docker."""
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest


def request(port, method, body=None, key=None):
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=3)
    headers = {'Content-Type': 'application/json'}
    if key is not None:
        headers['Idempotency-Key'] = key
    conn.request(method, '/activities', json.dumps(body) if body is not None else None, headers)
    response = conn.getresponse()
    raw = response.read(100000)
    status = response.status
    conn.close()
    return status, json.loads(raw)


def start_server(port, database, log):
    process = subprocess.Popen([sys.executable, 'main.py', '--port', str(port), '--db', database],
                               stdout=log, stderr=log, stdin=subprocess.DEVNULL)
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError('Il backend termina durante l’avvio.')
        try:
            request(port, 'GET')
            return process
        except (OSError, ValueError):
            time.sleep(.05)
    process.kill()
    process.wait()
    raise AssertionError('Il backend non risponde entro 6 secondi.')


def stop_server(process):
    process.terminate()
    try:
        process.wait(3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def run():
    suite = unittest.defaultTestLoader.discover('tests')
    count = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = {'unit_tests': count, 'unit_failures': len(result.failures),
               'unit_errors': len(result.errors), 'unit_skipped': len(result.skipped),
               'unit_expected_failures': len(result.expectedFailures),
               'unit_unexpected_successes': len(result.unexpectedSuccesses), 'contract': []}
    passed = count > 0 and result.wasSuccessful() and not result.skipped and not result.expectedFailures
    summary['unit_ok'] = passed
    process = None
    with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryFile() as log:
        sock = socket.socket()
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        sock.close()
        database = str(Path(temp) / 'activities.sqlite3')
        try:
            process = start_server(port, database, log)
            status, created = request(port, 'POST', {'title': 'Prima attività'}, 'contract-1')
            assert status == 201 and isinstance(created, dict) and created.get('id') is not None
            assert created.get('title') == 'Prima attività'
            summary['contract'].append('creazione')
            status, items = request(port, 'GET')
            assert status == 200 and isinstance(items, list) and created in items
            summary['contract'].append('consultazione')
            for payload in ({'title': ''}, {'title': '   '}, {'title': 42}, {}, {'title': 'x' * 201}):
                status, _ = request(port, 'POST', payload, 'invalid')
                assert status in (400, 422), f'Input non valido accettato: {payload!r}'
            summary['contract'].append('validazione')
            status, repeated = request(port, 'POST', {'title': 'Prima attività'}, 'contract-1')
            assert status in (200, 201) and repeated == created
            status, _ = request(port, 'POST', {'title': 'Diversa'}, 'contract-1')
            assert status == 409, 'La stessa chiave con dati diversi deve restituire 409.'
            status, items = request(port, 'GET')
            assert len(items) == 1, 'Richiesta ripetuta: è stata creata una duplicazione.'
            summary['contract'].append('idempotenza')
            stop_server(process)
            process = start_server(port, database, log)
            status, items = request(port, 'GET')
            assert status == 200 and items == [created]
            status, repeated = request(port, 'POST', {'title': 'Prima attività'}, 'contract-1')
            assert status in (200, 201) and repeated == created
            summary['contract'].append('persistenza dopo riavvio')
        except Exception as exc:
            summary['contract_error'] = f'{type(exc).__name__}: {exc}'
            passed = False
        finally:
            if process is not None and process.poll() is None:
                stop_server(process)
            log.seek(0)
            summary['server_log'] = log.read(8000).decode(errors='replace')
    summary['passed'] = passed and len(summary['contract']) == 5
    print('OFFICINA_CHECK=' + json.dumps(summary, ensure_ascii=False), flush=True)
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    sys.exit(run())
