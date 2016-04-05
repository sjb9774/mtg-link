from sqlalchemy import Table, Column, VARCHAR, Integer, Boolean, ForeignKey, Enum, Date, Float
from sqlalchemy.orm import  relationship
from mtg_link import db
from mtg_link.mtg.magic import MtgCard, MtgCardSet, ManaSymbol, Type, Subtype
from mtg_link.mtg.colors import Color
from mtg_link.mtg import ALL_COLOR_COMBINATIONS, TYPES, SET_TYPES

class MtgCardModel( db.IdMixin, db.Base, db.DefaultMixin, MtgCard):
    __tablename__ = 'cards'

    __fields__ = MtgCard.__fields__ + ['raw_power', 'raw_toughness']

    multiverse_id = Column(Integer)
    name = Column(VARCHAR(200), nullable=False, index=True) # must create index for foreign keys that reference this
    set_id = Column(VARCHAR(db.id_length), ForeignKey('sets.id'))
    colors = Column(Enum(*['/'.join(c) for c in ALL_COLOR_COMBINATIONS]))

    power = Column(Float)
    toughness = Column(Float)
    raw_power = Column(VARCHAR(25))
    raw_toughness = Column(VARCHAR(25))
    loyalty = Column(Integer)
    foil = Column(Enum('foil', 'normal', 'special'))
    converted_mana_cost = Column(Integer)
    # can we use a foreign key or will the constraint always fail due to circular referencing?
    # ie Ludevic's Subject.transform_id = 'xxxx' = Ludevic's Abomination.transform_id
    transform_multiverse_id = Column(VARCHAR(db.id_length))
    rarity = Column(Enum("common", "uncommon", "rare", "special", "mythic rare", "other", "promo", "basic land"))
    text = Column(VARCHAR(1000))

    def __init__(self, **kwargs):
        power = kwargs.get('power')
        toughness = kwargs.get('toughness')
        for pt in ('power', 'toughness'):
            stat = kwargs.pop(pt, None)
            if type(stat) == str or type(stat) == unicode:
                value = None
                if stat.lower() in ('*', 'x'):
                    value = 0
                elif stat.isdigit():
                    value = int(stat)

                if pt == 'power':
                    power = value
                else:
                    toughness = value
        MtgCard.__init__(self, power=power, toughness=toughness, **kwargs)
        db.IdMixin.__init__(self)

    @property
    def converted_mana_cost(self):
        mana_costs = ManaCostModel.filter_by(card_id=self.id).all()
        cmc = 0
        for mc in mana_costs:
            cmc += mc.count * mc.mana_symbol.value
        return cmc

class MtgCardSetModel(db.Base, db.DefaultMixin, db.IdMixin, MtgCardSet):

    __tablename__ = 'sets'
    name = Column(VARCHAR(200))
    code = Column(VARCHAR(10))
    block = Column(VARCHAR(200))
    release_date = Column(Date)
    set_type = Column(Enum(*SET_TYPES))
    cards = relationship('MtgCardModel', backref='set')

    def __init__(self, **kwargs):
        MtgCardSet.__init__(self, **kwargs)
        db.IdMixin.__init__(self)


from sqlalchemy import event
class ManaSymbolModel(db.IdMixin, db.Base, db.DefaultMixin, ManaSymbol):

    __tablename__ = 'mana_symbols'

    r = Column(Boolean, default=False)
    u = Column(Boolean, default=False)
    b = Column(Boolean, default=False)
    g = Column(Boolean, default=False)
    w = Column(Boolean, default=False)
    colorless = Column(Boolean, default=False)
    x = Column(Boolean, default=False)
    value = Column(Float, default=1)

    label = Column(VARCHAR(10))

    phyrexian = Column(Boolean, default=False)

    def __init__(self, *args, **kwargs):
        db.IdMixin.__init__(self)
        ManaSymbol.__init__(self, **kwargs)


# a couple of functions to bridge the gap between the database representation and the basic representation
@event.listens_for(ManaSymbolModel, 'load')
def set_colors(target, context):
    colors = ('b', 'g', 'r', 'u', 'w', 'colorless')
    mana_symbol = target
    mana_symbol.colors = []
    for color in colors:
        if getattr(mana_symbol, color):
            mana_symbol.colors.append(Color(color))

@event.listens_for(ManaSymbolModel.r, 'set')
@event.listens_for(ManaSymbolModel.u, 'set')
@event.listens_for(ManaSymbolModel.b, 'set')
@event.listens_for(ManaSymbolModel.w, 'set')
@event.listens_for(ManaSymbolModel.g, 'set')
def refresh_colors(target, value, old_value, initiator):
    if value not in (True, False, None):
        raise ValueError('Colors can only be set to True, False, or None for a ManaSymbolModel')
    else:
        colors = ('b', 'g', 'r', 'u', 'w', 'colorless')
        mana_symbol = target

        mana_symbol.colors = [Color(abbr) for abbr in colors if getattr(mana_symbol, abbr) and abbr != initiator.key]
        if value:
            mana_symbol.colors.append(Color(initiator.key))


class ManaCostModel(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'mana_costs'

    card_id = Column(VARCHAR(db.id_length), ForeignKey('cards.id'))
    mana_symbol_id = Column(VARCHAR(db.id_length), ForeignKey('mana_symbols.id'))
    count = Column(Integer)
    mana_symbol = relationship('ManaSymbolModel')

class FormatModel(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'formats'

    name = Column(VARCHAR(200))

class RulingModel(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'rulings'

    date = Column(Date)
    ruling = Column(VARCHAR(5000))


class XCardRuling(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'x_card_rulings'

    card_name = Column(VARCHAR(200), ForeignKey('cards.name'), nullable=False)
    ruling_id = Column(VARCHAR(db.id_length), ForeignKey('rulings.id'), nullable=False)

class XCardFormat(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'x_card_formats'

    card_name = Column(VARCHAR(200), ForeignKey('cards.name'), nullable=False)
    format_id = Column(VARCHAR(db.id_length), ForeignKey('formats.id'), nullable=False)

class TypeModel(db.IdMixin, db.Base, db.DefaultMixin, Type):

    __tablename__ = 'types'

    name = Column(VARCHAR(200))


class SubtypeModel(db.IdMixin, db.Base, db.DefaultMixin, Subtype):

    __tablename__ = 'subtypes'

    name = Column(VARCHAR(200))


class XCardType(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'x_card_types'

    card_id = Column(VARCHAR(db.id_length), ForeignKey('cards.id'))
    type_id = Column(VARCHAR(db.id_length), ForeignKey('types.id'))
    priority = Column(Integer)


class XCardSubtype(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'x_card_subtypes'

    card_id = Column(VARCHAR(db.id_length), ForeignKey('cards.id'))
    subtype_id = Column(VARCHAR(db.id_length), ForeignKey('subtypes.id'))
    priority = Column(Integer)
