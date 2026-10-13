import pytest
from app.providers import chat_messages
from app.providers import groq_messages
from app.config import load_settings, Settings


def test_old_responses_history_converts_to_groq_chat_without_losing_results():
    history = [{'role': 'user', 'content': 'Crea un backend'},
               {'type': 'reasoning', 'id': 'rs_old', 'summary': []},
               {'type': 'function_call', 'call_id': 'one', 'name': 'read_file', 'arguments': '{"path":"main.py"}'},
               {'type': 'function_call', 'call_id': 'two', 'name': 'list_files', 'arguments': '{}'},
               {'type': 'function_call_output', 'call_id': 'one', 'output': '{"content":"saved"}'},
               {'type': 'function_call_output', 'call_id': 'two', 'output': '{"files":["main.py"]}'},
               {'type': 'message', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': 'Controllo i file'}]}]
    messages = chat_messages(history, 'Regole del sistema')
    assert messages[0] == {'role': 'system', 'content': 'Regole del sistema'}
    assert [c['id'] for c in messages[2]['tool_calls']] == ['one', 'two']
    assert messages[3]['tool_call_id'] == 'one' and messages[4]['tool_call_id'] == 'two'
    assert messages[-1]['content'] == 'Controllo i file'
    assert not any('reasoning' in m for m in messages)


@pytest.fixture
def isolated_config(monkeypatch, tmp_path):
    import app.config
    monkeypatch.setattr(app.config, 'ROOT', tmp_path)
    for name in ('AI_PROVIDER', 'AI_MODEL', 'AI_PROVIDER_KEY', 'GROQ_API_KEY', 'GROQ_MODEL', 'AI_MIN_INTERVAL_SECONDS'):
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_default_groq_does_not_reuse_openai_credentials(isolated_config):
    isolated_config.setenv('AI_PROVIDER_KEY', 'offline-openai-key')
    isolated_config.setenv('AI_MODEL', 'gpt-5-mini')
    settings = load_settings()
    assert settings.provider == 'groq' and settings.api_key == ''
    assert settings.model == 'openai/gpt-oss-20b' and settings.min_interval == 60
    assert settings.credential_var == 'GROQ_API_KEY'


def test_provider_credentials_are_selected_separately(isolated_config):
    isolated_config.setenv('GROQ_API_KEY', 'offline-groq-key')
    isolated_config.setenv('AI_PROVIDER_KEY', 'offline-openai-key')
    assert load_settings().api_key == 'offline-groq-key'
    isolated_config.setenv('AI_PROVIDER', 'openai')
    selected = load_settings()
    assert selected.api_key == 'offline-openai-key' and selected.model == 'gpt-5-mini'
    assert 'offline-openai-key' not in repr(selected)


def test_unknown_provider_rejected(isolated_config):
    isolated_config.setenv('AI_PROVIDER', 'unknown')
    with pytest.raises(ValueError, match='AI_PROVIDER'):
        load_settings()


def test_groq_context_slimming_preserves_history_failures_and_document_sources():
    import copy
    import json
    source = 'print("actual_saved_code")\n' * 400
    history = [
        {'role': 'user', 'content': 'Backend attività'},
        {'type': 'function_call', 'call_id': 'saved', 'name': 'write_file',
         'arguments': json.dumps({'path': 'main.py', 'content': source})},
        {'type': 'function_call_output', 'call_id': 'saved', 'output': '{"path":"main.py","previous_version":1}'},
        {'type': 'function_call', 'call_id': 'failed', 'name': 'write_file',
         'arguments': json.dumps({'path': 'bad.py', 'content': 'must_remain_for_retry'})},
        {'type': 'function_call_output', 'call_id': 'failed', 'output': '{"error":"not saved"}'},
        {'type': 'function_call', 'call_id': 'docs', 'name': 'fetch_documentation', 'arguments': '{}'},
        {'type': 'function_call_output', 'call_id': 'docs', 'output': json.dumps({
            'source': 'https://docs.python.org/3.12/library/sqlite3.html', 'source_date': '2026-10-13',
            'content': 'documentation' * 1000, 'trust': 'untrusted data'})},
        {'type': 'function_call', 'call_id': 'checks', 'name': 'run_checks', 'arguments': '{}'},
        {'type': 'function_call_output', 'call_id': 'checks', 'output': json.dumps({
            'passed': False, 'check': {'unit_failures': 2}, 'stderr': 'trace' * 1000 + ' ROOT_CAUSE'})}]
    original = copy.deepcopy(history)
    messages = groq_messages(history, 'Rules remain mandatory')
    assert history == original
    assert messages[0]['content'] == 'Rules remain mandatory'
    calls = {c['id']: c['function'] for m in messages for c in m.get('tool_calls', [])}
    assert source not in calls['saved']['arguments']
    assert 'must_remain_for_retry' in calls['failed']['arguments']
    outputs = {m['tool_call_id']: json.loads(m['content']) for m in messages if m['role'] == 'tool'}
    assert outputs['docs']['source'] == 'https://docs.python.org/3.12/library/sqlite3.html'
    assert outputs['docs']['source_date'] == '2026-10-13' and outputs['docs']['trust'] == 'untrusted data'
    assert len(outputs['docs']['content']) == 2000 and outputs['docs']['request_excerpt_limited']
    assert outputs['checks']['passed'] is False and outputs['checks']['check']['unit_failures'] == 2
    assert outputs['checks']['stderr'].endswith('ROOT_CAUSE')
    assert len(json.dumps(messages)) < len(json.dumps(chat_messages(history, 'Rules remain mandatory'))) / 2
