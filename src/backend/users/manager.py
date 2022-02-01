from .sql import User

class UsersManager:
    data_class = User
    
    def __init__(self, session):
        self.session = session
    
    def search(self, info):
        pass
    
    def get_row(self, column, value):
        pass
    
    def add_new(self, data):
        pass
    
    def delete(self, id):
        pass
    
    def update(self, id, data):
        pass
