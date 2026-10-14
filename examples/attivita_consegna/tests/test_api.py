"""Prove HTTP isolate: ogni test prepara i propri dati, senza dipendenze d'ordine."""
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from main import ActivityStore, ThreadingHTTPServer, make_handler


class APITest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.temp.name) / 'activities.sqlite3')
        self.start_server()

    def start_server(self):
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(ActivityStore(self.db)))
        self.port = self.server.server_port
        self.worker = threading.Thread(target=self.server.serve_forever, kwargs={'poll_interval': .02}, daemon=True)
        self.worker.start()

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(2)
        self.assertFalse(self.worker.is_alive())

    def tearDown(self):
        self.stop_server()
        self.temp.cleanup()

    def request(self, method='GET', payload=None, key=None, path='/activities', raw=None, origin=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=4)
        headers = {'Content-Type': 'application/json'}
        if key is not None:
            headers['Idempotency-Key'] = key
        if origin:
            headers['Origin'] = origin
        body = raw if raw is not None else json.dumps(payload).encode() if payload is not None else None
        try:
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            data = response.read()
            if response.getheader('Content-Type', '').startswith('application/json'):
                data = json.loads(data)
            return response.status, data
        finally:
            connection.close()

    def test_get_empty(self):
        self.assertEqual(self.request(), (200, []))

    def test_post_create_and_trim(self):
        status, body = self.request('POST', {'title': '  attività  '}, 'create')
        self.assertEqual(status, 201)
        self.assertIsInstance(body['id'], int)
        self.assertEqual(body['title'], 'attività')
        self.assertEqual(self.request(), (200, [body]))

    def test_post_duplicate_same(self):
        _, first = self.request('POST', {'title': 'test'}, 'repeat')
        status, second = self.request('POST', {'title': 'test'}, 'repeat')
        self.assertEqual(status, 200)
        self.assertEqual(first, second)
        self.assertEqual(self.request(), (200, [first]))

    def test_post_duplicate_diff(self):
        status, first = self.request('POST', {'title': 'test'}, 'conflict')
        self.assertEqual(status, 201)
        status, _ = self.request('POST', {'title': 'other'}, 'conflict')
        self.assertEqual(status, 409)
        self.assertEqual(self.request(), (200, [first]))

    def test_title_validation(self):
        for title in ('', '   ', 'x' * 201, 0, False, None, [], {}):
            with self.subTest(title=title):
                self.assertEqual(self.request('POST', {'title': title}, 'invalid')[0], 422)
        self.assertEqual(self.request(), (200, []))

    def test_missing_title(self):
        self.assertEqual(self.request('POST', {}, 'missing')[0], 422)

    def test_idempotency_key_validation(self):
        for key in (None, '', '   ', 'k' * 201):
            with self.subTest(key=key):
                self.assertEqual(self.request('POST', {'title': 'test'}, key)[0], 422)
        self.assertEqual(self.request(), (200, []))

    def test_invalid_json(self):
        for raw in (b'{', b'[]', b'null', b'123', b'\xff'):
            with self.subTest(raw=raw):
                self.assertEqual(self.request('POST', key='json', raw=raw)[0], 422)

    def test_oversized_body(self):
        self.assertEqual(self.request('POST', key='size', raw=b'x' * 4097)[0], 422)

    def test_unknown_path(self):
        for method in ('GET', 'POST'):
            with self.subTest(method=method):
                self.assertEqual(self.request(method, path='/missing')[0], 404)

    def test_parameterized_sql_and_unicode(self):
        title = "caffè ☕ '); DROP TABLE activities;--"
        status, item = self.request('POST', {'title': title}, 'sql')
        self.assertEqual(status, 201)
        self.assertEqual(item['title'], title)
        self.assertEqual(self.request(), (200, [item]))

    def test_persistence_across_restart(self):
        _, before = self.request('POST', {'title': 'conserva'}, 'persist')
        self.stop_server()
        self.start_server()
        self.assertEqual(self.request(), (200, [before]))
        self.assertEqual(self.request('POST', {'title': 'conserva'}, 'persist'), (200, before))
        self.assertEqual(self.request('POST', {'title': 'diversa'}, 'persist')[0], 409)

    def test_concurrent_repetition_creates_one_row(self):
        with ThreadPoolExecutor(max_workers=4) as executor:
            responses = list(executor.map(lambda _: self.request('POST', {'title': 'insieme'}, 'parallel'), range(4)))
        self.assertEqual(sum(status == 201 for status, _ in responses), 1)
        self.assertTrue(all(status in (200, 201) for status, _ in responses))
        self.assertTrue(all(body == responses[0][1] for _, body in responses))
        self.assertEqual(self.request(), (200, [responses[0][1]]))

    def test_different_keys_create_distinct_rows(self):
        _, first = self.request('POST', {'title': 'test'}, 'first')
        _, second = self.request('POST', {'title': 'test'}, 'second')
        self.assertNotEqual(first['id'], second['id'])
        self.assertEqual(self.request(), (200, [first, second]))

    def test_trimmed_duplicate_is_same(self):
        _, first = self.request('POST', {'title': '  test  '}, 'trim')
        self.assertEqual(self.request('POST', {'title': 'test'}, 'trim'), (200, first))

    def test_max_length_is_accepted(self):
        self.assertEqual(self.request('POST', {'title': 'x' * 200}, 'length')[0], 201)

    def test_home_and_script_are_accessible(self):
        status, body = self.request(path='/')
        self.assertEqual(status, 200)
        self.assertIn(b'Le mie attivit', body)
        self.assertEqual(self.request(path='/app.js')[0], 200)

    def test_cross_origin_post_is_rejected(self):
        status, _ = self.request('POST', {'title': 'test'}, 'origin', origin='https://other.invalid')
        self.assertEqual(status, 403)
        self.assertEqual(self.request(), (200, []))


if __name__ == '__main__':
    unittest.main()
