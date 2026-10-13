"""Diagnosi in sola lettura; il codice generato non viene importato o eseguito."""
import hashlib
import json
from pathlib import Path

import pytest

from app.config import Settings
from app.storage import Store
from scripts import leggi_diagnosi as diagnostic


def prepare(tmp_path):
    store = Store(tmp_path / 'live-acceptance')
    project = store.create_project('Backend attività')
    (tmp_path / 'live-acceptance/RUN.json').write_text(json.dumps({'generation_id': project['id']}))
    return store, project


def test_current_files_and_agent_reply_are_read_without_execution_or_database_changes(tmp_path):
    store, project = prepare(tmp_path)
    pid = project['id']
    source = "import sqlite3\nraise RuntimeError('generated code must never execute')\ndef run_server(port, db):\n    pass\n"
    store.write_file(pid, 'main.py', source)
    fake_secret = 'gsk_test-placeholder-never-display'
    store.event(pid, 'messaggio_ia', {'text': f'Ho scritto il codice. {fake_secret}'})
    store.event(pid, 'errore_strumento', {'tool': 'write_file', 'message': f'Errore: {fake_secret}'})
    store.update(pid, model_calls=16, input_tokens=70000, output_tokens=10000,
        last_check={'passed': False, 'stderr': 'previous failure', 'check': {'server_log': fake_secret}},
        history=[{'type': 'function_call', 'call_id': 'main', 'name': 'write_file',
            'arguments': json.dumps({'path': 'main.py', 'content': source})},
            {'type': 'function_call_output', 'call_id': 'main', 'output': '{"path":"main.py","previous_version":1}'}])
    store.close()
    database = tmp_path / 'live-acceptance/memory.sqlite3'
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    report = diagnostic.collect(Settings(data_dir=tmp_path))
    assert report['project']['model_calls'] == 16
    assert report['python_outline_now']['main.py']['functions'] == [{'name': 'run_server', 'parameters': ['port', 'db']}]
    assert report['python_outline_now']['main.py']['imports'] == ['sqlite3']
    assert report['last_check']['passed'] is False and report['files_now'][0]['path'] == 'main.py'
    serialized = json.dumps(report)
    assert fake_secret not in serialized and 'CHIAVE OSCURATA' in serialized
    assert 'generated code must never execute' not in serialized
    assert hashlib.sha256(database.read_bytes()).hexdigest() == before
    assert (tmp_path / f'live-acceptance/projects/{pid}/workspace/main.py').read_text() == source


def test_diagnostic_does_not_follow_links_outside_project(tmp_path):
    store, project = prepare(tmp_path)
    secret = tmp_path / 'personal.py'
    secret.write_text('private_personal_content = True')
    (store.workspace(project['id']) / 'trap.py').symlink_to(secret)
    store.close()
    report = diagnostic.collect(Settings(data_dir=tmp_path))
    assert report['files_now'] == [] and report['python_outline_now'] == {}
    assert 'private_personal_content' not in json.dumps(report)


def test_invalid_project_reference_is_refused_before_database_access(tmp_path, monkeypatch):
    data = tmp_path / 'live-acceptance'
    data.mkdir()
    (data / 'RUN.json').write_text('{"generation_id":"../../personal"}')
    monkeypatch.setattr(diagnostic.sqlite3, 'connect', lambda *args, **kwargs: pytest.fail('Invalid project must not query any database'))
    with pytest.raises(ValueError, match='valid generation'):
        diagnostic.collect(Settings(data_dir=tmp_path))


def test_windows_reports_use_new_files_and_open_only_notepad(tmp_path, monkeypatch, capsys):
    store, project = prepare(tmp_path)
    store.close()
    monkeypatch.setattr(diagnostic, 'load_settings', lambda: Settings(data_dir=tmp_path))
    monkeypatch.setattr(diagnostic.sys, 'platform', 'win32')
    launched = []
    monkeypatch.setattr(diagnostic.subprocess, 'Popen', lambda args: launched.append(args))
    assert diagnostic.main() == 0 and diagnostic.main() == 0
    assert len(launched) == 2 and launched[0][1] != launched[1][1]
    for args in launched:
        assert args[0] == 'notepad.exe'
        assert json.loads(Path(args[1]).read_text())['project']['id'] == project['id']
    assert 'Nessuna chiamata IA' in capsys.readouterr().out
