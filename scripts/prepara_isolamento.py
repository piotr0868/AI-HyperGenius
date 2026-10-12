"""Scarica tramite Docker (digest verificato) e registra la sola immagine, mai segreti."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    try:
        subprocess.run(['docker', 'info', '--format', '{{.OSType}}'], check=True)
        subprocess.run(['docker', 'pull', 'python:3.12-slim'], check=True)
        digest = subprocess.check_output(['docker', 'image', 'inspect', 'python:3.12-slim',
            '--format', '{{index .RepoDigests 0}}'], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        print('Avvia Docker Desktop in modalità Linux, poi riprova. Nessun codice verrà eseguito sul PC.')
        return 1
    if '@sha256:' not in digest:
        print('Digest immagine non disponibile: isolamento non abilitato.')
        return 1
    path = ROOT / '.env'
    lines = path.read_text(encoding='utf-8').splitlines() if path.exists() else (ROOT / '.env.example').read_text().splitlines()
    lines = [line for line in lines if not line.startswith('SANDBOX_IMAGE=')]
    lines.append('SANDBOX_IMAGE=' + digest)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    if sys.platform != 'win32':
        path.chmod(0o600)
    print('Immagine fissata:', digest)
    print('Isolamento preparato. Riavvia Officina se è già aperta.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
