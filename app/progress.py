"""Recupero di avanzamento per il solo contratto backend attivita'.

Il sistema prepara prove dichiarate; non fornisce mai un backend sostitutivo.
"""
import hashlib
import json
from pathlib import Path

TEST_PATH = 'tests/test_officina_contract.py'
TEMPLATE = Path(__file__).with_name('templates') / 'test_activity_api.py.txt'
README = '''# Backend attivita'

L'implementazione e' in main.py. Consultare la cronologia di Officina per le
scritture del modello e le eventuali correzioni. Questo README e la base di test
tests/test_officina_contract.py sono predisposti dal sistema, non dal modello.

Il backend offre GET /activities e POST /activities con JSON {"title":"Compito"}
e intestazione Idempotency-Key. Le richieste ripetute non devono creare duplicati;
la stessa chiave con dati diversi restituisce 409. SQLite conserva i dati.

L'avvio previsto e' python main.py --port 8000 --db /data/activities.sqlite3,
esclusivamente in un container con volume dedicato per /data. Il codice generato
non va eseguito direttamente sul PC. Officina esegue le prove nel proprio
container isolato, senza rete, file personali o credenziali.

I test HTTP controllano creazione, consultazione, input, chiave obbligatoria,
idempotenza, conflitti e persistenza dopo riavvio. Si eseguono nel container con
python -m unittest discover -s tests -v. Officina aggiunge il contratto indipendente
e mostra Pronto solo dopo tutte le prove passate sui file correnti.
'''


def system_test_record(store, pid):
    rows = store.rows("SELECT detail FROM events WHERE project_id=? AND kind='file_sistema' ORDER BY id DESC", (pid,))
    return next((value for row in rows if (value := json.loads(row['detail'])).get('path') == TEST_PATH), None)


def system_checks_active(store, pid):
    record = system_test_record(store, pid)
    if not record:
        return False
    path = store.safe_path(pid, TEST_PATH)
    return path.exists() and hashlib.sha256(path.read_text(encoding='utf-8').encode()).hexdigest() == record['sha256']


def is_test_path(name):
    path = Path(name)
    return path.as_posix().startswith('tests/') and path.name.startswith('test') and path.suffix == '.py'


async def prepare_contract_checks(agent, pid, remaining):
    p = agent.store.project(pid)
    if (p['control'] != 'run' or p['state'] == 'Pronto' or remaining <= 0
            or p['elapsed'] >= agent.settings.task_timeout or p['failed_checks'] > agent.settings.max_corrections
            or not p['plan'] or not p['criteria'] or not p['docs_consulted']):
        return False
    files = agent.store.files(pid)
    if 'main.py' not in files or any(is_test_path(name) for name in files):
        return False
    versions = agent.store.rows('SELECT path FROM versions WHERE project_id=?', (pid,))
    if any(is_test_path(row['path']) for row in versions):
        return False  # Non ricreare test rimossi intenzionalmente.
    writes = sum(Path(row['path']).as_posix() == 'main.py' for row in versions)
    duplicates = any(Path(json.loads(row['detail']).get('path', '')).as_posix() == 'main.py' for row in
                     agent.store.rows("SELECT detail FROM events WHERE project_id=? AND kind='scrittura_invariata'", (pid,)))
    if writes < 2 and not duplicates and p['model_calls'] < agent.settings.max_model_calls:
        return False

    bundle = {TEST_PATH: TEMPLATE.read_text(encoding='utf-8')}
    for name, content in [('tests/__init__.py', '# Package dei test. Preparato dal sistema Officina.\n'), ('README.md', README)]:
        if name not in files and not any(row['path'] == name for row in versions):
            bundle[name] = content
    combined = {**files, **bundle}
    if (p['tool_calls'] + len(bundle) + 2 > agent.settings.max_tool_calls
            or len(combined) > 100 or sum(len(value.encode()) for value in combined.values()) > 2000000):
        return False  # Riserva verifica e certificazione, senza aumentare i budget.

    backend_hash = hashlib.sha256(files['main.py'].encode()).hexdigest()
    for name, content in bundle.items():
        await agent.perform(pid, 'write_file', {'path': name, 'content': content})
        agent.store.event(pid, 'file_sistema', {
            'actor': 'system', 'model_called': False, 'path': name,
            'sha256': hashlib.sha256(content.encode()).hexdigest(),
            'reason': 'repeated_backend_writes_without_tests'})
    history = agent.store.project(pid)['history']
    history.append({'role': 'user', 'content':
        'Il sistema ha predisposto una base dichiarata di test HTTP del contratto e, se mancavano, '
        'istruzioni di avvio e package dei test. Non sono file generati dal modello. '
        f'File preparati: {json.dumps(list(bundle))}. main.py e\' invariato. '
        'Usa queste prove per correggere l’implementazione; non riscriverle per nascondere errori.'})
    agent.store.update(pid, history=history)
    agent.store.event(pid, 'avanzamento_guidato', {
        'actor': 'system', 'model_called': False, 'files': list(bundle), 'backend_sha256': backend_hash})
    return True
