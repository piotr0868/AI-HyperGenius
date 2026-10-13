"""Aggiorna solo file elencati da una revisione GitHub verificata; conserva i dati."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request

from dotenv import dotenv_values, set_key

ROOT = Path(__file__).resolve().parent.parent
FILES = ('app/agent.py', 'app/providers.py', 'app/config.py', 'scripts/prova_agente.py')


def fetch(ref, name):
    if not re.fullmatch(r'[a-f0-9]{40}', ref):
        raise ValueError('Revisione non valida.')
    url = f'https://raw.githubusercontent.com/piotr0868/AI-HyperGenius/{ref}/{name}'
    with urllib.request.urlopen(url, timeout=30) as response:
        if response.geturl() != url:
            raise ValueError('Destinazione di download inattesa.')
        data = response.read(250001)
    if len(data) > 250000:
        raise ValueError('File oltre il limite di aggiornamento.')
    return data


def update_code(ref):
    manifest = json.loads(fetch(ref, 'VERIFICHE.json'))['source_sha256']
    bundle = {}
    # Prima convalida l'intero gruppo. Nessuna modifica su download incompleto.
    for name in FILES:
        data = fetch(ref, name)
        expected = manifest.get(name, '')
        if not re.fullmatch(r'[a-f0-9]{64}', expected) or hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('Checksum dei sorgenti non corrispondente.')
        compile(data, name, 'exec')
        bundle[name] = data
    archive = ROOT / '.data' / 'updates' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    originals = {}
    for name in FILES:
        path = ROOT / name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('File collegato: aggiornamento interrotto.')
        originals[name] = path.read_bytes()
        backup = archive / name
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(originals[name])
    applied = []
    try:
        for name, data in bundle.items():
            path = ROOT / name
            temporary = path.with_suffix('.update-tmp')
            temporary.write_bytes(data)
            temporary.replace(path)
            applied.append(name)
    except Exception:
        for name in applied:
            (ROOT / name).write_bytes(originals[name])
        raise
    (archive / 'UPDATE.json').write_text(json.dumps({'ref': ref, 'files': list(FILES),
        'data_preserved': True}, indent=2), encoding='utf-8')
    print('Sorgenti aggiornati con checksum verificati. Versione precedente conservata.', flush=True)
    return archive


def configure_free_profile():
    path = ROOT / '.env'
    values = dotenv_values(path)
    if os.environ.get('AI_PROVIDER', values.get('AI_PROVIDER', 'groq')) != 'groq':
        return
    try:
        output = int(values.get('MAX_OUTPUT_TOKENS') or '4000')
        retries = int(values.get('MAX_RATE_LIMIT_RETRIES') or '2')
    except ValueError:
        raise ValueError('Limiti locali non validi; nessuna modifica alla chiave.') from None
    if output < 500 or not 0 <= retries <= 2:
        raise ValueError('Limiti locali fuori intervallo.')
    for name, value in {'AI_MIN_INTERVAL_SECONDS': 60, 'MAX_OUTPUT_TOKENS': min(output, 3000),
                        'MAX_RATE_LIMIT_RETRIES': retries}.items():
        set_key(str(path), name, str(value), quote_mode='never')
        os.environ[name] = str(value)
    print('Profilo Groq: richieste distanziate, meno testo ripetuto, attese brevi limitate.', flush=True)


def update_docker():
    if sys.platform != 'win32':
        return True
    if not shutil.which('winget'):
        print('Serve il tuo intervento: nella finestra Docker premi Update, completa l’aggiornamento e riprova.', flush=True)
        return False
    print('Preparazione: aggiorno Docker Desktop tramite il gestore ufficiale Windows.', flush=True)
    try:
        result = subprocess.run(['winget', 'upgrade', '--id', 'Docker.DockerDesktop', '--exact',
                                 '--source', 'winget', '--silent', '--disable-interactivity'], timeout=900)
    except (OSError, subprocess.TimeoutExpired):
        print('Aggiornamento Docker non completato entro il limite.', flush=True)
        return False
    if result.returncode != 0:
        print('Il gestore non ha completato un aggiornamento. Controlla Update nella finestra Docker.', flush=True)
        print('Nessuna nuova esecuzione IA avviata da questo comando.', flush=True)
        return False
    print('Il gestore Windows ha completato l’aggiornamento Docker. Nessun riavvio del PC imposto.', flush=True)
    return True


def app_running():
    value = os.environ.get('APP_PORT') or dotenv_values(ROOT / '.env').get('APP_PORT') or '8765'
    port = int(value)
    if not 1024 <= port <= 65535:
        raise ValueError('Porta locale non valida.')
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health', timeout=3) as response:
            health = json.loads(response.read(12000))
        return isinstance(health, dict) and health.get('service') == 'ok'
    except (OSError, ValueError):
        return False


def main():
    try:
        ref = sys.argv[1]
        if app_running():
            print('Officina è ancora aperta. Nella sua finestra del terminale premi Ctrl+C, poi ripeti questo comando.', flush=True)
            print('Nessun file è stato modificato.', flush=True)
            return 1
        update_code(ref)
        configure_free_profile()
        if '--aggiorna-docker' in sys.argv and not update_docker():
            return 1
        print('Riprendo la prova salvata. La chiave resta sul PC e i contatori non vengono azzerati.', flush=True)
        sys.path.insert(0, str(ROOT))
        from scripts import avvio_automatico
        sys.argv.append('--riprova-verifica')
        return avvio_automatico.main()
    except KeyboardInterrupt:
        print('Aggiornamento interrotto. Chiave e memoria conservate.', flush=True)
        return 130
    except Exception as exc:
        print(f'Aggiornamento non completato ({type(exc).__name__}). Nessuna chiave viene mostrata.', flush=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
