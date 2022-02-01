import pytest
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.users.manager import UsersManager
from src.backend.users.sql import User

DB = "testdatabase.db"
engine = create_engine("sqlite:///{}".format(DB), echo=True)
Session = sessionmaker(bind=engine)

@pytest.fixture(autouse=True)
def setup_and_cleanup_database():
    if os.path.exists(DB):
        os.remove(DB)
    yield
    
    if os.path.exists(DB):
        os.remove(DB)

class TestUsersManager:
    def test_fields(self):
        session = Session()
        man = UsersManager(session)
        assert man.session is session
        session.close()
    
    def test_search_empty(self):
        session = Session()
        man = UsersManager(session)
        assert man.search() == []
        session.close()
    
    def test_add_new_tuple(self):
        session = Session()
        man = UsersManager(session)
        new_usr = ("foo", "bar")
        man.add_new(new_usr)
        added_usr, = man.search()
        assert (added_usr.name, added_usr.password) == new_usr
        session.close()
    
    def test_add_new_dict(self):
        session = Session()
        man = UsersManager(session)
        new_usr = dict(name="foo", password="bar")
        man.add_new(new_usr)
        added_usr, = man.search()
        assert added_usr.name == new_usr['name']
        assert added_usr.password == new_usr['password']
        session.close()
