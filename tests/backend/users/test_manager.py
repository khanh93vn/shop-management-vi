import pytest
import os
# from src.backend.users.manager import UsersManager

DB = "testdatabase.db"

@pytest.fixture(autouse=True)
def setup_and_cleanup_database():
    if os.path.exists(DB):
        os.remove(DB)
    
    yield
    
    if os.path.exists(DB):
        os.remove(DB)
