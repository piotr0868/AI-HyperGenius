from pathlib import Path
import pytest

from app.storage import Store


@pytest.fixture
def store(tmp_path):
    store = Store(tmp_path)
    yield store
    store.close()


def test_memory_and_files_survive_restart(tmp_path):
    store = Store(tmp_path)
    p = store.create_project('Backend con dati persistenti')
    store.update(p['id'], criteria=['Dati conservati'], plan=['Crea database'])
    store.write_file(p['id'], 'main.py', 'print(1)\n')
    store.close()
    reopened = Store(tmp_path)
    reopened.recover()
    assert reopened.project(p['id'])['criteria'] == ['Dati conservati']
    assert reopened.project(p['id'])['state'] == 'Serve il tuo intervento'
    assert reopened.files(p['id']) == {'main.py': 'print(1)\n'}
    assert any(e['kind'] == 'recupero' for e in reopened.events(p['id']))
    reopened.close()


@pytest.mark.parametrize('name', ['../secrets.txt', '/etc/passwd', '.env', 'sub/.git/config', 'C:\\Users\\secret.txt', 'folder/../../x.py'])
def test_paths_cannot_escape_workspace(store, name):
    p = store.create_project('Progetto di prova')
    with pytest.raises(ValueError):
        store.write_file(p['id'], name, 'unauthorized')


def test_symlink_cannot_escape_workspace(store, tmp_path):
    p = store.create_project('Progetto di prova')
    secret = tmp_path / 'personal.txt'
    secret.write_text('personal')
    (store.workspace(p['id']) / 'trap.txt').symlink_to(secret)
    with pytest.raises(ValueError):
        store.write_file(p['id'], 'trap.txt', 'replace')
    assert secret.read_text() == 'personal'


def test_rollback_preserves_previous_content_and_invalidates_evidence(store):
    p = store.create_project('Progetto di prova')
    store.write_file(p['id'], 'main.py', 'old')
    version = store.write_file(p['id'], 'main.py', 'new')['previous_version']
    store.update(p['id'], state='Pronto', verified_hash=store.digest(p['id']))
    store.rollback(p['id'], version)
    assert store.files(p['id'])['main.py'] == 'old'
    assert store.project(p['id'])['verified_hash'] is None
    assert store.project(p['id'])['state'] == 'Serve il tuo intervento'


def test_retrieval_returns_relevant_chunks_with_provenance(store):
    store.add_document('SQLite', 'https://docs.python.org/3/library/sqlite3.html', '2026-10-12', 'SQLite: transazioni, persistenza, idempotenza e database.')
    store.add_document('Giardinaggio', 'Tutorial personale', '2026-10-11', 'Come coltivare tulipani sul balcone.')
    docs = store.search('backend SQLite persistente')
    assert len(docs) == 1
    assert docs[0]['title'] == 'SQLite' and docs[0]['source_date'] == '2026-10-12'
    assert store.search('unrelatedzzzz') == []


def test_workspace_size_limit_preserves_old_file(store):
    p = store.create_project('Progetto di prova')
    store.write_file(p['id'], 'main.py', 'old')
    with pytest.raises(ValueError):
        store.write_file(p['id'], 'main.py', 'x' * 128001)
    assert store.files(p['id'])['main.py'] == 'old'
