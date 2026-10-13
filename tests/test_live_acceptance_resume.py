"""Ripresa della prova: agenti simulati qui, nessuna generazione reale certificata."""
import json
from dataclasses import replace
import sys

from app.config import Settings
from app.storage import Store
from scripts import prova_agente as live


async def test_legacy_quota_result_resumes_same_files_history_and_counters(tmp_path, monkeypatch):
    config = Settings(data_dir=tmp_path, api_key='test-not-real-api-key')
    store = Store(tmp_path / 'live-acceptance')
    project = store.create_project(live.GOAL)
    store.write_file(project['id'], 'main.py', 'saved_before_quota = True\n')
    store.update(project['id'], state='Serve il tuo intervento', model_calls=3, input_tokens=1500,
                 history=[{'role': 'user', 'content': live.GOAL}])
    live.save_json(tmp_path / 'live-acceptance/RESULTS.json',
                   {'generation': {'id': project['id']}, 'repair': None, 'ai_used': True})
    store.close()
    monkeypatch.setattr(live, 'load_settings', lambda: config)
    monkeypatch.setattr(sys, 'argv', ['prova_agente.py'])
    called = []

    class StubAgent:
        def __init__(self, settings, store, sandbox):
            self.store = store

        async def run(self, pid):
            row = self.store.project(pid)
            assert row['model_calls'] == 3 and row['input_tokens'] == 1500 and row['history']
            assert self.store.files(pid)['main.py'] == 'saved_before_quota = True\n'
            called.append(pid)
            self.store.update(pid, state='Serve il tuo intervento', summary='Quota simulata', model_calls=4)

        async def shutdown(self):
            pass

    monkeypatch.setattr(live, 'Agent', StubAgent)
    assert await live.main() == 1
    assert called == [project['id']]
    store = Store(tmp_path / 'live-acceptance')
    try:
        assert len(store.rows('SELECT id FROM projects')) == 1
        assert store.project(project['id'])['model_calls'] == 4
        assert store.search('SQLite')  # Official dated sources are seeded for this store too.
    finally:
        store.close()
    assert list((tmp_path / 'live-acceptance/runs').glob('*.json'))
    assert live.read_json(tmp_path / 'live-acceptance/RUN.json')['generation_id'] == project['id']


async def test_resume_does_not_inject_fault_again_and_rechecks_ready_projects(tmp_path, monkeypatch):
    config = Settings(data_dir=tmp_path, api_key='test-not-real-api-key')
    store = Store(tmp_path / 'live-acceptance')
    original = store.create_project(live.GOAL)
    repair = store.create_project(live.REPAIR_GOAL)
    store.write_file(original['id'], 'main.py', 'original_must_stay = True\n')
    store.update(original['id'], state='Pronto', verified_hash=store.digest(original['id']),
                 last_check={'passed': True}, model_calls=8)
    fixed = 'def normalize_title(value):\n    return value.strip()\n'
    store.write_file(repair['id'], 'regression_target.py', fixed)
    store.update(repair['id'], state='Serve il tuo intervento', model_calls=5)
    store.event(repair['id'], 'verifica', {'passed': False})
    previous = {'generation': {'id': original['id']}, 'repair': {'project': {'id': repair['id']}}}
    live.save_json(tmp_path / 'live-acceptance/RESULTS.json', previous)
    store.close()
    monkeypatch.setattr(live, 'load_settings', lambda: config)
    monkeypatch.setattr(sys, 'argv', ['prova_agente.py'])
    called, checked = [], []

    class StubSandbox:
        def __init__(self, settings):
            pass

        async def verify(self, files, pid):
            checked.append(pid)
            return {'passed': True, 'check': {'unit_tests': 8}}

    class StubAgent:
        def __init__(self, settings, store, sandbox):
            self.store = store

        async def run(self, pid):
            assert pid == repair['id']
            assert self.store.files(pid)['regression_target.py'] == fixed
            assert self.store.project(pid)['model_calls'] == 5
            called.append(pid)
            self.store.event(pid, 'verifica', {'passed': True})
            self.store.update(pid, state='Pronto', verified_hash=self.store.digest(pid),
                              last_check={'passed': True}, model_calls=6)

        async def shutdown(self):
            pass

    monkeypatch.setattr(live, 'Sandbox', StubSandbox)
    monkeypatch.setattr(live, 'Agent', StubAgent)
    assert await live.main() == 0
    assert called == [repair['id']] and checked == [original['id']]
    result = live.read_json(tmp_path / 'live-acceptance/RESULTS.json')
    assert result['repair']['detected_initial_fault'] and result['repair']['original_unchanged']
    assert result['repair']['corrected_and_retested']
    # A second launch uses Docker checks for both; no new model calls.
    assert await live.main() == 0
    assert called == [repair['id']] and checked[-2:] == [original['id'], repair['id']]
