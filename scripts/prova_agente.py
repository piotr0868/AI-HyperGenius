"""Accettazione reale riprendibile; nessun modello simulato o ripiego."""
import asyncio
from dataclasses import replace
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.agent import Agent
from app.config import load_settings
from app.sandbox import Sandbox
from app.storage import Store

GOAL = 'Crea un backend locale per attività con SQLite, API per creare e consultare, input validati, richieste idempotenti e persistenza dopo riavvio. Scrivi unittest e README.'
REPAIR_GOAL = 'Verifica separata: i file sono una copia di un backend già verificato. In regression_target.py è stato introdotto un difetto. Prima di modificarlo riproduci l’errore con run_checks, poi correggi il comportamento: normalize_title deve togliere spazi ai bordi. Non cambiare i test, ripeti tutte le prove e concludi soltanto quando passano.'


def read_json(path):
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def save_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def seed_documentation(store):
    path = ROOT / 'resources' / 'official_docs.json'
    if path.exists():
        for document in json.loads(path.read_text(encoding='utf-8')):
            if not store.rows('SELECT id FROM documents WHERE source=? AND source_date=? LIMIT 1',
                              (document['source'], document['source_date'])):
                store.add_document(**document)


def saved_project(store, pid, description):
    try:
        project = store.project(pid)
        return project if project['description'] == description else None
    except (KeyError, TypeError):
        return None


async def run_or_recheck(agent, store, sandbox, project):
    pid = project['id']
    if project['state'] == 'Pronto' and project['verified_hash'] == store.digest(pid):
        result = await sandbox.verify(store.files(pid), pid)
        digest = store.digest(pid)
        ok = result['passed'] and digest == project['verified_hash']
        store.event(pid, 'verifica', result)
        store.update(pid, last_check=result, verified_hash=digest if ok else None,
                     state='Pronto' if ok else 'Serve il tuo intervento',
                     failed_checks=project['failed_checks'] + (not ok))
        if ok:
            return store.project(pid)
    store.update(pid, control='run')
    await agent.run(pid)
    return store.project(pid)


async def main():
    config = load_settings()
    if not config.api_key:
        print(f'NON ESEGUITA: manca {config.credential_var} nel file locale .env. Nessuna chiamata IA. Fornitore: {config.provider}.')
        return 2
    settings = replace(config, data_dir=config.data_dir / 'live-acceptance')
    store, sandbox = Store(settings.data_dir), Sandbox(settings)
    agent = Agent(settings, store, sandbox)
    result_path = settings.data_dir / 'RESULTS.json'
    checkpoint_path = settings.data_dir / 'RUN.json'
    previous = read_json(result_path)
    checkpoint = read_json(checkpoint_path)
    try:
        seed_documentation(store)
        if previous:
            archive = settings.data_dir / 'runs'
            archive.mkdir(exist_ok=True)
            save_json(archive / (uuid.uuid4().hex + '.json'), previous)
        if '--nuova-prova' in sys.argv:
            checkpoint = {}
            previous = {}
        generation_id = checkpoint.get('generation_id') or previous.get('generation', {}).get('id')
        project = saved_project(store, generation_id, GOAL)
        if project:
            print('Riprendo la generazione salvata: file, storia e contatori dei limiti conservati.', flush=True)
        else:
            project = store.create_project(GOAL)
            checkpoint = {}
        checkpoint['generation_id'] = project['id']
        save_json(checkpoint_path, checkpoint)
        final = await run_or_recheck(agent, store, sandbox, project)
        evidence = {'generation': {k: v for k, v in final.items() if k != 'history'},
                    'repair': None, 'ai_used': True, 'limits_preserved_on_resume': True}
        save_json(result_path, evidence)
        if final['state'] != 'Pronto':
            print('Generazione non completata:', final['summary'])
            outcome = 1
        else:
            old_repair = (previous.get('repair') or {}).get('project') or {}
            repair_id = checkpoint.get('repair_id') or old_repair.get('id')
            repair = saved_project(store, repair_id, REPAIR_GOAL)
            if repair:
                if old_repair.get('id') == repair['id']:
                    checkpoint['fault_injected'] = True
                print('Riprendo la copia di correzione salvata, senza reintrodurre il difetto.', flush=True)
            else:
                repair = store.create_project(REPAIR_GOAL)
                checkpoint['fault_injected'] = False
            rid = repair['id']
            checkpoint['repair_id'] = rid
            save_json(checkpoint_path, checkpoint)
            if not checkpoint.get('fault_injected'):
                for name, content in store.files(project['id']).items():
                    store.write_file(rid, name, content)
                store.write_file(rid, 'regression_target.py', 'def normalize_title(value):\n    return value\n')
                store.write_file(rid, 'tests/test_regression_injected.py', 'import unittest\nfrom regression_target import normalize_title\nclass Regression(unittest.TestCase):\n    def test_strip(self):\n        self.assertEqual(normalize_title("  attività  "), "attività")\n')
                checkpoint['fault_injected'] = True
                save_json(checkpoint_path, checkpoint)
            result = await run_or_recheck(agent, store, sandbox, store.project(rid))
            checks = [e for e in reversed(store.events(rid)) if e['kind'] == 'verifica']
            detected = bool(checks) and checks[0]['detail'].get('passed') is False
            corrected = result['state'] == 'Pronto' and bool(checks) and checks[-1]['detail'].get('passed') is True
            original_unchanged = store.digest(project['id']) == final['verified_hash']
            evidence['repair'] = {'project': {k: v for k, v in result.items() if k != 'history'},
                'detected_initial_fault': detected, 'corrected_and_retested': corrected,
                'original_unchanged': original_unchanged, 'checks': checks}
            outcome = 0 if detected and corrected and original_unchanged else 1
        save_json(result_path, evidence)
        print('Risultati salvati:', result_path)
        print('ACCETTAZIONE IA:', 'PASSATA' if outcome == 0 else 'NON COMPLETATA')
        return outcome
    finally:
        await agent.shutdown()
        store.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
