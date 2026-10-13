"""Riserva basata sulla richiesta SDK; nessuna API reale o aumento dei limiti."""
import copy
import json

from groq import AsyncGroq
import httpx
import pytest

from app.agent import Agent, INSTRUCTIONS, TOOLS, NeedsIntervention, preflight, token_budget
from app.config import Settings
from app.providers import generation_payload
from app.storage import Store


class OfflineSandbox:
    async def status(self):
        return {'available': True}

    async def stop(self, owner):
        pass


def large_history(succeeded=True):
    return [
        {'role': 'user', 'content': 'Crea un backend attività'},
        {'type': 'function_call', 'call_id': 'saved', 'name': 'write_file',
         'arguments': json.dumps({'path': 'main.py', 'content': '# existing code\n' * 4000})},
        {'type': 'function_call_output', 'call_id': 'saved',
         'output': json.dumps({'path': 'main.py', 'previous_version': 1} if succeeded else {'error': 'not saved'})}]


async def test_compacted_request_fits_budget_without_erasing_history_or_usage(tmp_path):
    history = large_history()
    original = copy.deepcopy(history)
    settings = Settings(data_dir=tmp_path, max_total_tokens=30000, max_output_tokens=3000)
    store = Store(tmp_path)
    project = store.create_project('Backend attività')
    store.update(project['id'], history=history, input_tokens=1000, output_tokens=500,
                 model_calls=8, docs_consulted=1)
    row = store.project(project['id'])
    # Il precedente calcolo sulla memoria integrale avrebbe bloccato questa richiesta.
    old_reserve = len(json.dumps(history, ensure_ascii=False).encode()) + len(INSTRUCTIONS.encode()) + len(json.dumps(TOOLS).encode()) + 4096
    assert row['input_tokens'] + row['output_tokens'] + old_reserve + settings.max_output_tokens > settings.max_total_tokens
    budget = token_budget(settings, row, history)
    assert budget['required_tokens'] < settings.max_total_tokens
    preflight(settings, row, history)
    expected_history = original + [{'role': 'user', 'content': 'Riprendi il lavoro dai file salvati e dalle prove. Non presumere operazioni riuscite.'}]
    expected_budget = token_budget(settings, row, expected_history)
    sent = []

    def respond(request):
        sent.append(request.content)
        payload = json.loads(request.content)
        assert payload == generation_payload(settings, expected_history, INSTRUCTIONS, TOOLS)
        assert len(request.content) <= expected_budget['reserved_input_tokens'] - 4096
        return httpx.Response(200, json={
            'id': 'chat_budget', 'object': 'chat.completion', 'created': 1,
            'model': settings.model, 'choices': [{'index': 0, 'finish_reason': 'tool_calls',
                'message': {'role': 'assistant', 'content': None, 'tool_calls': [{
                    'id': 'ask', 'type': 'function', 'function': {'name': 'ask_user',
                    'arguments': '{"question":"Verifica del protocollo conclusa?"}'}}]}}],
            'usage': {'prompt_tokens': 20, 'completion_tokens': 10, 'total_tokens': 30}})

    client = AsyncGroq(api_key='offline-test-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
    agent = Agent(settings, store, OfflineSandbox(), client=client)
    try:
        await agent.run(project['id'])
        result = store.project(project['id'])
        assert len(sent) == 1 and result['model_calls'] == 9
        assert result['input_tokens'] == 1020 and result['output_tokens'] == 510
        assert result['history'][:len(original)] == original
        recorded = next(e['detail'] for e in store.events(project['id']) if e['kind'] == 'controllo_budget_token')
        assert recorded['used_tokens'] == 1500 and recorded['limit_tokens'] == 30000
        assert recorded['basis'] == 'provider_request_bytes_plus_4096_margin'
        assert 'existing code' not in json.dumps(recorded)
        assert history == original
    finally:
        await agent.shutdown()
        store.close()


@pytest.mark.parametrize('provider,succeeded', [('groq', False), ('openai', True)])
def test_reserve_retains_unsaved_code_and_uses_each_providers_actual_payload(tmp_path, provider, succeeded):
    settings = Settings(data_dir=tmp_path, provider=provider, max_total_tokens=30000)
    history = large_history(succeeded)
    project = {'input_tokens': 1000, 'output_tokens': 500, 'model_calls': 1, 'estimated_cost': None}
    budget = token_budget(settings, project, history)
    assert budget['required_tokens'] > settings.max_total_tokens
    with pytest.raises(NeedsIntervention, match='Budget token'):
        preflight(settings, project, history)


async def test_real_usage_exhaustion_still_stops_before_any_request(tmp_path):
    store = Store(tmp_path)
    project = store.create_project('Backend attività')
    store.update(project['id'], input_tokens=119000, output_tokens=1000, model_calls=8)
    settings = Settings(data_dir=tmp_path, max_total_tokens=120000)
    client = AsyncGroq(api_key='offline-test-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: pytest.fail('Exhausted token budget must prevent API calls'))))
    agent = Agent(settings, store, OfflineSandbox(), client=client)
    try:
        await agent.run(project['id'])
        result = store.project(project['id'])
        assert result['model_calls'] == 8 and result['input_tokens'] == 119000 and result['output_tokens'] == 1000
        assert result['state'] == 'Serve il tuo intervento' and 'Budget token' in result['summary']
        recorded = next(e['detail'] for e in store.events(project['id']) if e['kind'] == 'controllo_budget_token')
        assert recorded['used_tokens'] == recorded['limit_tokens'] == 120000
        assert recorded['required_tokens'] > 120000
    finally:
        await agent.shutdown()
        store.close()
