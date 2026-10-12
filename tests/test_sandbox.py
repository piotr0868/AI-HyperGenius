"""Esecuzioni Docker reali. Se Docker manca, l'esito è skipped e non convalida l'isolamento."""
import json
from pathlib import Path
import pytest

from app.config import load_settings
from app.sandbox import Sandbox


@pytest.fixture
async def sandbox():
    sandbox = Sandbox(load_settings())
    status = await sandbox.status()
    if not status['available']:
        pytest.skip(status['reason'])
    return sandbox


async def test_isolation_has_no_secrets_mounts_or_external_network(sandbox):
    probe = '''
import json,os,socket,pathlib
assert os.getuid() == 65534
assert not any(name in os.environ for name in ('GROQ_API_KEY','AI_PROVIDER_KEY','OPENAI_API_KEY','GH_TOKEN','GITHUB_TOKEN'))
assert not pathlib.Path('/var/run/docker.sock').exists()
assert not pathlib.Path('/workspace').exists()
try:
    pathlib.Path('/root-owned-file').write_text('blocked')
except OSError: pass
else: raise AssertionError('root filesystem writable')
sock=socket.socket(); sock.settimeout(.5)
try: sock.connect(('1.1.1.1',80))
except OSError: pass
else: raise AssertionError('external network available')
finally: sock.close()
pathlib.Path('/work/writable.txt').write_text('local only')
print('ISOLATION_PASS')
'''
    result = await sandbox.execute({}, ['python', '-c', probe], 'isolation-test')
    assert result['exit_code'] == 0 and 'ISOLATION_PASS' in result['stdout']


async def test_timeout_kills_generated_process(sandbox):
    result = await sandbox.execute({}, ['python', '-c', 'import time; time.sleep(20)'], 'timeout-test', timeout=1)
    assert result['exit_code'] == 124 and result['timeout'] is True
    assert sandbox.active['timeout-test'] == set()


async def test_zero_test_run_never_certifies_ready(sandbox):
    result = await sandbox.verify({'main.py': 'pass\n', 'tests/test_empty.py': 'import unittest\n'}, 'zero-tests')
    assert result['passed'] is False
    assert result['check']['unit_tests'] == 0


async def test_reference_and_external_contract(sandbox):
    root = Path(__file__).resolve().parent.parent / 'examples' / 'activity_backend'
    files = {p.relative_to(root).as_posix(): p.read_text(encoding='utf-8') for p in root.rglob('*.py')
             if '__pycache__' not in p.parts}
    result = await sandbox.verify(files, 'reference-tests')
    assert result['passed'] is True
    assert result['check']['unit_tests'] == 8
    assert len(result['check']['contract']) == 5
