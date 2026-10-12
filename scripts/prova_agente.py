"""Accettazione end-to-end con il vero SDK; nessun modello simulato o ripiego."""
import asyncio
from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.agent import Agent
from app.config import load_settings
from app.sandbox import Sandbox
from app.storage import Store

GOAL = 'Crea un backend locale per attività con SQLite, API per creare e consultare, input validati, richieste idempotenti e persistenza dopo riavvio. Scrivi unittest e README.'


async def main():
    config = load_settings()
    if not config.api_key:
        print('NON ESEGUITA: manca AI_PROVIDER_KEY nel file locale .env. Non è stata fatta alcuna chiamata IA.')
        return 2
    settings = replace(config, data_dir=config.data_dir / 'live-acceptance')
    store, sandbox = Store(settings.data_dir), Sandbox(settings)
    agent = Agent(settings, store, sandbox)
    try:
        project = store.create_project(GOAL)
        await agent.run(project['id'])
        final = store.project(project['id'])
        evidence = {'generation': {k: v for k, v in final.items() if k != 'history'}, 'repair': None, 'ai_used': True}
        if final['state'] != 'Pronto':
            print('Generazione non completata:', final['summary'])
            outcome = 1
        else:
            repair = store.create_project('Verifica separata: i file sono una copia di un backend già verificato. In regression_target.py è stato introdotto un difetto. Prima di modificarlo riproduci l’errore con run_checks, poi correggi il comportamento: normalize_title deve togliere spazi ai bordi. Non cambiare i test, ripeti tutte le prove e concludi soltanto quando passano.')
            rid = repair['id']
            for name, content in store.files(project['id']).items():
                store.write_file(rid, name, content)
            store.write_file(rid, 'regression_target.py', 'def normalize_title(value):\n    return value\n')
            store.write_file(rid, 'tests/test_regression_injected.py', 'import unittest\nfrom regression_target import normalize_title\nclass Regression(unittest.TestCase):\n    def test_strip(self):\n        self.assertEqual(normalize_title("  attività  "), "attività")\n')
            await agent.run(rid)
            result = store.project(rid)
            checks = [e for e in reversed(store.events(rid)) if e['kind'] == 'verifica']
            detected = bool(checks) and checks[0]['detail'].get('passed') is False
            corrected = result['state'] == 'Pronto' and bool(checks) and checks[-1]['detail'].get('passed') is True
            original_unchanged = store.digest(project['id']) == final['verified_hash']
            evidence['repair'] = {'project': {k: v for k, v in result.items() if k != 'history'},
                'detected_initial_fault': detected, 'corrected_and_retested': corrected,
                'original_unchanged': original_unchanged, 'checks': checks}
            outcome = 0 if detected and corrected and original_unchanged else 1
        path = settings.data_dir / 'RESULTS.json'
        path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Risultati salvati:', path)
        print('ACCETTAZIONE IA:', 'PASSATA' if outcome == 0 else 'NON COMPLETATA')
        return outcome
    finally:
        await agent.shutdown()
        store.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
