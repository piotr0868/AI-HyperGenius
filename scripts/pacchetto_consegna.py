"""Confeziona il backend separato senza credenziali, dati locali o dipendenze."""
import hashlib
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'examples/attivita_consegna'
ALLOWED = {'main.py', 'Dockerfile', '.dockerignore', 'AVVIA.bat', 'FERMA.bat',
           'LEGGIMI.txt', 'RISULTATI.json', 'tests/__init__.py', 'tests/test_api.py',
           'web/index.html', 'web/app.js'}


def main():
    output = ROOT / 'resources/consegne/Backend-attivita.zip'
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = []
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(ALLOWED):
            data = (SOURCE / name).read_bytes()
            if name.endswith('.bat'):
                data = data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
            info = zipfile.ZipInfo(name, (2026, 10, 14, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
            manifest.append(hashlib.sha256(data).hexdigest() + '  ' + name)
        info = zipfile.ZipInfo('MANIFEST.sha256', (2026, 10, 14, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, '\n'.join(manifest) + '\n')
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        for row in manifest:
            digest, name = row.split('  ', 1)
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
        assert len(archive.namelist()) == len(ALLOWED) + 1
        for name in ('AVVIA.bat', 'FERMA.bat'):
            assert b'\n' not in archive.read(name).replace(b'\r\n', b'')
    shutil.copyfile(output, ROOT.parent / output.name)
    print(f'Consegna verificata: {output}; {output.stat().st_size} byte; {len(ALLOWED)} file e manifest.')


if __name__ == '__main__':
    main()
