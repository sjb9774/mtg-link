from sqlalchemy import Table, Column, VARCHAR, Integer, Boolean, ForeignKey, Enum, Date, Float, Integer
from sqlalchemy.orm import relationship
from mtg_link import db
from mtg_link.models.magic import MtgCardModel, MtgCardSetModel, TypeModel, XCardType
from mtg_link.mtg import ALL_COLOR_COMBINATIONS, TYPES, SET_TYPES

class Deck(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'decks'

    user_id = Column(VARCHAR(db.id_length), ForeignKey('users.id'))
    name = Column(VARCHAR(200))
    create_date = Column(Date())
    deck_index = Column(Integer, default=0)
    root_deck_id = Column(VARCHAR(db.id_length))
    sanitized_name = Column(VARCHAR(200))

    @property
    def cards(self):
        all_cards = db.Session.query(MtgCardModel, XDeckCard.quantity)\
                              .join(XDeckCard)\
                              .filter(XDeckCard.deck_id == self.id)\
                              .all()
        return all_cards

    @property
    def user(self):
        from mtg_link.models.users import User
        return User.filter(User.id==self.user_id).one()

    @property
    def creatures(self):
        return self.get_cards_of_type('creature')

    @property
    def planeswalkers(self):
        return self.get_cards_of_type('planeswalker')

    @property
    def instants(self):
        return self.get_cards_of_type('instant')

    @property
    def sorceries(self):
        return self.get_cards_of_type('sorcery')

    @property
    def lands(self):
        return self.get_cards_of_type('land')

    @property
    def artifacts(self):
        return self.get_cards_of_type('artifact')

    @property
    def enchantments(self):
        return self.get_cards_of_type('enchantment')

    def get_cards_of_type(self, card_type):
        return db.Session.query(MtgCardModel, XDeckCard.quantity)\
                         .join(XCardType)\
                         .join(TypeModel)\
                         .join(XDeckCard)\
                         .join(Deck)\
                         .filter(Deck.id==self.id)\
                         .filter(TypeModel.name==card_type)\
                         .order_by(MtgCardModel.name.desc())\
                         .all()

class XDeckCard(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'x_decks_cards'

    deck_id = Column(VARCHAR(db.id_length), ForeignKey('decks.id'))
    card_id = Column(VARCHAR(db.id_length), ForeignKey('cards.id'))
    quantity = Column(Integer, default=1)
