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
