from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest
from main import ActivityStore


class ActivityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.filename = Path(self.temp.name) / 'test.sqlite3'
        self.store = ActivityStore(self.filename)

    def test_create_and_list(self):
        status, activity = self.store.create('Compito', 'one')
        self.assertEqual(status, 201)
        self.assertEqual(self.store.all(), [activity])

    def test_repeated_request(self):
        _, first = self.store.create('Compito', 'one')
        status, second = self.store.create('Compito', 'one')
        self.assertEqual(status, 200)
        self.assertEqual(first, second)
        self.assertEqual(len(self.store.all()), 1)

    def test_conflicting_request(self):
        self.store.create('Compito', 'one')
        self.assertEqual(self.store.create('Altro', 'one')[0], 409)

    def test_invalid_titles(self):
        for value in ('', '   ', None, 42, 'x' * 201):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.store.create(value, 'one')
        self.assertEqual(self.store.all(), [])

    def test_missing_key(self):
        for key in ('', None, 'x' * 201):
            with self.assertRaises(ValueError):
                self.store.create('Compito', key)

    def test_restart_persistence(self):
        _, first = self.store.create('Compito', 'one')
        reopened = ActivityStore(self.filename)
        self.assertEqual(reopened.all(), [first])
        self.assertEqual(reopened.create('Compito', 'one'), (200, first))

    def test_concurrent_idempotency(self):
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(lambda _: self.store.create('Compito', 'parallel'), range(8)))
        self.assertEqual(sum(code == 201 for code, _ in results), 1)
        self.assertEqual(len({item['id'] for _, item in results}), 1)

    def test_sql_is_data(self):
        title = "'; DROP TABLE activities; --"
        _, item = self.store.create(title, 'sql')
        self.assertEqual(self.store.all(), [item])
