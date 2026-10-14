"""Regressione UI riportata dal PC: fonte di prova dichiarata, SDK reale senza API."""
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path

from groq import AsyncGroq
import httpx
import pytest

from app.agent import Agent
from app.config import Settings, load_settings
from app.sandbox import Sandbox
from app.storage import Store

ROOT = Path(__file__).resolve().parent.parent
BLOCKED = 'Prima salva piano e criteri, poi consulta documentazione pertinente.'


def saved_attempt(code):
    return [
        {'type': 'function_call', 'name': 'write_file', 'call_id': 'blocked-main',
         'arguments': json.dumps({'path': 'main.py', 'content': code})},
        {'type': 'function_call_output', 'call_id': 'blocked-main',
         'output': json.dumps({'error': BLOCKED})},
    ]


@pytest.mark.parametrize('invalid_backend', [False, True])
async def test_ui_recovers_at_twelve_calls_and_checks_original_uploaded_tests_in_docker(tmp_path, invalid_backend):
    settings = replace(load_settings(), data_dir=tmp_path, max_model_calls=12, min_interval=0)
    sandbox = Sandbox(settings)
    status = await sandbox.status()
    if not status['available']:
        pytest.skip(status['reason'])
    # Il codice della prova è il riferimento dichiarato, NON il main.py di 4485
    # caratteri sul PC (il rapporto ne fornisce solo hash e ricevuta).
    code = (ROOT / 'examples/activity_backend/main.py').read_text()
    if invalid_backend:
        code = code.replace('or not title.strip() or', 'or')
    uploaded_tests = (ROOT / 'resources/evidence/attivita-e32ae57b/test_api_originale.py.txt').read_text()
    store = Store(tmp_path)
    pid = store.create_project('Riproduzione dello stato UI a 12 chiamate')['id']
    store.write_file(pid, 'tests/__init__.py', '# init\n')
    store.write_file(pid, 'tests/test_api.py', uploaded_tests)
    history = saved_attempt(code)
    store.update(pid, state='Serve il tuo intervento', model_calls=12, tool_calls=12,
        input_tokens=34765, output_tokens=7394, elapsed=677.437,
        criteria=['API, input validi, richieste idempotenti e persistenza'],
        plan=['Scrivere e verificare il backend'], docs_consulted=1, history=history)
    old_history = copy.deepcopy(history)
    original_tests = {name: value for name, value in store.files(pid).items()}

    def reject_request(request):
        pytest.fail('Recupero e verifiche a limite raggiunto non devono chiamare il modello')

    client = AsyncGroq(api_key='offline-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(reject_request)))
    agent = Agent(settings, store, sandbox, client=client)
    try:
        await agent.run(pid)
        result = store.project(pid)
        assert result['model_calls'] == 12
        assert result['input_tokens'] == 34765 and result['output_tokens'] == 7394
        assert result['elapsed'] >= 677.437
        assert store.files(pid)['main.py'] == code
        assert {name: store.files(pid)[name] for name in original_tests} == original_tests
        assert result['history'][:len(old_history)] == old_history
        recovery = next(event for event in store.events(pid) if event['kind'] == 'recupero_scrittura_ia')
        assert recovery['detail']['sha256'] == hashlib.sha256(code.encode()).hexdigest()
        assert recovery['detail']['actor'] == 'system' and recovery['detail']['model_called'] is False
        assert result['last_check']['check']['unit_tests'] == 5
        assert result['last_check']['passed'] is not invalid_backend
        if invalid_backend:
            assert result['state'] == 'Serve il tuo intervento' and result['verified_hash'] is None
            assert result['failed_checks'] == 1 and result['tool_calls'] == 14
        else:
            assert result['state'] == 'Pronto' and result['verified_hash'] == store.digest(pid)
            assert len(result['last_check']['check']['contract']) == 5
            assert result['failed_checks'] == 0 and result['tool_calls'] == 15
        checks_before = len([event for event in store.events(pid) if event['kind'] == 'verifica'])
        await agent.run(pid)
        assert len([event for event in store.events(pid) if event['kind'] == 'verifica']) == checks_before
        assert len([event for event in store.events(pid) if event['kind'] == 'recupero_scrittura_ia']) == 1
        version = store.rows('SELECT id FROM versions WHERE project_id=? AND path=?', (pid, 'main.py'))[0]['id']
        store.rollback(pid, version)
        assert 'main.py' not in store.files(pid)
        assert not await agent.recover_missing_entrypoint(pid), 'Un file rimosso intenzionalmente non va ricreato'
    finally:
        await agent.shutdown()
        store.close()


@pytest.mark.parametrize('condition', ['pause', 'stop', 'time', 'tool_budget', 'before_model_limit'])
async def test_shared_recovery_respects_control_and_remaining_operational_limits(tmp_path, condition):
    store = Store(tmp_path)
    pid = store.create_project('Recupero controllato')['id']
    code = 'raise RuntimeError("Il codice generato non deve essere eseguito sull’host")\n'
    store.update(pid, history=saved_attempt(code), criteria=['API'], plan=['Implementare'], docs_consulted=1,
                 model_calls=3, control=condition if condition in ('pause', 'stop') else 'run',
                 elapsed=1200 if condition == 'time' else 0,
                 tool_calls=39 if condition == 'tool_budget' else 0)
    agent = Agent(Settings(data_dir=tmp_path), store, None)
    try:
        recovered = await agent.recover_missing_entrypoint(pid)
        assert recovered == (condition == 'before_model_limit')
        assert ('main.py' in store.files(pid)) == recovered
        assert store.project(pid)['model_calls'] == 3
    finally:
        await agent.shutdown()
        store.close()
