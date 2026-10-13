"""SDK Groq reale e HTTP simulato: recupero del protocollo, non capacità del modello."""
import json

from groq import AsyncGroq
import httpx
import pytest

from app.agent import Agent
from app.config import Settings
from app.storage import Store


class OfflineSandbox:
    async def status(self):
        return {'available': True}

    async def stop(self, owner):
        pass


def tool_response(name, args, number=1):
    return httpx.Response(200, json={
        'id': f'chat_{number}', 'object': 'chat.completion', 'created': 1,
        'model': 'openai/gpt-oss-20b', 'choices': [{
            'index': 0, 'finish_reason': 'tool_calls',
            'message': {'role': 'assistant', 'content': None, 'tool_calls': [{
                'id': f'call_{number}', 'type': 'function',
                'function': {'name': name, 'arguments': json.dumps(args)}}]}}],
        'usage': {'prompt_tokens': 20, 'completion_tokens': 10, 'total_tokens': 30}})


async def test_invalid_tool_generation_retries_once_with_changed_prompt_and_temperature(tmp_path):
    requests = []
    private = 'gsk_test-value-never-log'

    def respond(request):
        requests.append(json.loads(request.content))
        if len(requests) == 2:
            return tool_response('ask_user', {'question': 'Verifica del protocollo conclusa?'})
        return httpx.Response(400, json={'error': {
            'code': 'tool_use_failed', 'message': f'Failed to call a function: {private}',
            'failed_generation': f'write_file(path="outside", content="{private}")'}})

    client = AsyncGroq(api_key='offline-test-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    store = Store(tmp_path)
    agent = Agent(Settings(data_dir=tmp_path), store, OfflineSandbox(), client=client)
    project = store.create_project('Backend locale')
    store.write_file(project['id'], 'README.md', 'Lavoro preesistente conservato')
    original = store.digest(project['id'])
    try:
        await agent.run(project['id'])
        result = store.project(project['id'])
        assert result['model_calls'] == 2 and result['question']
        assert requests[0]['temperature'] == 0.4 and requests[1]['temperature'] == 0.2
        assert 'una sola chiamata' in requests[1]['messages'][-1]['content']
        assert requests[1]['parallel_tool_calls'] is False
        assert store.digest(project['id']) == original
        assert private not in json.dumps(store.events(project['id']))
        assert private not in json.dumps(result['history'])
        assert len(store.rows("SELECT id FROM events WHERE kind='recupero_formato_tool'")) == 1
        # Riprendi conserva sia il contatore sia il tentativo di recupero esaurito.
        await agent.run(project['id'])
        result = store.project(project['id'])
        assert len(requests) == result['model_calls'] == 3
        assert 'HTTP 400' in result['summary'] and 'strumento non valida' in result['summary']
        assert len(store.rows("SELECT id FROM events WHERE kind='recupero_formato_tool'")) == 1
        assert store.digest(project['id']) == original
    finally:
        await agent.shutdown()
        store.close()


async def test_documented_failed_generation_shape_recovers_without_executing_it(tmp_path):
    requests = []

    def respond(request):
        requests.append(json.loads(request.content))
        if len(requests) == 1:
            return httpx.Response(400, json={'error': {
                'message': 'Invalid tool call generated', 'type': 'invalid_request_error',
                'failed_generation': {'reason': 'Tool call arguments are not valid JSON',
                                      'attempted_arguments': "{'path': 'main.py'}"}}})
        return tool_response('ask_user', {'question': 'Test concluso?'})

    client = AsyncGroq(api_key='offline-test-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    store = Store(tmp_path)
    agent = Agent(Settings(data_dir=tmp_path), store, OfflineSandbox(), client=client)
    project = store.create_project('Backend locale')
    try:
        await agent.run(project['id'])
        assert len(requests) == 2
        assert store.files(project['id']) == {}
        error = next(e for e in store.events(project['id']) if e['kind'] == 'errore_provider')
        assert error['detail']['diagnostic'] == {'category': 'invalid_tool_call'}
        assert 'attempted_arguments' not in json.dumps(store.events(project['id']))
    finally:
        await agent.shutdown()
        store.close()


@pytest.mark.parametrize('body,category,parameter', [
    ({'error': {'code': 'unsupported_parameter', 'param': 'parallel_tool_calls',
                'message': 'Unsupported parameter; private-value'}}, 'invalid_parameter', 'parallel_tool_calls'),
    ({'error': {'code': 'context_length_exceeded', 'message': 'Context length exceeded; private-value'}}, 'context_too_large', None),
    ({'error': {'message': 'messages: tool_call_id not found; private-value'}}, 'invalid_history', None),
    ({'error': {'code': 'private-value', 'param': 'private-value', 'message': 'private-value',
                'failed_generation': 'private-value'}}, 'bad_request', None),
    ('private-value', 'bad_request', None),
])
async def test_other_400_errors_stop_once_and_only_store_safe_diagnostics(tmp_path, body, category, parameter):
    requests = []

    def respond(request):
        requests.append(request.url.host)
        return httpx.Response(400, json=body)

    client = AsyncGroq(api_key='offline-test-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    store = Store(tmp_path)
    agent = Agent(Settings(data_dir=tmp_path), store, OfflineSandbox(), client=client)
    project = store.create_project('Backend locale')
    try:
        await agent.run(project['id'])
        result = store.project(project['id'])
        assert requests == ['api.groq.com'] and result['model_calls'] == 1
        assert result['state'] == 'Serve il tuo intervento' and result['verified_hash'] is None
        assert 'HTTP 400' in result['summary']
        error = next(e for e in store.events(project['id']) if e['kind'] == 'errore_provider')
        assert error['detail']['diagnostic']['category'] == category
        assert error['detail']['diagnostic'].get('parameter') == parameter
        assert 'private-value' not in json.dumps(store.events(project['id']))
        assert not store.rows("SELECT id FROM events WHERE kind='recupero_formato_tool'")
    finally:
        await agent.shutdown()
        store.close()


async def test_format_recovery_never_exceeds_model_call_budget(tmp_path):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(400, json={'error': {'code': 'tool_use_failed'}})

    client = AsyncGroq(api_key='offline-test-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    store = Store(tmp_path)
    agent = Agent(Settings(data_dir=tmp_path, max_model_calls=1), store, OfflineSandbox(), client=client)
    project = store.create_project('Backend locale')
    try:
        await agent.run(project['id'])
        assert len(requests) == store.project(project['id'])['model_calls'] == 1
        assert not store.rows("SELECT id FROM events WHERE kind='recupero_formato_tool'")
    finally:
        await agent.shutdown()
        store.close()


async def test_resume_after_historical_400_recovers_missing_documentation_without_reset(tmp_path):
    requests = []

    def respond(request):
        requests.append(json.loads(request.content))
        if len(requests) == 1:
            return tool_response('search_knowledge', {'query': 'SQLite'}, 1)
        return tool_response('ask_user', {'question': 'Test concluso?'}, 2)

    client = AsyncGroq(api_key='offline-test-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    store = Store(tmp_path)
    store.add_document('SQLite', 'https://docs.python.org/3.12/library/sqlite3.html', '2026-10-13', 'SQLite transazioni e persistenza')
    agent = Agent(Settings(data_dir=tmp_path), store, OfflineSandbox(), client=client)
    project = store.create_project('Backend locale')
    store.update(project['id'], model_calls=8, failed_checks=1,
        summary='Il provider ha risposto HTTP 400. Nessuna riuscita dichiarata.',
        history=[{'role': 'user', 'content': 'Backend locale'}])
    try:
        await agent.run(project['id'])
        result = store.project(project['id'])
        assert requests[0]['temperature'] == 0.2
        assert 'documentazione non è ancora riuscita' in requests[0]['messages'][-1]['content']
        assert result['model_calls'] == 10 and result['failed_checks'] == 1
        assert result['docs_consulted'] == 1
        assert result['state'] == 'Serve il tuo intervento'
    finally:
        await agent.shutdown()
        store.close()
