"""Consegna riproducibile della sola applicazione, con esclusione esplicita dei segreti."""
import hashlib
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent
TOP = {'.env.example', '.gitignore', 'README.md', 'STATO_PROGETTO.md', 'RISULTATI_VERIFICHE.md',
       'VERIFICHE.json', 'pyproject.toml', 'uv.lock', 'requirements.lock', 'avvia.py',
       'installa.bat', 'avvia.bat', 'configura_ia.bat', 'prepara_isolamento.bat', 'verifica_senza_ia.bat'}
DIRS = {'app', 'scripts', 'tests', 'examples', 'resources'}


def main():
    path = ROOT.parent / 'Officina-v0.1.zip'
    files = [p for p in ROOT.rglob('*') if p.is_file() and
        (p.relative_to(ROOT).as_posix() in TOP or p.relative_to(ROOT).parts[0] in DIRS) and
        not set(p.relative_to(ROOT).parts).intersection({'.env', '.git', '.data', '.venv', '__pycache__', '.pytest_cache'})
        and p.suffix not in ('.pyc', '.sqlite3', '.db') and not p.is_symlink()]
    manifest = []
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(files):
            name = file.relative_to(ROOT).as_posix()
            content = file.read_bytes()
            if file.suffix == '.bat':
                content = content.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
            archive.writestr('Officina/' + name, content)
            manifest.append(hashlib.sha256(content).hexdigest() + '  ' + name)
        archive.writestr('Officina/MANIFEST.sha256', '\n'.join(manifest) + '\n')
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert not any(set(Path(name).parts).intersection({'.env', '.data', '.venv', '.git'}) for name in archive.namelist())
        assert 'Officina/avvia.bat' in archive.namelist()
        assert 'Officina/resources/evidence/pytest.xml' in archive.namelist()
    print(f'Pacchetto verificato: {path} ({path.stat().st_size} byte, {len(files)} file, nessun segreto o dato di progetto).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
