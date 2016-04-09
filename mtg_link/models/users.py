from sqlalchemy import Table, Column, VARCHAR, Integer, Boolean, ForeignKey, Enum, DateTime, Float
from mtg_link import db

class User(db.Base, db.IdMixin, db.DefaultMixin):

    first_name = Column(VARCHAR(200))
    last_name = Column(VARCHAR(200))
    username = Column(VARCHAR(200))
    password = Column(VARCHAR(1000))
