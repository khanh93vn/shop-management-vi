from ..base.sql import *

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    name = Column(String(50))
    password = Column(String(30))
