from sqlalchemy import Table, Column, VARCHAR, Integer, Boolean, ForeignKey
from sqlalchemy import Enum, DateTime, Float
from sqlalchemy.orm import relationship
from mtg_link import db
from mtg_link.models.decks import Deck

class User(db.Base, db.IdMixin, db.DefaultMixin):

    first_name = Column(VARCHAR(200))
    last_name = Column(VARCHAR(200))
    username = Column(VARCHAR(200))
    password = Column(VARCHAR(1000))
    decks = relationship('Deck')
