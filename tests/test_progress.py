"""Scritture ripetute: SDK HTTP simulato, controlli reali; nessuna riuscita IA inventata."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path

from groq import AsyncGroq
import httpx
from openai import AsyncOpenAI
import pytest

from app.agent import Agent
from app.config import Settings, load_settings
from app.progress import TEST_PATH, prepare_contract_checks, system_checks_active
from app.sandbox import Sandbox
from app.storage import Store

ROOT = Path(__file__).resolve().parents[1]


def ready_to_work(store, pid):
    store.update(pid, criteria=['API, validazione, idempotenza e persistenza'],
                 plan=['Implementa e verifica'], docs_consulted=1)


@pytest.mark.parametrize('faulty', [False, True])
async def test_exhausted_project_gets_real_http_tests_without_new_model_or_backend_changes(tmp_path, faulty):
    settings = replace(load_settings(), data_dir=tmp_path, min_interval=0)
    sandbox = Sandbox(settings)
    state = await sandbox.status()
    if not state['available']:
        pytest.skip(state['reason'])
    code = (ROOT / 'examples/activity_backend/main.py').read_text()
    if faulty:
        code = code.replace('or not title.strip() or', 'or')
    store = Store(tmp_path)
    pid = store.create_project('Riproduzione della prova Windows: main ripetuto, test mancanti')['id']
    store.write_file(pid, 'main.py', '# previous version\n' + code)
    store.write_file(pid, 'main.py', code)
    ready_to_work(store, pid)
    store.update(pid, model_calls=12, tool_calls=14, input_tokens=3000, output_tokens=500,
                 elapsed=700, failed_checks=1)

    def forbidden(request):
        pytest.fail('La ripresa al limite non puo\' generare nuove richieste IA')

    client = AsyncGroq(api_key='offline-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(forbidden)))
    agent = Agent(settings, store, sandbox, client=client)
    try:
        await agent.run(pid)
        result = store.project(pid)
        assert store.files(pid)['main.py'] == code
        assert result['model_calls'] == 12 and result['input_tokens'] == 3000 and result['output_tokens'] == 500
        assert result['elapsed'] >= 700
        assert result['last_check']['check']['unit_tests'] == 5
        assert result['last_check']['passed'] is not faulty
        records = [e['detail'] for e in store.events(pid) if e['kind'] == 'file_sistema']
        assert {record['path'] for record in records} == {TEST_PATH, 'tests/__init__.py', 'README.md'}
        assert all(record['actor'] == 'system' and record['model_called'] is False for record in records)
        assert 'non dal modello' in store.files(pid)['README.md']
        if faulty:
            assert result['state'] == 'Serve il tuo intervento' and result['verified_hash'] is None
            assert result['failed_checks'] == 2
        else:
            assert result['state'] == 'Pronto' and result['verified_hash'] == store.digest(pid)
            assert 'predisposti dal sistema' in result['summary']
            assert len(result['last_check']['check']['contract']) == 5
            assert result['failed_checks'] == 1
        checks_before = sum(e['kind'] == 'verifica' for e in store.events(pid))
        await agent.run(pid)
        assert sum(e['kind'] == 'verifica' for e in store.events(pid)) == checks_before
        assert store.files(pid)['main.py'] == code
    finally:
        await agent.shutdown()
        store.close()


@pytest.mark.parametrize('provider', ['groq', 'openai'])
@pytest.mark.parametrize('repair', [False, True])
async def test_repeated_write_switches_to_checks_and_meaningful_correction(tmp_path, provider, repair):
    from tests.test_autonomous_completion import reply
    settings = replace(load_settings(), data_dir=tmp_path, provider=provider, min_interval=0,
                       model='openai/gpt-oss-20b' if provider == 'groq' else 'gpt-5-mini')
    sandbox = Sandbox(settings)
    state = await sandbox.status()
    if not state['available']:
        pytest.skip(state['reason'])
    correct = (ROOT / 'examples/activity_backend/main.py').read_text()
    source = correct.replace('or not title.strip() or', 'or') if repair else correct
    store = Store(tmp_path)
    pid = store.create_project('Fixture: il modello insiste sullo stesso main.py')['id']
    store.write_file(pid, 'main.py', source)
    ready_to_work(store, pid)
    requests = []

    def respond(request):
        requests.append(json.loads(request.content))
        assert len(requests) <= (2 if repair else 1)
        if len(requests) == 2:
            assert 'Il sistema ha verificato il backend' in str(requests[-1])
            if provider == 'groq':
                assert '[Contenuto archiviato:' in str(requests[-1])
        code = correct if repair and len(requests) == 2 else source
        return httpx.Response(200, json=reply(provider, len(requests), ('write_file', {'path': 'main.py', 'content': code})))

    sdk = AsyncGroq if provider == 'groq' else AsyncOpenAI
    client = sdk(api_key='offline-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    agent = Agent(settings, store, sandbox, client=client)
    try:
        await agent.run(pid)
        result = store.project(pid)
        assert result['state'] == 'Pronto', result['summary']
        assert result['model_calls'] == len(requests) == (2 if repair else 1)
        assert result['input_tokens'] == len(requests) * 100 and result['output_tokens'] == len(requests) * 20
        assert store.files(pid)['main.py'] == correct
        assert len(store.rows("SELECT id FROM versions WHERE project_id=? AND path='main.py'", (pid,))) == (2 if repair else 1)
        assert result['last_check']['check']['unit_tests'] == 5
        assert result['failed_checks'] == int(repair)
        assert system_checks_active(store, pid)
        before = store.files(pid)[TEST_PATH]
        for protected in (TEST_PATH, 'tests//test_officina_contract.py', './tests/test_officina_contract.py',
                          'tests/TEST_OFFICINA_CONTRACT.PY'):
            with pytest.raises(ValueError, match='protetti'):
                await agent.perform(pid, 'write_file', {'path': protected, 'content': '# remove tests\n'})
        assert store.files(pid)[TEST_PATH] == before
    finally:
        await agent.shutdown()
        store.close()


@pytest.mark.parametrize('case', ['existing_tests', 'deleted_tests', 'no_docs', 'no_plan', 'pause', 'stop',
                                 'tool_limit', 'time_limit', 'correction_limit', 'not_stalled', 'existing_readme'])
async def test_system_checks_preserve_user_work_controls_and_budgets(tmp_path, case):
    store = Store(tmp_path)
    pid = store.create_project('Preparazione controllata, senza esecuzione del codice')['id']
    store.write_file(pid, 'main.py', 'raise RuntimeError("never execute on host")\n')
    if case != 'not_stalled':
        store.write_file(pid, 'main.py', 'raise RuntimeError("another saved version; still never execute on host")\n')
    ready_to_work(store, pid)
    if case in ('existing_tests', 'deleted_tests'):
        store.write_file(pid, 'tests/test_existing.py', '# preserve original test file\n')
        if case == 'deleted_tests':
            store.safe_path(pid, 'tests/test_existing.py').unlink()
    if case == 'existing_readme':
        store.write_file(pid, 'README.md', 'Istruzioni dell’utente: conservare.\n')
    if case == 'no_docs':
        store.update(pid, docs_consulted=0)
    if case == 'no_plan':
        store.update(pid, plan=[])
    if case in ('pause', 'stop'):
        store.update(pid, control=case)
    if case == 'tool_limit':
        store.update(pid, tool_calls=38)
    if case == 'time_limit':
        store.update(pid, elapsed=1200)
    if case == 'correction_limit':
        store.update(pid, failed_checks=4)
    agent = Agent(Settings(data_dir=tmp_path), store, None)
    original = store.files(pid)
    try:
        created = await prepare_contract_checks(agent, pid, remaining=100)
        assert created == (case == 'existing_readme')
        assert all(store.files(pid)[name] == value for name, value in original.items())
        assert store.project(pid)['model_calls'] == 0
        if not created:
            assert store.files(pid) == original
    finally:
        await agent.shutdown()
        store.close()


async def test_identical_write_keeps_version_and_verified_hash(tmp_path):
    store = Store(tmp_path)
    pid = store.create_project('Scrittura identica senza invalidare le prove')['id']
    ready_to_work(store, pid)
    store.write_file(pid, 'main.py', '# saved source\n')
    digest = store.digest(pid)
    store.update(pid, verified_hash=digest)
    agent = Agent(Settings(data_dir=tmp_path), store, None)
    try:
        result = await agent.perform(pid, 'write_file', {'path': 'main.py', 'content': '# saved source\n'})
        assert result['unchanged'] is True
        assert store.project(pid)['verified_hash'] == digest
        assert len(store.rows('SELECT id FROM versions WHERE project_id=?', (pid,))) == 1
        assert store.project(pid)['tool_calls'] == 1
    finally:
        await agent.shutdown()
        store.close()
