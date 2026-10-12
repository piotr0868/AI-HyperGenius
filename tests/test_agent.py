"""Test offline del protocollo e dei limiti: provider simulato, nessuna capacità IA certificata."""
import asyncio
import json
from dataclasses import replace
import httpx
from openai import AsyncOpenAI
import pytest

from app.agent import Agent, NeedsIntervention, preflight, repair_history
from app.config import Settings
from app.storage import Store


class OfflineSandbox:
    async def status(self):
        return {'available': True}
    async def stop(self, owner):
        pass


@pytest.fixture
def agent(tmp_path):
    store = Store(tmp_path)
    agent = Agent(Settings(data_dir=tmp_path), store, OfflineSandbox())
    yield agent
    store.close()


async def test_cannot_write_before_plan_and_references(agent):
    p = agent.store.create_project('Progetto di test')
    with pytest.raises(ValueError, match='Prima salva'):
        await agent.perform(p['id'], 'write_file', {'path': 'main.py', 'content': 'print(1)'})
    assert agent.store.files(p['id']) == {}


async def test_ready_requires_current_successful_proof(agent):
    p = agent.store.create_project('Progetto di test')
    pid = p['id']
    with pytest.raises(ValueError, match='mancanti'):
        await agent.perform(pid, 'finish', {'summary': 'Pronto', 'next_step': 'Prova'})
    agent.store.write_file(pid, 'main.py', 'old')
    agent.store.update(pid, criteria=['criterio'], docs_consulted=1,
        last_check={'passed': True, 'check': {'unit_tests': 2}}, verified_hash=agent.store.digest(pid))
    agent.store.write_file(pid, 'main.py', 'new')
    with pytest.raises(ValueError, match='File cambiati'):
        await agent.perform(pid, 'finish', {'summary': 'Pronto', 'next_step': 'Prova'})


def test_budgets_reject_before_call(agent):
    p = agent.store.create_project('Progetto di test')
    p['model_calls'] = 12
    with pytest.raises(NeedsIntervention, match='chiamate'):
        preflight(agent.settings, p, [])
    p['model_calls'] = 0
    with pytest.raises(NeedsIntervention, match='Budget token'):
        preflight(replace(agent.settings, max_total_tokens=1000), p, [])
    with pytest.raises(NeedsIntervention, match='prezzi'):
        preflight(replace(agent.settings, max_cost=1), p, [])
    with pytest.raises(NeedsIntervention, match='costo'):
        preflight(replace(agent.settings, max_cost=0, input_rate=1, output_rate=1), p, [])


def test_interrupted_tool_history_is_repaired():
    history = [{'type': 'function_call', 'call_id': 'c1', 'name': 'write_file', 'arguments': '{}'}]
    repaired = repair_history(history)
    assert repaired[-1]['call_id'] == 'c1'
    assert json.loads(repaired[-1]['output'])['interrupted']
    assert len(repair_history(repaired)) == 2


async def test_pause_blocks_next_operation_until_resume(agent):
    p = agent.store.create_project('Progetto di test')
    agent.store.update(p['id'], control='pause')
    task = asyncio.create_task(agent.checkpoint(p['id']))
    await asyncio.sleep(.03)
    assert not task.done()
    agent.store.update(p['id'], control='run')
    await asyncio.wait_for(task, 1)


async def test_official_sdk_function_call_protocol_and_usage(tmp_path):
    """SDK vero, trasporto HTTP simulato: controlla JSON e orchestrazione, non il modello."""
    requests = []
    def respond(request):
        payload = json.loads(request.content)
        requests.append(payload)
        return httpx.Response(200, json={
            'id': 'resp_offline', 'object': 'response', 'created_at': 1, 'model': 'gpt-5-mini',
            'status': 'completed', 'output': [{'type': 'function_call', 'id': 'fc_test',
                'call_id': 'call_test', 'name': 'ask_user', 'arguments': '{"question":"Quale risultato è indispensabile?"}'}],
            'usage': {'input_tokens': 100, 'output_tokens': 20, 'total_tokens': 120,
                'input_tokens_details': {'cached_tokens': 0}, 'output_tokens_details': {'reasoning_tokens': 0}}})
    client = AsyncOpenAI(api_key='offline-test-only', http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    store = Store(tmp_path)
    agent = Agent(Settings(data_dir=tmp_path, provider="openai", model="gpt-5-mini"), store, OfflineSandbox(), client=client)
    p = store.create_project('Backend con API')
    await agent.run(p['id'])
    result = store.project(p['id'])
    assert result['state'] == 'Serve il tuo intervento'
    assert result['question'] == 'Quale risultato è indispensabile?'
    assert result['input_tokens'] == 100 and result['output_tokens'] == 20
    assert requests[0]['store'] is False and requests[0]['parallel_tool_calls'] is False
    assert requests[0]['tools'][0]['strict'] is True
    assert result['history'][-1]['type'] == 'function_call_output'
    await agent.shutdown()
    store.close()


@pytest.mark.parametrize('provider', ['openai', 'groq'])
async def test_offline_protocol_drives_real_docker_failure_repair_and_retest(tmp_path, provider):
    """Chiamate predisposte dal test, SDK vero e Docker vero: non è una prova del modello."""
    from pathlib import Path
    from app.config import load_settings
    from app.sandbox import Sandbox
    settings = replace(load_settings(), data_dir=tmp_path, provider=provider,
                       model='gpt-5-mini' if provider == 'openai' else 'openai/gpt-oss-20b', min_interval=0)
    sandbox = Sandbox(settings)
    if not (await sandbox.status())['available']:
        pytest.skip('Docker non disponibile: protocollo con esecuzione reale non verificato.')
    root = Path(__file__).resolve().parent.parent / 'examples' / 'activity_backend'
    source = (root / 'main.py').read_text()
    faulty = source.replace('or not title.strip() or', 'or')
    calls = iter([
        ('record_plan', {'outcome': 'Backend attività', 'criteria': ['API, idempotenza, riavvio'], 'steps': ['Crea e verifica']}),
        ('search_knowledge', {'query': 'SQLite'}),
        ('write_file', {'path': 'main.py', 'content': faulty}),
        ('write_file', {'path': 'tests/test_activities.py', 'content': (root / 'tests/test_activities.py').read_text()}),
        ('run_checks', {}), ('write_file', {'path': 'main.py', 'content': source}),
        ('run_checks', {}), ('finish', {'summary': 'Riferimento verificato con protocollo offline.', 'next_step': 'Prova API'})])
    sent = []
    def respond(request):
        sent.append(json.loads(request.content))
        name, args = next(calls)
        if provider == 'groq':
            assert request.url.host == 'api.groq.com'
            assert sent[-1]['parallel_tool_calls'] is False
            assert 'store' not in sent[-1] and 'max_output_tokens' not in sent[-1]
            assert 'strict' not in sent[-1]['tools'][0]['function']
            return httpx.Response(200, json={'id': f'chat_{len(sent)}', 'object': 'chat.completion', 'created': 1,
                'model': settings.model, 'choices': [{'index': 0, 'finish_reason': 'tool_calls',
                'message': {'role': 'assistant', 'content': None, 'tool_calls': [{'id': f'call_{len(sent)}',
                    'type': 'function', 'function': {'name': name, 'arguments': json.dumps(args)}}]}}],
                'usage': {'prompt_tokens': 100, 'completion_tokens': 20, 'total_tokens': 120}})
        return httpx.Response(200, json={'id': f'resp_{len(sent)}', 'object': 'response', 'created_at': 1,
            'model': settings.model, 'status': 'completed', 'output': [{'type': 'function_call', 'id': f'fc_{len(sent)}',
            'call_id': f'call_{len(sent)}', 'name': name, 'arguments': json.dumps(args)}],
            'usage': {'input_tokens': 100, 'output_tokens': 20, 'total_tokens': 120,
            'input_tokens_details': {'cached_tokens': 0}, 'output_tokens_details': {'reasoning_tokens': 0}}})
    from groq import AsyncGroq
    sdk = AsyncGroq if provider == 'groq' else AsyncOpenAI
    client = sdk(api_key='offline-test-only', max_retries=0, http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    store = Store(tmp_path)
    store.add_document('SQLite', 'https://docs.python.org/3.12/library/sqlite3.html', '2026-10-12', 'SQLite transazioni e idempotenza.')
    agent = Agent(settings, store, sandbox, client=client)
    p = store.create_project('Crea il backend di riferimento tramite protocollo offline.')
    await agent.run(p['id'])
    result = store.project(p['id'])
    assert result['state'] == 'Pronto', result['summary']
    assert result['model_calls'] == 8 and result['tool_calls'] == 8
    assert result['verified_hash'] == store.digest(p['id'])
    checks = [e['detail'] for e in reversed(store.events(p['id'])) if e['kind'] == 'verifica']
    assert checks[0]['passed'] is False and checks[-1]['passed'] is True
    assert result['failed_checks'] == 1
    if provider == 'openai':
        assert any(json.loads(i['output']).get('passed') is False for i in sent[5]['input'] if i.get('type') == 'function_call_output')
    else:
        assert any(json.loads(i['content']).get('passed') is False for i in sent[5]['messages'] if i.get('role') == 'tool')
    await agent.shutdown()
    store.close()


async def test_groq_rate_limit_stops_without_paid_fallback(tmp_path):
    from groq import AsyncGroq
    requests = []
    def respond(request):
        requests.append(request.url.host)
        return httpx.Response(429, headers={'Retry-After': '7'}, json={'error': {'message': 'Quota reached', 'type': 'rate_limit_error'}})
    client = AsyncGroq(api_key='offline-test-only', max_retries=0,
                       http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    store = Store(tmp_path)
    agent = Agent(Settings(data_dir=tmp_path), store, OfflineSandbox(), client=client)
    p = store.create_project('Backend con quota gratuita')
    await agent.run(p['id'])
    row = store.project(p['id'])
    assert row['state'] == 'Serve il tuo intervento'
    assert 'Quota API raggiunta' in row['summary'] and '7 secondi' in row['summary']
    assert requests == ['api.groq.com'] and row['model_calls'] == 1
    await agent.shutdown()
    store.close()


async def test_tool_arguments_are_validated_on_host(agent):
    p = agent.store.create_project('Test argomenti non fidati')
    for name, args in [('execute_python', {'argv': 'python -c evil'}),
                       ('read_file', {'path': 'main.py', 'unexpected': 'ignore rules'}),
                       ('unknown_tool', {})]:
        with pytest.raises(ValueError):
            await agent.perform(p['id'], name, args)
    assert agent.store.project(p['id'])['tool_calls'] == 0


async def test_stop_cancels_inflight_request_and_preserves_project(tmp_path):
    entered = asyncio.Event()
    async def respond(request):
        entered.set()
        await asyncio.Event().wait()
    client = AsyncOpenAI(api_key='offline-test-only', http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    store = Store(tmp_path)
    agent = Agent(Settings(data_dir=tmp_path, provider="openai", model="gpt-5-mini"), store, OfflineSandbox(), client=client)
    p = store.create_project('Progetto da interrompere')
    agent.launch(p['id'])
    await asyncio.wait_for(entered.wait(), 2)
    await agent.stop(p['id'])
    assert agent.tasks[p['id']].done()
    assert store.project(p['id'])['state'] == 'Serve il tuo intervento'
    assert store.project(p['id'])['model_calls'] == 1
    await agent.shutdown()
    store.close()
