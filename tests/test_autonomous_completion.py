"""SDK ufficiali, HTTP simulato e Docker reale: prova del controller, non del modello."""
import asyncio
from dataclasses import replace
import json
from pathlib import Path

from groq import AsyncGroq
import httpx
from openai import AsyncOpenAI
import pytest

from app.agent import Agent
from app.config import Settings, load_settings
from app.sandbox import Sandbox
from app.storage import Store


def reply(provider, number, step):
    name, arguments = step
    text = 'Il progetto e\' completo.'
    if provider == 'groq':
        message = {'role': 'assistant', 'content': text}
        if name != 'plain':
            message = {'role': 'assistant', 'content': None, 'tool_calls': [{
                'id': f'call_{number}', 'type': 'function',
                'function': {'name': name, 'arguments': json.dumps(arguments)}}]}
        return {'id': f'chat_{number}', 'object': 'chat.completion', 'created': 1,
                'model': 'openai/gpt-oss-20b', 'choices': [{'index': 0,
                'finish_reason': 'stop' if name == 'plain' else 'tool_calls', 'message': message}],
                'usage': {'prompt_tokens': 100, 'completion_tokens': 20, 'total_tokens': 120}}
    output = [{'type': 'message', 'id': f'msg_{number}', 'role': 'assistant',
               'status': 'completed', 'content': [{'type': 'output_text', 'text': text, 'annotations': []}]}]
    if name != 'plain':
        output = [{'type': 'function_call', 'id': f'fc_{number}', 'call_id': f'call_{number}',
                   'name': name, 'arguments': json.dumps(arguments)}]
    return {'id': f'resp_{number}', 'object': 'response', 'created_at': 1,
            'model': 'gpt-5-mini', 'status': 'completed', 'output': output,
            'usage': {'input_tokens': 100, 'output_tokens': 20, 'total_tokens': 120,
            'input_tokens_details': {'cached_tokens': 0}, 'output_tokens_details': {'reasoning_tokens': 0}}}


@pytest.mark.parametrize('provider', ['groq', 'openai'])
@pytest.mark.parametrize('case', ['valid', 'repair', 'repeated_plain'])
async def test_premature_completion_checks_and_repairs_without_manual_resume(tmp_path, provider, case):
    settings = replace(load_settings(), data_dir=tmp_path, provider=provider, min_interval=0,
                       model='openai/gpt-oss-20b' if provider == 'groq' else 'gpt-5-mini', max_model_calls=3)
    sandbox = Sandbox(settings)
    status = await sandbox.status()
    if not status['available']:
        pytest.skip(status['reason'])
    root = Path(__file__).resolve().parents[1] / 'examples/activity_backend'
    files = {p.relative_to(root).as_posix(): p.read_text(encoding='utf-8')
             for p in root.rglob('*.py') if '__pycache__' not in p.parts}
    correct = files['main.py']
    if case != 'valid':
        files['main.py'] = correct.replace('or not title.strip() or', 'or')
    store = Store(tmp_path)
    pid = store.create_project('Fixture di riferimento per la ripresa autonoma del controller')['id']
    for name, content in files.items():
        store.write_file(pid, name, content)
    store.update(pid, criteria=['Test, API, validazione, idempotenza e riavvio'],
                 plan=['Implementa e verifica'], docs_consulted=1)
    original_tests = {name: value for name, value in files.items() if name.startswith('tests/')}
    requests = []

    def respond(request):
        requests.append(json.loads(request.content))
        if len(requests) > 1:
            assert 'Continua autonomamente con gli strumenti' in str(requests[-1])
            assert '"passed": false' in json.dumps(requests[-1], ensure_ascii=False).replace('\\"', '"')
        step = ('plain', {})
        if case == 'repair' and len(requests) == 2:
            step = ('write_file', {'path': 'main.py', 'content': correct})
        assert len(requests) <= 3, 'La ripresa deve rispettare il limite complessivo di chiamate'
        return httpx.Response(200, json=reply(provider, len(requests), step))

    sdk = AsyncGroq if provider == 'groq' else AsyncOpenAI
    client = sdk(api_key='offline-only', max_retries=0,
                 http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    agent = Agent(settings, store, sandbox, client=client)
    try:
        await agent.run(pid)
        result = store.project(pid)
        assert {name: store.files(pid)[name] for name in original_tests} == original_tests
        expected_calls = 1 if case == 'valid' else 3
        assert result['model_calls'] == len(requests) == expected_calls
        assert result['input_tokens'] == expected_calls * 100
        assert result['output_tokens'] == expected_calls * 20
        checks = [e['detail'] for e in reversed(store.events(pid)) if e['kind'] == 'verifica']
        assert len(checks) == (2 if case == 'repair' else 1)
        if case == 'repeated_plain':
            assert result['state'] == 'Serve il tuo intervento'
            assert 'Limite di chiamate' in result['summary']
            assert result['verified_hash'] is None and result['failed_checks'] == 1
            assert not checks[0]['passed']
        else:
            assert result['state'] == 'Pronto', result['summary']
            assert result['verified_hash'] == store.digest(pid)
            assert result['last_check']['check']['unit_tests'] == 8
            assert len(result['last_check']['check']['contract']) == 5
            assert checks[-1]['passed']
            if case == 'repair':
                assert not checks[0]['passed'] and result['failed_checks'] == 1
        events = store.events(pid)
        assert sum(e['kind'] == 'proseguimento_automatico' for e in events) == (0 if case == 'valid' else 2 if case == 'repeated_plain' else 1)
    finally:
        await agent.shutdown()
        store.close()


@pytest.mark.parametrize('control', ['run', 'stop'])
async def test_automatic_final_checks_obey_pause_and_stop(tmp_path, control):
    checked = asyncio.Event()
    store = Store(tmp_path)
    pid = store.create_project('Prova offline dei controlli durante la verifica automatica')['id']
    store.write_file(pid, 'main.py', 'raise RuntimeError("do not execute on host")\n')
    store.update(pid, criteria=['Test e API'], plan=['Verifica'], docs_consulted=1)

    class PausingSandbox:
        async def status(self):
            return {'available': True}

        async def verify(self, files, owner):
            store.update(pid, control='pause')
            checked.set()
            return {'passed': True, 'exit_code': 0, 'timeout': False,
                    'check': {'unit_tests': 1, 'passed': True}}

    def respond(request):
        return httpx.Response(200, json=reply('groq', 1, ('plain', {})))

    client = AsyncGroq(api_key='offline-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    agent = Agent(Settings(data_dir=tmp_path, max_model_calls=1), store, PausingSandbox(), client=client)
    task = asyncio.create_task(agent.run(pid))
    try:
        await asyncio.wait_for(checked.wait(), 2)
        await asyncio.sleep(.02)
        assert not task.done() and store.project(pid)['state'] != 'Pronto'
        store.update(pid, control=control)
        await asyncio.wait_for(task, 2)
        result = store.project(pid)
        assert result['model_calls'] == 1
        assert result['state'] == ('Pronto' if control == 'run' else 'Serve il tuo intervento')
        assert result['tool_calls'] == (2 if control == 'run' else 1)
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await agent.shutdown()
        store.close()


async def test_genuine_question_still_waits_for_the_user_after_automatic_continuation(tmp_path):
    class AvailableSandbox:
        async def status(self):
            return {'available': True}

    requests = []

    def respond(request):
        requests.append(request)
        step = ('plain', {}) if len(requests) == 1 else ('ask_user', {'question': 'Quale servizio esterno devo integrare?'})
        return httpx.Response(200, json=reply('groq', len(requests), step))

    client = AsyncGroq(api_key='offline-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    store = Store(tmp_path)
    pid = store.create_project('Un requisito essenziale non ricavabile dai file')['id']
    agent = Agent(Settings(data_dir=tmp_path, max_model_calls=3), store, AvailableSandbox(), client=client)
    try:
        await agent.run(pid)
        result = store.project(pid)
        assert len(requests) == result['model_calls'] == 2
        assert result['state'] == 'Serve il tuo intervento'
        assert result['question'] == 'Quale servizio esterno devo integrare?'
        assert result['last_check'] is None
    finally:
        await agent.shutdown()
        store.close()


@pytest.mark.parametrize('limit', ['tools', 'corrections'])
async def test_automatic_continuation_does_not_spend_requests_after_operational_limits(tmp_path, limit):
    class FailedSandbox:
        async def status(self):
            return {'available': True}

        async def verify(self, files, owner):
            return {'passed': False, 'timeout': False, 'exit_code': 1,
                    'check': {'unit_tests': 1, 'unit_errors': 1, 'passed': False}}

    requests = []

    def respond(request):
        requests.append(request)
        assert limit == 'corrections' and len(requests) == 1
        return httpx.Response(200, json=reply('groq', len(requests), ('plain', {})))

    client = AsyncGroq(api_key='offline-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    store = Store(tmp_path)
    pid = store.create_project('Arresto rispettando i limiti operativi')['id']
    store.write_file(pid, 'main.py', 'raise RuntimeError("never execute on host")\n')
    store.update(pid, criteria=['API e test'], plan=['Verifica'], docs_consulted=1,
                 tool_calls=3 if limit == 'tools' else 0)
    settings = Settings(data_dir=tmp_path, max_model_calls=3, max_tool_calls=3, max_corrections=0)
    agent = Agent(settings, store, FailedSandbox(), client=client)
    try:
        await agent.run(pid)
        result = store.project(pid)
        assert len(requests) == result['model_calls'] == (0 if limit == 'tools' else 1)
        assert result['state'] == 'Serve il tuo intervento'
        assert ('Limite di operazioni' if limit == 'tools' else 'Limite di correzioni') in result['summary']
        assert result['verified_hash'] is None
    finally:
        await agent.shutdown()
        store.close()
