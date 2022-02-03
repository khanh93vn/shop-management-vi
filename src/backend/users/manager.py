from sqlalchemy import String
from .sql import User

class UsersManager:
    data_class = User
    
    def __init__(self, session):
        self.session = session
    
    def search(self, **info):
        query = self.session.query(self.data_class)
        for key, value in info.items():
            col = getattr(self.data_class, key)
            if isinstance(col.type, String):
                query = query.filter(col.like('%'+value+'%'))
            else:
                query = query.filter(col == value)
        return query.all()
    
    def get_row(self, column, value):
        pass
    
    def add_new(self, data):
        pass
        # if isinstance(data, dict)
            # entry = self.data_class(**data)
        # elif isinstance(data, (tuple, list)):
            # entry = self.data_class(
                # **{key:value 
                #    for key, value in
                #    zip(self.data_class.__table__.columns.keys(), data)})
        # else:
            # raise TypeError("Must be a dict, tuple or list")
        # self.session.add(entry)
        # self.session.commit()
    
    def delete(self, id):
        pass
    
    def update(self, id, data):
        pass
