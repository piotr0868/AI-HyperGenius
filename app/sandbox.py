import asyncio
import base64
import json
from pathlib import Path
import re
import shutil
import uuid


BOOTSTRAP = r'''
import base64, json, os, pathlib, subprocess, sys, tempfile
payload = json.load(sys.stdin)
root = pathlib.Path('/work')
for name, data in payload['files'].items():
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(data))
with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
    try:
        child = subprocess.run(payload['argv'], cwd=root, stdin=subprocess.DEVNULL,
            stdout=out, stderr=err, timeout=payload['timeout'], env={
              'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':'/tmp',
              'PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1'})
        code, timeout = child.returncode, False
    except subprocess.TimeoutExpired:
        code, timeout = 124, True
    out.seek(0); err.seek(0)
    print(json.dumps({'exit_code':code,'timeout':timeout,
        'stdout':out.read(48000).decode(errors='replace'),
        'stderr':err.read(12000).decode(errors='replace')}, ensure_ascii=False))
'''


class SandboxUnavailable(RuntimeError):
    pass


class Sandbox:
    def __init__(self, settings):
        self.settings = settings
        self.active = {}

    async def _cli(self, *args, timeout=12):
        proc = await asyncio.create_subprocess_exec('docker', *args, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout)
        except (TimeoutError, asyncio.CancelledError):
            if proc.returncode is None:
                proc.kill()
            await proc.wait()
            raise
        return proc.returncode, out.decode(errors='replace'), err.decode(errors='replace')

    async def status(self):
        if not shutil.which('docker'):
            return {'available': False, 'reason': 'Installa Docker Desktop e attiva i container Linux.'}
        if not re.fullmatch(r'(?:[a-z0-9./_-]+)@sha256:[a-f0-9]{64}', self.settings.sandbox_image):
            return {'available': False, 'reason': 'Esegui prepara_isolamento.py per verificare e fissare l’immagine Docker.'}
        try:
            code, out, _ = await self._cli('info', '--format', '{{.OSType}}')
            if code or out.strip() != 'linux':
                return {'available': False, 'reason': 'Avvia Docker Desktop in modalità container Linux.'}
            code, out, _ = await self._cli('image', 'inspect', self.settings.sandbox_image, '--format', '{{.Id}}')
            if code:
                return {'available': False, 'reason': 'Immagine Docker mancante: esegui prepara_isolamento.py.'}
            return {'available': True, 'image': self.settings.sandbox_image}
        except (OSError, TimeoutError):
            return {'available': False, 'reason': 'Docker non risponde. L’esecuzione autonoma è disabilitata.'}

    async def stop(self, owner):
        for name in tuple(self.active.get(owner, set())):
            try:
                await self._cli('rm', '-f', name, timeout=6)
            except (OSError, TimeoutError):
                pass

    async def execute(self, files, argv, owner='probe', timeout=None):
        state = await self.status()
        if not state['available']:
            raise SandboxUnavailable(state['reason'])
        if not argv or argv[0] != 'python' or len(argv) > 20 or any(not isinstance(s, str) for s in argv):
            raise ValueError('Sono supportati soltanto comandi Python nel container.')
        if len(files) > 100 or sum(len(v.encode()) for v in files.values()) > 2000000:
            raise ValueError('Progetto troppo grande')
        for name in files:
            path = Path(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
                raise ValueError('Percorso non valido')
        limit = timeout or self.settings.command_timeout
        name = 'officina-' + uuid.uuid4().hex
        args = ['docker', 'run', '--rm', '--pull=never', '--name', name, '-i',
                '--network=none', '--read-only', '--cap-drop=ALL',
                '--security-opt=no-new-privileges', '--user=65534:65534',
                '--memory=256m', '--memory-swap=256m', '--cpus=0.5', '--pids-limit=64',
                '--ulimit', 'fsize=65536:65536', '--ulimit', 'nofile=128:128',
                '--tmpfs', '/work:rw,noexec,nosuid,size=32m,mode=1777',
                '--tmpfs', '/tmp:rw,noexec,nosuid,size=32m,mode=1777', '--workdir=/work',
                self.settings.sandbox_image, 'python', '-c', BOOTSTRAP]
        payload = json.dumps({'files': {k: base64.b64encode(v.encode()).decode() for k, v in files.items()},
                              'argv': argv, 'timeout': limit}).encode()
        self.active.setdefault(owner, set()).add(name)
        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(*args, stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await asyncio.wait_for(proc.communicate(payload), limit + 12)
            if proc.returncode:
                return {'exit_code': proc.returncode, 'timeout': False,
                        'stdout': stdout.decode(errors='replace')[:48000],
                        'stderr': stderr.decode(errors='replace')[:12000]}
            try:
                return json.loads(stdout)
            except ValueError:
                return {'exit_code': 125, 'timeout': False, 'stdout': '', 'stderr': 'Risposta del container non valida.'}
        except TimeoutError:
            return {'exit_code': 124, 'timeout': True, 'stdout': '', 'stderr': 'Timeout del container.'}
        finally:
            try:
                await asyncio.shield(self._cli('rm', '-f', name, timeout=6))
            except (OSError, TimeoutError, asyncio.CancelledError):
                pass
            if proc and proc.returncode is None:
                proc.kill()
                await proc.wait()
            self.active.get(owner, set()).discard(name)

    async def verify(self, files, owner):
        contract = Path(__file__).with_name('acceptance_contract.py').read_text(encoding='utf-8')
        result = await self.execute(files, ['python', '-c', contract], owner)
        result['passed'] = False
        for line in result.get('stdout', '').splitlines():
            if line.startswith('OFFICINA_CHECK='):
                try:
                    check = json.loads(line.removeprefix('OFFICINA_CHECK='))
                    result['check'] = check
                    result['passed'] = result['exit_code'] == 0 and check.get('passed') is True
                except ValueError:
                    pass
        return result
