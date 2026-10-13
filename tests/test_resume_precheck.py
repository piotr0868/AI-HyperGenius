"""File di riferimento scritti per i test, Docker reale e SDK HTTP simulato."""
from dataclasses import replace
import json
from pathlib import Path

from groq import AsyncGroq
import httpx
import pytest

from app.agent import Agent
from app.config import load_settings
from app.sandbox import Sandbox
from app.storage import Store
from scripts.prova_agente import run_or_recheck


@pytest.mark.parametrize('case', ['valid', 'zero_tests', 'invalid_validation'])
async def test_resume_checks_saved_files_before_model_and_never_accepts_missing_or_failed_tests(tmp_path, case):
    settings = replace(load_settings(), data_dir=tmp_path, min_interval=0, max_model_calls=20)
    sandbox = Sandbox(settings)
    status = await sandbox.status()
    if not status['available']:
        pytest.skip(status['reason'])
    root = Path(__file__).resolve().parent.parent / 'examples/activity_backend'
    files = {p.relative_to(root).as_posix(): p.read_text(encoding='utf-8')
             for p in root.rglob('*.py') if '__pycache__' not in p.parts}
    if case == 'zero_tests':
        files = {'main.py': files['main.py'], 'tests/test_empty.py': 'import unittest\n'}
    elif case == 'invalid_validation':
        files['main.py'] = files['main.py'].replace('or not title.strip() or', 'or')
    store = Store(tmp_path)
    project = store.create_project('Backend attività: fixture, non generazione IA reale')
    pid = project['id']
    for name, content in files.items():
        store.write_file(pid, name, content)
    store.update(pid, state='Serve il tuo intervento', model_calls=14, tool_calls=12,
                 input_tokens=60306, output_tokens=8853, failed_checks=1, elapsed=646,
                 criteria=['API, validazione, idempotenza, persistenza'], plan=['Verifica i file salvati'],
                 docs_consulted=1, history=[{'role': 'user', 'content': 'Riprendi il backend'}])
    digest = store.digest(pid)
    requests = []

    def respond(request):
        payload = json.loads(request.content)
        requests.append(payload)
        assert any('verifica automatica' in (message.get('content') or '').lower()
                   for message in payload['messages'])
        return httpx.Response(200, json={
            'id': 'chat_precheck', 'object': 'chat.completion', 'created': 1,
            'model': settings.model, 'choices': [{'index': 0, 'finish_reason': 'tool_calls',
                'message': {'role': 'assistant', 'content': None, 'tool_calls': [{
                    'id': 'ask', 'type': 'function', 'function': {'name': 'ask_user',
                    'arguments': '{"question":"Test del protocollo concluso?"}'}}]}}],
            'usage': {'prompt_tokens': 20, 'completion_tokens': 10, 'total_tokens': 30}})

    client = AsyncGroq(api_key='offline-test-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    agent = Agent(settings, store, sandbox, client=client)
    try:
        result = await run_or_recheck(agent, store, sandbox, store.project(pid))
        assert store.digest(pid) == digest
        assert result['elapsed'] > 646
        if case == 'valid':
            assert result['state'] == 'Pronto' and result['verified_hash'] == digest
            assert result['last_check']['check']['unit_tests'] == 8
            assert len(result['last_check']['check']['contract']) == 5
            assert requests == [] and result['model_calls'] == 14
            assert result['input_tokens'] == 60306 and result['output_tokens'] == 8853
            assert result['failed_checks'] == 1
            certificate = next(e for e in store.events(pid) if e['kind'] == 'certificazione_automatica')
            assert certificate['detail']['actor'] == 'system' and certificate['detail']['model_called'] is False
        else:
            assert result['state'] == 'Serve il tuo intervento' and result['verified_hash'] is None
            assert result['last_check']['passed'] is False and result['failed_checks'] == 2
            assert len(requests) == 1 and result['model_calls'] == 15
            assert not any(e['kind'] == 'certificazione_automatica' for e in store.events(pid))
            if case == 'zero_tests':
                assert result['last_check']['check']['unit_tests'] == 0
    finally:
        await agent.shutdown()
        store.close()
