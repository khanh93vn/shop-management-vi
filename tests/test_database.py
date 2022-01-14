import pytest
import os

from src.database import *

DB = "testdatabase.db"

@pytest.fixture(autouse=True)
def setup_and_cleanup_database():
    if os.path.exists(DB):
        os.remove(DB)
    
    yield
    
    if os.path.exists(DB):
        os.remove(DB)


class TestDatabase:
    def test_init(self):
        db = Database(DB)
        assert db.dbname == DB
    
    def test_connDB(self):
        db = Database(DB)
        db.connDB()
        assert db.conn
        assert db.cursor
    
    def test_createDB(self):
        db = Database(DB)
        db.createDB()
        db.connDB()
        table_names = db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        assert ("users",) in table_names
        users = db.cursor.execute("SELECT * FROM users").fetchall()
        assert users[0] == (1, 'Admininstrator', 'admin', '12345')
    
    def test_queryDB_select(self):
        db = Database(DB)
        db.createDB()
        data = db.queryDB("SELECT * FROM users")
        assert data[0] == (1, 'Admininstrator', 'admin', '12345')
    
    def test_queryDB_create_table(self):
        db = Database(DB)
        db.queryDB("CREATE TABLE tests (id INTEGER PRIMARY KEY AUTOINCREMENT, name)")
        assert ("tests",) in db.queryDB("SELECT name FROM sqlite_master WHERE type='table'")
    
    def test_queryDB_insert(self):
        db = Database(DB)
        db.queryDB("CREATE TABLE tests (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        db.queryDB("INSERT INTO tests VALUES (1, 'test insert')")
        assert db.queryDB("SELECT * FROM tests") == [(1, "test insert")]
    
    def test_list_tables(self):
        db = Database(DB)
        db.createDB()
        table_names = db.list_tables()
        assert "users" in table_names
    
class TestMedStoreDatabase:
    tables = [
        ("products",),
        ("suppliers",),
        ("customers",),
        ("bills",),
        ("batches",),
        ("stock",),
    ]
    @pytest.mark.parametrize("table_name", tables)
    def test_createDB_tables(self, table_name):
        db = MedStoreDatabase(DB)
        db.createDB()
        table_names = db.queryDB("SELECT name from sqlite_master WHERE type='table'")
        assert table_name in table_names
    
    def test_createDB_while_exists(self):
        pass