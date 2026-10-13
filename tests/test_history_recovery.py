"""Recupero di richieste predisposte dal test: nessuna capacità IA simulata come reale."""
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path

from groq import AsyncGroq
import httpx
import pytest

from app.agent import Agent, INSTRUCTIONS, TOOLS
from app.config import Settings, load_settings
from app.providers import generation_payload, groq_messages, request_input_reserve
from app.sandbox import Sandbox
from app.storage import Store
from scripts.prova_agente import recover_missing_entrypoint, run_or_recheck

BLOCKED = 'Prima salva piano e criteri, poi consulta documentazione pertinente.'


def attempted_write(content, call_id='main_attempt', error=BLOCKED):
    return [{'type': 'function_call', 'call_id': call_id, 'name': 'write_file',
             'arguments': json.dumps({'path': 'main.py', 'content': content})},
            {'type': 'function_call_output', 'call_id': call_id, 'output': json.dumps({'error': error})}]


class OfflineSandbox:
    async def status(self):
        return {'available': True}

    async def stop(self, owner):
        pass


@pytest.mark.parametrize('condition', ['existing', 'deleted', 'no_docs', 'other_error', 'unknown_result', 'too_large', 'correction_limit'])
async def test_recovery_only_replays_known_prerequisite_failure_for_missing_unversioned_main(tmp_path, condition):
    store = Store(tmp_path)
    project = store.create_project('Backend attività')
    pid = project['id']
    content = 'print("from prior response")\n' if condition != 'too_large' else 'x' * 128001
    history = [{'role': 'user', 'content': 'Backend'}] + attempted_write(content)
    if condition == 'other_error':
        history[-1]['output'] = json.dumps({'error': 'Percorso non consentito'})
    elif condition == 'unknown_result':
        history += attempted_write('latest unknown', 'later')
        history[-1]['output'] = '{"interrupted":true}'
    if condition in ('existing', 'deleted'):
        store.write_file(pid, 'main.py', 'preserve existing intent')
        if condition == 'deleted':
            store.safe_path(pid, 'main.py').unlink()
    store.update(pid, criteria=['API'], plan=['Crea e verifica'], docs_consulted=int(condition != 'no_docs'),
                 model_calls=15, input_tokens=67974, output_tokens=10448, history=history,
                 failed_checks=4 if condition == 'correction_limit' else 0)
    agent = Agent(Settings(data_dir=tmp_path, max_model_calls=20), store, OfflineSandbox())
    original = copy.deepcopy(history)
    before = store.files(pid)
    try:
        assert await recover_missing_entrypoint(agent, store, store.project(pid)) is False
        assert store.files(pid) == before and store.project(pid)['history'] == original
        assert store.project(pid)['model_calls'] == 15
        assert not any(event['kind'] == 'recupero_scrittura_ia' for event in store.events(pid))
    finally:
        await agent.shutdown()
        store.close()


async def test_exact_prior_main_is_recovered_then_verified_in_real_docker_without_new_model_call(tmp_path):
    settings = replace(load_settings(), data_dir=tmp_path, min_interval=0, max_model_calls=20)
    sandbox = Sandbox(settings)
    status = await sandbox.status()
    if not status['available']:
        pytest.skip(status['reason'])
    root = Path(__file__).resolve().parent.parent / 'examples/activity_backend'
    main = (root / 'main.py').read_text()
    store = Store(tmp_path)
    project = store.create_project('Fixture di codice antecedente, non nuova generazione IA')
    pid = project['id']
    for path in (root / 'tests').rglob('*.py'):
        store.write_file(pid, path.relative_to(root).as_posix(), path.read_text())
    history = [{'role': 'user', 'content': 'Backend attività'}] + attempted_write('old source', 'old') + attempted_write(main)
    original = copy.deepcopy(history)
    store.update(pid, criteria=['API, validazione, idempotenza, persistenza'], plan=['Crea e verifica'],
                 docs_consulted=1, model_calls=15, tool_calls=14, input_tokens=67974,
                 output_tokens=10448, failed_checks=2, elapsed=711.188, history=history)
    reserve_before = request_input_reserve(settings, history, INSTRUCTIONS, TOOLS)
    client = AsyncGroq(api_key='offline-test-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: pytest.fail('Recovered valid backend needs no new inference'))))
    agent = Agent(settings, store, sandbox, client=client)
    try:
        result = await run_or_recheck(agent, store, sandbox, store.project(pid))
        assert store.files(pid)['main.py'] == main and result['state'] == 'Pronto'
        assert result['last_check']['check']['unit_tests'] == 8
        assert len(result['last_check']['check']['contract']) == 5
        assert result['model_calls'] == 15 and result['input_tokens'] == 67974 and result['output_tokens'] == 10448
        assert result['history'][:len(original)] == original
        assert result['elapsed'] > 711.188
        assert request_input_reserve(settings, result['history'], INSTRUCTIONS, TOOLS) < reserve_before
        event = next(event for event in store.events(pid) if event['kind'] == 'recupero_scrittura_ia')
        assert event['detail']['call_id'] == 'main_attempt' and event['detail']['model_called'] is False
        # Il rollback della scrittura recuperata rimane disponibile.
        version = store.rows('SELECT id FROM versions WHERE project_id=? AND path=?', (pid, 'main.py'))[0]['id']
        store.rollback(pid, version)
        assert 'main.py' not in store.files(pid) and store.project(pid)['verified_hash'] is None
    finally:
        await agent.shutdown()
        store.close()


def test_recovered_or_superseded_code_is_slimmed_but_newer_failed_changes_remain(tmp_path):
    source = 'prior recovered source\n' * 1000
    history = attempted_write('earlier source\n' * 1000, 'earlier') + attempted_write(source)
    marker = {'call_id': 'main_attempt', 'path': 'main.py', 'sha256': hashlib.sha256(source.encode()).hexdigest()}
    history.append({'role': 'user', 'content': 'System recovery recorded', '_recovered_file': marker})
    history += attempted_write('newer failed code must stay', 'latest', 'File troppo grande')
    original = copy.deepcopy(history)
    messages = groq_messages(history, 'Mandatory rules')
    arguments = {call['id']: call['function']['arguments'] for message in messages for call in message.get('tool_calls', [])}
    assert 'prior recovered source' not in arguments['main_attempt'] and 'earlier source' not in arguments['earlier']
    assert 'newer failed code must stay' in arguments['latest']
    assert history == original
    openai_payload = generation_payload(Settings(data_dir=tmp_path, provider='openai'), history, 'Rules')
    assert all('_recovered_file' not in item for item in openai_payload['input'])
    assert json.loads(openai_payload['input'][2]['arguments'])['content'] == source


def test_unmatched_recovery_hash_does_not_suppress_unsaved_code():
    history = attempted_write('must remain')
    history.append({'role': 'user', 'content': 'Unmatched record', '_recovered_file': {
        'call_id': 'main_attempt', 'path': 'main.py', 'sha256': '0' * 64}})
    messages = groq_messages(history, 'Rules')
    assert 'must remain' in messages[1]['tool_calls'][0]['function']['arguments']
