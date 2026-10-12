"""Verifica reale in Docker senza chiamare un modello IA."""
import asyncio
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.config import load_settings
from app.sandbox import Sandbox


async def main():
    root = ROOT / 'examples' / 'activity_backend'
    files = {p.relative_to(root).as_posix(): p.read_text(encoding='utf-8')
             for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py', '.md')}
    sandbox = Sandbox(load_settings())
    good = await sandbox.verify(files, 'local-acceptance')
    broken = dict(files)
    before = 'if not isinstance(title, str) or not title.strip() or len(title.strip()) > 200:'
    after = 'if not isinstance(title, str) or len(title.strip()) > 200:'
    assert before in broken['main.py'], 'Punto di iniezione del difetto non trovato.'
    broken['main.py'] = broken['main.py'].replace(before, after)
    fault = await sandbox.verify(broken, 'local-fault')
    # Il ripristino è operato da questo script, non da un agente IA.
    restored = await sandbox.verify(files, 'local-restored')
    evidence = {'reference_backend': good, 'intentional_fault': fault, 'restored_reference': restored,
                'fault_detection_passed': not fault['passed'] and fault.get('check', {}).get('unit_failures', 0) > 0,
                'ai_used': False, 'note': 'La correzione di questa prova è un ripristino deterministico; la prova di correzione IA è separata.'}
    path = ROOT / '.data' / 'verification' / 'local_acceptance.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Backend di riferimento:', 'VERIFICATO' if good['passed'] else 'NON VERIFICATO')
    print('Difetto introdotto:', 'RILEVATO' if evidence['fault_detection_passed'] else 'NON RILEVATO')
    print('Ripristino del riferimento:', 'VERIFICATO' if restored['passed'] else 'NON VERIFICATO')
    print('Questa prova non usa IA. Risultati completi:', path)
    if '--dettagli' in sys.argv:
        print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0 if good['passed'] and evidence['fault_detection_passed'] and restored['passed'] else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
