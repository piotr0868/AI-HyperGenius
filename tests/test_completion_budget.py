"""Conclusione del progetto UI a budget esaurito: SDK simulato, Docker reale."""
from dataclasses import replace
from pathlib import Path

from groq import AsyncGroq
import httpx
import pytest

from app.agent import Agent
from app.config import load_settings
from app.sandbox import Sandbox
from app.storage import Store


@pytest.mark.parametrize('case', ['unchecked_valid', 'verified', 'changed_after_verification',
                                 'invalid_validation', 'zero_tests', 'unchanged_failure'])
async def test_ui_call_limit_checks_saved_files_without_new_model_calls(tmp_path, case):
    settings = replace(load_settings(), data_dir=tmp_path, max_model_calls=12, min_interval=0)
    sandbox = Sandbox(settings)
    status = await sandbox.status()
    if not status['available']:
        pytest.skip(status['reason'])
    root = Path(__file__).resolve().parent.parent / 'examples/activity_backend'
    files = {p.relative_to(root).as_posix(): p.read_text(encoding='utf-8')
             for p in root.rglob('*.py') if '__pycache__' not in p.parts}
    if case in ('invalid_validation', 'unchanged_failure'):
        files['main.py'] = files['main.py'].replace('or not title.strip() or', 'or')
    elif case == 'zero_tests':
        files = {'main.py': files['main.py'], 'tests/test_empty.py': 'import unittest\n'}

    def reject_request(request):
        pytest.fail('Il limite raggiunto deve impedire ogni richiesta al modello')

    client = AsyncGroq(api_key='offline-only', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(reject_request)))
    store = Store(tmp_path)
    agent = Agent(settings, store, sandbox, client=client)
    pid = store.create_project('Prova UI da file salvati, fixture non generata da IA')['id']
    for name, content in files.items():
        store.write_file(pid, name, content)
    store.update(pid, criteria=['Test, API e persistenza'], plan=['Implementa e verifica'], docs_consulted=1)
    if case in ('verified', 'changed_after_verification', 'unchanged_failure'):
        result = await agent.perform(pid, 'run_checks', {})
        assert result['passed'] == (case != 'unchanged_failure')
        assert result['files_sha256'] == store.digest(pid)
    if case == 'changed_after_verification':
        store.write_file(pid, 'README.md', 'Istruzioni aggiornate dopo il precedente controllo.\n')
    store.update(pid, state='Serve il tuo intervento', model_calls=12,
                 input_tokens=1250, output_tokens=125, elapsed=10)
    digest = store.digest(pid)
    before = store.project(pid)
    checks_before = sum(e['kind'] == 'verifica' for e in store.events(pid))
    try:
        await agent.run(pid)
        result = store.project(pid)
        assert result['model_calls'] == 12 and result['input_tokens'] == 1250 and result['output_tokens'] == 125
        assert result['elapsed'] >= 10 and store.digest(pid) == digest
        checks_after = sum(e['kind'] == 'verifica' for e in store.events(pid))
        assert checks_after - checks_before == (0 if case in ('verified', 'unchanged_failure') else 1)
        if case in ('unchecked_valid', 'verified', 'changed_after_verification'):
            assert result['state'] == 'Pronto' and result['verified_hash'] == digest
            assert result['last_check']['check']['unit_tests'] == 8
            assert len(result['last_check']['check']['contract']) == 5
            certificate = next(e for e in store.events(pid) if e['kind'] == 'certificazione_automatica')
            assert not certificate['detail']['model_called']
            assert result['failed_checks'] == before['failed_checks']
        else:
            assert result['state'] == 'Serve il tuo intervento' and result['verified_hash'] is None
            assert result['last_check']['passed'] is False
            assert result['failed_checks'] == before['failed_checks'] + (case != 'unchanged_failure')
            assert 'Limite di chiamate' in result['summary']
            assert not any(e['kind'] == 'certificazione_automatica' for e in store.events(pid))
    finally:
        await agent.shutdown()
        store.close()
