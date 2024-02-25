import unittest

from tinydb import TinyDB
from chessapp.util.database import update_table
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from chessapp.util.database import update_table

s_initial_docs = [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Doe"},
    {"id": 3, "name": "Smith"},
    {"id": 7, "name": "Peter"},
    {"id": 8, "name": "Paaarker"},
    {"id": 6, "name": "Tina"}
]
s_upserted_docs = [
    {"id": 1, "name": "Jane"},
    {"id": 4, "name": "Johnson"},
    {"id": 5, "name": "Dow"},
    {"id": 3, "name": "Schmidt"},
    {"id": 8, "name": "Parker"}
]
s_expected_docs = [
    {"id": 1, "name": "Jane"},
    {"id": 2, "name": "Doe"},
    {"id": 3, "name": "Schmidt"},
    {"id": 4, "name": "Johnson"},
    {"id": 5, "name": "Dow"},
    {"id": 6, "name": "Tina"},
    {"id": 7, "name": "Peter"},
    {"id": 8, "name": "Parker"}
]


class TestUpsertMultiple(unittest.TestCase):

    def test_upsert_multiple(self):
        db = TinyDB(storage=MemoryStorage)
        table = db.table("test")
        table.insert_multiple(s_initial_docs)
        update_table(table, s_upserted_docs)
        self.assertEqual(table.all().sort(
            key=lambda x: x["id"]), s_expected_docs.sort(key=lambda x: x["id"]))
