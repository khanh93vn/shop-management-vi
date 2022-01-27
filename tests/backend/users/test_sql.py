import pytest
from src.backend.users.sql import User

class TestUser:
    def test_fields(self):
        name = "khanh"
        password = "123"
        usr = User(name=name, password=password)
        assert (usr.name, usr.password) == (name, password)
    