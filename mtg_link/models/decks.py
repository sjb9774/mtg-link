from sqlalchemy import Table, Column, VARCHAR, Integer, Boolean, ForeignKey, Enum, Date, Float, Integer
from sqlalchemy.orm import  relationship
from mtg_link import db
from mtg_link.mtg.magic import MtgCard, MtgCardSet, ManaSymbol, Type, Subtype
from mtg_link.mtg.colors import Color
from mtg_link.mtg import ALL_COLOR_COMBINATIONS, TYPES, SET_TYPES

class Deck(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'decks'

    user_id = Column(VARCHAR(db.id_length), ForeignKey('users.id'))
    name = Column(VARCHAR(200))
    create_date = Column(Date())
    deck_index = Column(Integer, default=0)
    root_deck_id = Column(VARCHAR(db.id_length))
    sanitized_name = Column(VARCHAR(200))

class XDeckCard(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'x_decks_cards'

    deck_id = Column(VARCHAR(db.id_length), ForeignKey('decks.id'))
    card_id = Column(VARCHAR(db.id_length), ForeignKey('cards.id'))
    quantity = Column(Integer, default=1)
