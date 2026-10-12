import io
import zipfile
from fastapi.testclient import TestClient
import pytest

from app.config import Settings
from app.main import create_app
from app.storage import Store


@pytest.fixture
def api(tmp_path):
    store = Store(tmp_path)
    app = create_app(Settings(data_dir=tmp_path), store=store)
    with TestClient(app, base_url='http://localhost:8765') as client:
        token = client.get('/api/session').json()['token']
        client.headers['X-App-Token'] = token
        yield client, store
    store.close()


def test_missing_key_reports_intervention_never_ready(api):
    client, store = api
    health = client.get('/api/health').json()
    assert health['ai_configured'] is False
    created = client.post('/api/projects', json={'description': 'Crea un backend per attività'}).json()
    for _ in range(10):
        project = client.get('/api/projects/' + created['id']).json()
        if project['state'] == 'Serve il tuo intervento':
            break
    assert project['state'] == 'Serve il tuo intervento'
    assert 'AI_PROVIDER_KEY' in project['summary']
    assert project['model_calls'] == 0 and project['last_check'] is None


def test_local_security_origin_token_and_host(api):
    client, _ = api
    body = {'description': 'Crea un piccolo backend'}
    assert client.post('/api/projects', json=body, headers={'X-App-Token': ''}).status_code == 403
    assert client.post('/api/projects', json=body, headers={'Origin': 'https://evil.example'}).status_code == 403
    assert client.get('/api/session', headers={'Host': 'evil.example'}).status_code == 403
    assert client.get('/').headers['Content-Security-Policy'].startswith("default-src 'self'")


def test_documents_and_procedure_version_guard(api):
    client, _ = api
    doc = {'title': 'La mia correzione', 'source': 'Tutorial trascritto', 'source_date': '2026-10-12',
           'content': 'SQLite deve usare query parametrizzate.'}
    assert client.post('/api/documents', json=doc).status_code == 201
    retrieved = client.get('/api/knowledge?q=SQLite').json()
    assert any(doc['source'] == 'Tutorial trascritto' for doc in retrieved)
    assert len({doc['id'] for doc in retrieved}) == len(retrieved)
    body = {'title': 'Idempotenza', 'trigger': 'API database', 'guidance': 'Controlla le richieste ripetute e usa test di idempotenza.',
            'examples': [{'prompt': 'Pianifica un backend di attività', 'expected_contains': ['idempotenza', 'test']}]}
    first = client.post('/api/procedures', json=body).json()
    assert client.post(f"/api/procedures/{first['id']}/activate", json={}).status_code == 409
    assert client.post(f"/api/procedures/{first['id']}/test", json={}).status_code == 409
    second = client.put(f"/api/procedures/{first['id']}", json=body).json()
    assert second['version'] == 2 and second['status'] == 'bozza'
    body['examples'][0]['expected_contains'] = ['']
    assert client.post('/api/procedures', json=body).status_code == 422


def test_export_only_project_and_readiness_invalidated(api):
    client, store = api
    p = store.create_project('Progetto da scaricare')
    store.write_file(p['id'], 'main.py', 'print("hello")')
    store.update(p['id'], state='Pronto', verified_hash=store.digest(p['id']))
    response = client.get(f"/api/projects/{p['id']}/download")
    archive = zipfile.ZipFile(io.BytesIO(response.content))
    assert set(archive.namelist()) == {'main.py', 'OFFICINA_RISULTATI.json'}
    store.safe_path(p['id'], 'main.py').write_text('changed')
    response = client.get(f"/api/projects/{p['id']}").json()
    assert response['state'] == 'Serve il tuo intervento' and response['verified_hash'] is None


def test_empty_goal_and_missing_id_are_rejected(api):
    client, _ = api
    assert client.post('/api/projects', json={'description': ' ' * 20}).status_code == 400
    assert client.get('/api/projects/' + 'a' * 32).status_code == 404
