import pytest
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.users.manager import UsersManager
from src.backend.base.sql import Base
from src.backend.users.sql import User

DB = "testdatabase.db"
engine = create_engine("sqlite:///{}".format(DB), echo=True)
Session = sessionmaker(bind=engine)

@pytest.fixture(autouse=True, scope='function')
def setup_and_cleanup_database():
    if os.path.exists(DB):
        os.remove(DB)
    Base.metadata.create_all(engine)
    yield
    
    if os.path.exists(DB):
        os.remove(DB)

class TestUsersManager:
    def test_fields(self):
        with Session() as session:
            man = UsersManager(session)
        assert man.session is session
    
    def test_search_empty(self):
        with Session() as session:
            man = UsersManager(session)
        assert man.search() == []
    
    def test_add_new_tuple(self):
        with Session() as session:
            Base.metadata.create_all(engine)
            man = UsersManager(session)
            new_usr = ("foo", "bar")
            man.add_new(new_usr)
            added_usr, = man.search()
        assert (added_usr.name, added_usr.password) == new_usr
    
    def test_add_new_dict(self):
        with Session() as session:
            Base.metadata.create_all(engine)
            man = UsersManager(session)
            new_usr = dict(name="foo", password="bar")
            man.add_new(new_usr)
            added_usr, = man.search()
        assert added_usr.name == new_usr['name']
        assert added_usr.password == new_usr['password']
