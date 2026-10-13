"""Controlli dei fallimenti dell'avvio. API simulate qui, non accettazione IA."""
from dataclasses import replace
import json
from pathlib import Path
import stat
import sys

from dotenv import dotenv_values
import pytest

from app.config import Settings
from app.storage import Store
from scripts import avvio_automatico as setup


@pytest.fixture
def workflow(monkeypatch, tmp_path):
    config = Settings(data_dir=tmp_path / '.data', api_key='test-placeholder-not-real-000',
                      sandbox_image='python@sha256:' + 'a' * 64)
    monkeypatch.setattr(setup, 'ROOT', tmp_path)
    monkeypatch.setattr(setup, 'load_settings', lambda: config)
    monkeypatch.setattr(setup, 'ensure_docker', lambda: True)
    monkeypatch.setattr(setup, 'fingerprint', lambda settings: 'same-source-fingerprint')
    calls = {'api': 0, 'reference': 0, 'live': 0}

    async def api():
        calls['api'] += 1
        return 0

    async def reference():
        calls['reference'] += 1
        path = tmp_path / '.data/verification/local_acceptance.json'
        setup.write_report(path, {'fault_detection_passed': True, 'reference_backend': {'passed': True},
                                  'restored_reference': {'passed': True}})
        return 0

    async def live():
        calls['live'] += 1
        return 1

    class AvailableSandbox:
        def __init__(self, settings):
            pass

        async def status(self):
            return {'available': True}

    monkeypatch.setattr(setup.controlla_ia, 'main', api)
    monkeypatch.setattr(setup.verifica_locale, 'main', reference)
    monkeypatch.setattr(setup.prova_agente, 'main', live)
    monkeypatch.setattr(setup, 'Sandbox', AvailableSandbox)
    return config, calls


def test_local_key_does_not_replace_other_settings_or_appear_in_output(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(setup, 'ROOT', tmp_path)
    path = tmp_path / '.env'
    path.write_text('APP_PORT=9999\nAI_PROVIDER_KEY=old-placeholder\n')
    key = 'test-placeholder-secret-not-real-000'
    monkeypatch.setenv('GROQ_API_KEY', '')
    monkeypatch.setenv('AI_PROVIDER', 'groq')
    setup.save_key('groq', key)
    values = dotenv_values(path)
    assert values['GROQ_API_KEY'] == key
    assert values['AI_PROVIDER_KEY'] == 'old-placeholder' and values['APP_PORT'] == '9999'
    assert key not in capsys.readouterr().out
    if sys.platform != 'win32':
        assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_abbreviated_key_is_rejected_before_writing(monkeypatch, tmp_path):
    monkeypatch.setattr(setup, 'ROOT', tmp_path)
    with pytest.raises(ValueError):
        setup.save_key('groq', 'gsk_...XPpP')
    assert not (tmp_path / '.env').exists()


def test_windows_key_path_is_outside_project_and_is_loaded_without_logging(monkeypatch, tmp_path, capsys):
    project = tmp_path / 'OneDrive/Desktop/Officina'
    project.mkdir(parents=True)
    (project / '.env.example').write_text('AI_PROVIDER=groq\nGROQ_API_KEY=\n')
    monkeypatch.setattr(setup, 'ROOT', project)
    monkeypatch.setattr(setup.sys, 'platform', 'win32')
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path / 'Local'))
    monkeypatch.setenv('USERNAME', 'test-user')
    monkeypatch.setenv('USERDOMAIN', '')
    monkeypatch.setenv('GROQ_API_KEY', '')
    monkeypatch.setenv('AI_PROVIDER', 'groq')
    commands = []

    def icacls(args, **kwargs):
        commands.append(args)
        return type('Result', (), {'returncode': 0})()

    monkeypatch.setattr(setup.subprocess, 'run', icacls)
    dummy = 'test-windows-local-secret-not-real-000'
    setup.save_key('groq', dummy)
    assert dummy not in (project / '.env').read_text()
    assert dotenv_values(tmp_path / 'Local/Officina/credentials.env')['GROQ_API_KEY'] == dummy
    assert commands[0][0] == 'icacls' and dummy not in str(commands)
    monkeypatch.setenv('GROQ_API_KEY', '')
    setup.load_local_credentials()
    assert setup.os.environ['GROQ_API_KEY'] == dummy
    assert dummy not in capsys.readouterr().out


def test_cancelled_key_never_calls_api_or_runs_verifications(workflow, monkeypatch):
    config, calls = workflow
    monkeypatch.setattr(setup, 'load_settings', lambda: replace(config, api_key=''))
    monkeypatch.setattr(setup, 'request_key', lambda provider: '')
    report = setup.run_setup()
    assert report['api'] == report['reference'] == report['live_ai'] == 'not_run'
    assert calls == {'api': 0, 'reference': 0, 'live': 0}


def test_api_failure_never_launches_live_generation(workflow, monkeypatch):
    _, calls = workflow

    async def rejected():
        return 1

    monkeypatch.setattr(setup.controlla_ia, 'main', rejected)
    report = setup.run_setup()
    assert report['api'] == 'failed' and report['live_ai'] == 'not_run'
    assert calls['live'] == calls['reference'] == 0


def test_missing_docker_does_not_execute_generated_code(workflow, monkeypatch):
    _, calls = workflow
    monkeypatch.setattr(setup, 'ensure_docker', lambda: False)
    report = setup.run_setup()
    assert report['sandbox'] == 'unavailable' and report['live_ai'] == 'not_run'
    assert calls['live'] == calls['reference'] == 0


def test_failed_reference_blocks_model_acceptance(workflow, monkeypatch):
    _, calls = workflow

    async def failed():
        return 1

    monkeypatch.setattr(setup.verifica_locale, 'main', failed)
    report = setup.run_setup()
    assert report['reference'] == 'failed' and report['live_ai'] == 'not_run'
    assert calls['live'] == 0


def test_failed_live_proof_is_not_retried_on_every_launch(workflow):
    _, calls = workflow
    first = setup.run_setup()
    second = setup.run_setup()
    third = setup.run_setup(retry=True)
    assert first['live_ai'] == second['live_ai'] == third['live_ai'] == 'failed'
    assert calls['live'] == 2  # One initial attempt and one explicit retry.
    assert calls['reference'] == 1
    assert second['live_ai_reused'] is True


def test_interrupted_proof_stays_unverified_without_extra_calls(workflow):
    config, calls = workflow
    path = config.data_dir / 'setup/RESULTS.json'
    setup.write_report(path, {'fingerprint': 'same-source-fingerprint', 'live_ai': 'running'})
    assert setup.run_setup()['live_ai'] == 'interrupted'
    assert setup.run_setup()['live_ai'] == 'interrupted'
    assert calls['live'] == 0


def test_lost_live_evidence_cannot_be_reused_as_passed(workflow):
    config, calls = workflow
    setup.write_report(config.data_dir / 'setup/RESULTS.json',
                       {'fingerprint': 'same-source-fingerprint', 'live_ai': 'passed'})
    report = setup.run_setup()
    assert report['live_ai'] == 'not_verified' and calls['live'] == 0
    assert setup.run_setup()['live_ai'] == 'not_verified'
    assert calls['live'] == 0


def test_live_evidence_is_invalidated_when_verified_files_change(tmp_path):
    config = Settings(data_dir=tmp_path)
    store = Store(tmp_path / 'live-acceptance')
    projects = []
    try:
        for description in ('Originale', 'Riparazione separata'):
            project = store.create_project(description)
            store.write_file(project['id'], 'main.py', 'print("verified")\n')
            projects.append({'id': project['id'], 'state': 'Pronto', 'verified_hash': store.digest(project['id'])})
        evidence = {'generation': projects[0], 'repair': {'project': projects[1], 'detected_initial_fault': True,
                    'corrected_and_retested': True, 'original_unchanged': True}}
        setup.write_report(tmp_path / 'live-acceptance/RESULTS.json', evidence)
        assert setup.verified_live_evidence(config) is True
        store.write_file(projects[0]['id'], 'main.py', 'print("edited")\n')
        assert setup.verified_live_evidence(config) is False
    finally:
        store.close()


def test_invalid_docker_digest_never_updates_configuration(monkeypatch, tmp_path):
    monkeypatch.setattr(setup, 'ROOT', tmp_path)
    path = tmp_path / '.env'
    path.write_text('SANDBOX_IMAGE=original\n')
    monkeypatch.setattr(setup.subprocess, 'run', lambda *args, **kwargs: None)
    monkeypatch.setattr(setup.subprocess, 'check_output', lambda *args, **kwargs: 'python:latest')
    assert setup.prepare_image() is False
    assert path.read_text() == 'SANDBOX_IMAGE=original\n'
