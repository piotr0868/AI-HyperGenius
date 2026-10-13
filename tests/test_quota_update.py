"""Verifica download incompleti, checksum e conservazione dei dati nell'aggiornamento."""
import hashlib
import json

from dotenv import dotenv_values
import pytest

from scripts import aggiorna_quota as update


def test_running_app_blocks_updates_before_any_mutation(monkeypatch):
    monkeypatch.setattr(update.sys, 'argv', ['aggiorna_quota.py', 'a' * 40])
    monkeypatch.setattr(update, 'app_running', lambda: True)
    monkeypatch.setattr(update, 'update_code', lambda ref: pytest.fail('Must not change running app'))
    assert update.main() == 1


def test_update_verifies_all_files_before_mutation_and_keeps_backups(tmp_path, monkeypatch):
    monkeypatch.setattr(update, 'ROOT', tmp_path)
    originals, incoming = {}, {}
    for name in update.FILES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        originals[name] = b'old_source = True\n'
        incoming[name] = b'updated_source = True\n'
        path.write_bytes(originals[name])
    (tmp_path / '.env').write_text('GROQ_API_KEY=not-real-test-key\n')
    manifest = {'source_sha256': {k: hashlib.sha256(v).hexdigest() for k, v in incoming.items()}}

    def fetch(ref, name):
        return json.dumps(manifest).encode() if name == 'VERIFICHE.json' else incoming[name]

    monkeypatch.setattr(update, 'fetch', fetch)
    archive = update.update_code('a' * 40)
    assert (tmp_path / '.env').read_text() == 'GROQ_API_KEY=not-real-test-key\n'
    for name in update.FILES:
        assert (tmp_path / name).read_bytes() == incoming[name]
        assert (archive / name).read_bytes() == originals[name]


def test_bad_checksum_never_overwrites_existing_files(tmp_path, monkeypatch):
    monkeypatch.setattr(update, 'ROOT', tmp_path)
    for name in update.FILES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'original = True\n')
    monkeypatch.setattr(update, 'fetch', lambda ref, name:
        json.dumps({'source_sha256': {k: '0' * 64 for k in update.FILES}}).encode()
        if name == 'VERIFICHE.json' else b'changed = True\n')
    with pytest.raises(ValueError, match='Checksum'):
        update.update_code('a' * 40)
    assert all((tmp_path / name).read_bytes() == b'original = True\n' for name in update.FILES)


def test_free_profile_keeps_credentials_and_explicit_lower_limits(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(update, 'ROOT', tmp_path)
    for name in ('AI_PROVIDER', 'AI_MIN_INTERVAL_SECONDS', 'MAX_OUTPUT_TOKENS', 'MAX_RATE_LIMIT_RETRIES'):
        monkeypatch.setenv(name, 'groq' if name == 'AI_PROVIDER' else '')
    path = tmp_path / '.env'
    dummy = 'test-placeholder-not-real-secret'
    path.write_text(f'AI_PROVIDER=groq\nGROQ_API_KEY={dummy}\nMAX_OUTPUT_TOKENS=1000\nMAX_RATE_LIMIT_RETRIES=0\nAPP_PORT=9999\n')
    update.configure_free_profile()
    values = dotenv_values(path)
    assert values['GROQ_API_KEY'] == dummy and values['APP_PORT'] == '9999'
    assert values['AI_MIN_INTERVAL_SECONDS'] == '60'
    assert values['MAX_OUTPUT_TOKENS'] == '1000' and values['MAX_RATE_LIMIT_RETRIES'] == '0'
    assert dummy not in capsys.readouterr().out


@pytest.mark.parametrize('pid,port', [(-1, 8765), (2 ** 31, 8765), (18348, 80)])
def test_invalid_process_target_never_invokes_windows_commands(monkeypatch, pid, port):
    monkeypatch.setattr(update.sys, 'platform', 'win32')
    monkeypatch.setattr(update.subprocess, 'run', lambda *args, **kwargs: pytest.fail('Invalid target must be refused'))
    assert update.checked_windows_process(pid, port, stop=True) is False


def test_unmatched_process_never_queries_session_or_terminates(monkeypatch, tmp_path):
    monkeypatch.setattr(update, 'ROOT', tmp_path)
    monkeypatch.setattr(update, 'local_port', lambda: 8765)
    actions = []

    def check(pid, port, stop=False):
        actions.append(stop)
        return False

    monkeypatch.setattr(update, 'checked_windows_process', check)
    monkeypatch.setattr(update.urllib.request, 'build_opener', lambda *args: pytest.fail('Identity check must precede HTTP controls'))
    assert update.stop_reported_instance(18348) is False
    assert actions == [False]


def test_matching_process_stops_active_work_before_process_and_keeps_token_private(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(update, 'ROOT', tmp_path)
    monkeypatch.setattr(update, 'local_port', lambda: 8765)
    calls = []
    project_id = 'a' * 32
    token = 'test-session-token-not-real'

    class Response:
        def __init__(self, data):
            self.data = data

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, limit):
            return json.dumps(self.data).encode()

    class Opener:
        def open(self, request, **kwargs):
            url = request if isinstance(request, str) else request.full_url
            if url.endswith('/api/session'):
                return Response({'token': token})
            if url.endswith('/api/projects'):
                return Response([{'id': project_id, 'state': 'Lavoro'}])
            if url.endswith('/control'):
                assert request.get_header('X-app-token') == token
                assert request.data == b'{"action":"stop"}'
                calls.append('stop_work')
                return Response({'ok': True})
            return Response({'worker_active': True})

    def check(pid, port, stop=False):
        assert pid == 18348 and port == 8765
        calls.append('stop_process' if stop else 'check_process')
        return True

    monkeypatch.setattr(update, 'checked_windows_process', check)
    monkeypatch.setattr(update.urllib.request, 'build_opener', lambda *args: Opener())
    monkeypatch.setattr(update, 'app_running', lambda: False)
    assert update.stop_reported_instance(18348) is True
    assert calls == ['check_process', 'stop_work', 'stop_process']
    assert token not in capsys.readouterr().out


def test_failed_work_shutdown_prevents_process_stop_and_update(monkeypatch, tmp_path):
    monkeypatch.setattr(update, 'ROOT', tmp_path)
    monkeypatch.setattr(update, 'local_port', lambda: 8765)
    calls = []

    def check(pid, port, stop=False):
        calls.append(stop)
        return True

    class BrokenOpener:
        def open(self, *args, **kwargs):
            raise OSError('Unavailable local session')

    monkeypatch.setattr(update, 'checked_windows_process', check)
    monkeypatch.setattr(update.urllib.request, 'build_opener', lambda *args: BrokenOpener())
    assert update.stop_reported_instance(18348) is False
    assert calls == [False]
