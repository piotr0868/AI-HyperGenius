import importlib.util
from pathlib import Path
import stat
import sys

from dotenv import dotenv_values


def test_groq_key_is_saved_locally_without_printing_or_overwriting_legacy_key(monkeypatch, tmp_path, capsys):
    path = Path(__file__).resolve().parent.parent / 'scripts' / 'configura_ia.py'
    spec = importlib.util.spec_from_file_location('local_key_setup', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    dummy = 'test-local-provider-key-not-real-000'
    old = 'legacy-placeholder-not-real'
    (tmp_path / '.env').write_text('AI_PROVIDER_KEY=' + old + '\nAPP_PORT=9999\n')
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    monkeypatch.setattr(module, 'getpass', lambda prompt: dummy)
    monkeypatch.setattr(sys, 'argv', ['configura_ia.py', '--no-browser'])
    assert module.main() == 0
    values = dotenv_values(tmp_path / '.env')
    assert values['AI_PROVIDER'] == 'groq' and values['GROQ_API_KEY'] == dummy
    assert values['AI_PROVIDER_KEY'] == old and values['APP_PORT'] == '9999'
    output = capsys.readouterr().out
    assert dummy not in output and old not in output
    if sys.platform != 'win32':
        assert stat.S_IMODE((tmp_path / '.env').stat().st_mode) == 0o600
