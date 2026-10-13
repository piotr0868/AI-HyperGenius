"""Backend di riferimento e HTTP SDK simulato; nessuna capacità del modello certificata."""
from dataclasses import replace
import json
from pathlib import Path
import sys

from groq import AsyncGroq
import httpx
import pytest

from app.agent import Agent
from app.config import load_settings
from app.sandbox import Sandbox
from app.storage import Store
from scripts import prova_agente as live


RESTART_TEST = '''import json
import tempfile
import threading
import unittest
import urllib.request
import main

class Restart(unittest.TestCase):
    def test_persistence_across_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            db = directory + '/tasks.sqlite3'
            httpd = main.ThreadingHTTPServer(('localhost', 0), main.make_handler(main.ActivityStore(db)))
            port = httpd.server_port
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            second = None
            try:
                request = urllib.request.Request('http://localhost:%s/activities' % port,
                    json.dumps({'title': 'persistente'}).encode(),
                    {'Idempotency-Key': 'restart', 'Content-Type': 'application/json'})
                with urllib.request.urlopen(request) as response:
                    created = json.load(response)
                httpd.shutdown()
                thread.join()
                # Riproduce la riga e il difetto della diagnosi Windows.
                second = main.ThreadingHTTPServer(('localhost', port), main.make_handler(main.ActivityStore(db)))
                thread2 = threading.Thread(target=second.serve_forever, daemon=True)
                thread2.start()
                with urllib.request.urlopen('http://localhost:%s/activities' % port) as response:
                    self.assertEqual(json.load(response), [created])
                second.shutdown()
                thread2.join()
            finally:
                httpd.server_close()
                if second is not None:
                    second.server_close()
'''


def reference_files():
    root = Path(__file__).resolve().parent.parent / 'examples/activity_backend'
    files = {path.relative_to(root).as_posix(): path.read_text(encoding='utf-8')
             for path in root.rglob('*.py') if '__pycache__' not in path.parts}
    files['tests/test_restart_lifecycle.py'] = RESTART_TEST
    return files


@pytest.mark.parametrize('source', [
    'from http.server import ThreadingHTTPServer as Server\n',
    'from http.server import ThreadingHTTPServer\nThreadingHTTPServer = custom\n',
    'from http.server import ThreadingHTTPServer\nclass ThreadingHTTPServer: pass\n',
    'from http.server import ThreadingHTTPServer\nfrom other import *\n',
    'invalid python {',
])
def test_procedure_refuses_unknown_bindings(source):
    assert live.closing_server_source(source) is None


def test_procedure_never_executes_source_and_does_not_apply_twice(tmp_path):
    marker = tmp_path / 'not-executed'
    source = 'from http.server import ThreadingHTTPServer\n' + f'open({str(marker)!r}, "w").write("bad")\n'
    fixed = live.closing_server_source(source)
    assert 'self.server_close()' in fixed and not marker.exists()
    assert live.closing_server_source(fixed) is None


async def test_windows_failure_reproduced_and_system_fix_passes_same_tests_in_docker(tmp_path):
    settings = replace(load_settings(), data_dir=tmp_path, min_interval=0, max_model_calls=20)
    sandbox = Sandbox(settings)
    status = await sandbox.status()
    if not status['available']:
        pytest.skip(status['reason'])
    store = Store(tmp_path)
    agent = Agent(settings, store, sandbox, client=object())
    project = store.create_project(live.GOAL)
    pid = project['id']
    files = reference_files()
    for name, content in files.items():
        store.write_file(pid, name, content)
    store.update(pid, criteria=['API e test'], plan=['Verifica'], docs_consulted=1)
    initial = await agent.perform(pid, 'run_checks', {})
    assert initial['passed'] is False and initial['check']['unit_errors'] == 1
    assert len(initial['check']['contract']) == 5 and 'Address already in use' in initial['stderr']
    store.update(pid, state='Serve il tuo intervento', model_calls=16, tool_calls=15,
                 input_tokens=74968, output_tokens=10486, failed_checks=3, elapsed=777.391)
    try:
        result = await live.run_or_recheck(agent, store, sandbox, store.project(pid))
        assert result['state'] == 'Pronto' and result['last_check']['passed']
        assert result['last_check']['check']['unit_tests'] == 9
        assert len(result['last_check']['check']['contract']) == 5
        assert result['model_calls'] == 16 and result['input_tokens'] == 74968 and result['output_tokens'] == 10486
        assert result['failed_checks'] == 3 and result['elapsed'] > 777.391
        assert all(store.files(pid)[name] == content for name, content in files.items() if name.startswith('tests/'))
        event = next(e for e in store.events(pid) if e['kind'] == 'correzione_sistema')
        assert event['detail']['author'] == 'Codex' and not event['detail']['model_called']
        version = store.rows('SELECT id FROM versions WHERE project_id=? AND path=? ORDER BY id DESC LIMIT 1', (pid, 'main.py'))[0]
        store.rollback(pid, version['id'])
        assert store.files(pid)['main.py'] == files['main.py'] and store.project(pid)['verified_hash'] is None
    finally:
        store.close()


async def test_separate_ai_protocol_repairs_after_system_fix_within_four_remaining_calls(tmp_path, monkeypatch):
    config = replace(load_settings(), data_dir=tmp_path, api_key='offline-only', min_interval=0, max_model_calls=12)
    sandbox = Sandbox(config)
    status = await sandbox.status()
    if not status['available']:
        pytest.skip(status['reason'])
    store = Store(tmp_path / 'live-acceptance')
    pid = store.create_project(live.GOAL)['id']
    files = reference_files()
    for name, content in files.items():
        store.write_file(pid, name, content)
    initial = await sandbox.verify(files, pid)
    assert initial['passed'] is False
    store.update(pid, state='Serve il tuo intervento', criteria=['API e test'], plan=['Verifica'], docs_consulted=1,
        last_check=initial, model_calls=16, tool_calls=15, input_tokens=74968, output_tokens=10486,
        failed_checks=3, elapsed=777.391)
    live.save_json(tmp_path / 'live-acceptance/RUN.json', {'generation_id': pid})
    store.close()
    calls = iter([
        ('write_file', {'path': 'regression_target.py', 'content': 'def normalize_title(value):\n    return value.strip()\n'}),
        ('run_checks', {}), ('finish', {'summary': 'Prova offline verificata', 'next_step': 'Risultati'})])
    requests = []

    def respond(request):
        payload = json.loads(request.content)
        requests.append(payload)
        if len(requests) == 1:
            assert any('test_strip' in str(message) and 'FAIL' in str(message) for message in payload['messages'])
            assert any('unittest' in str(message) and 'source_date' in str(message) for message in payload['messages'])
        name, args = next(calls)
        return httpx.Response(200, json={'id': f'chat_{len(requests)}', 'object': 'chat.completion',
            'created': 1, 'model': config.model, 'choices': [{'index': 0, 'finish_reason': 'tool_calls',
            'message': {'role': 'assistant', 'content': None, 'tool_calls': [{'id': f'call_{len(requests)}',
                'type': 'function', 'function': {'name': name, 'arguments': json.dumps(args)}}]}}],
            'usage': {'prompt_tokens': 100, 'completion_tokens': 20, 'total_tokens': 120}})

    client = AsyncGroq(api_key='offline-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    monkeypatch.setattr(live, 'load_settings', lambda: config)
    monkeypatch.setattr(live, 'Agent', lambda settings, store, sandbox: Agent(settings, store, sandbox, client=client))
    monkeypatch.setattr(sys, 'argv', ['prova_agente.py', '--chiamate-prova', '20'])
    assert await live.main() == 0
    result = live.read_json(tmp_path / 'live-acceptance/RESULTS.json')
    assert result['generation']['model_calls'] == 16 and len(requests) == 3
    assert result['repair']['project']['model_calls'] == 3
    assert result['repair']['detected_initial_fault'] and result['repair']['corrected_and_retested']
    assert result['repair']['ai_repair_write'] and result['repair']['original_unchanged']
    assert result['repair']['project']['last_check']['check']['unit_tests'] == 10
    assert result['operational_limits']['repair_model_calls'] == 4 and config.max_model_calls == 12


def test_certificate_requires_actual_successful_ai_write():
    assert live.ai_repair_write({'history': []}) is None
    call = {'type': 'function_call', 'call_id': 'c', 'name': 'write_file',
            'arguments': json.dumps({'path': 'regression_target.py', 'content': 'fixed'})}
    failure = {'type': 'function_call_output', 'call_id': 'c', 'output': '{"error":"not saved"}'}
    assert live.ai_repair_write({'history': [call, failure]}) is None
