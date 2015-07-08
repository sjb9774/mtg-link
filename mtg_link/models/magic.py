from sqlalchemy import Column, VARCHAR, Integer, Boolean, ForeignKey, Enum, Date
from mtg_link import db
from mtg_link.mtg.magic import MtgCard, MtgCardSet
from mtg_link.mtg import ALL_COLOR_COMBINATIONS

class MtgCardModel( db.IdMixin, db.Base, db.DefaultMixin, MtgCard):
    __tablename__ = 'cards'

    multiverse_id = Column(Integer)
    name = Column(VARCHAR(200))
    set_id = Column(VARCHAR(db.id_length), ForeignKey('sets.id'))
    colors = Column(Enum(*['/'.join(c) for c in ALL_COLOR_COMBINATIONS]))
    type = Column(VARCHAR(100))
    subtype1 = Column(VARCHAR(100))
    subtype2 = Column(VARCHAR(100))
    power = Column(Integer)
    toughness = Column(Integer)
    loyalty = Column(Integer)
    foil = Column(Enum('foil', 'normal', 'special'))
    converted_mana_cost = Column(Integer)
    mana_cost_id = Column(VARCHAR(db.id_length), ForeignKey('mana_costs.id'))
    # can we use a foreign key or will the constraint always fail due to circular referencing?
    # ie Ludevic's Subject.transform_id = 'xxxx' = Ludevic's Abomination.transform_id
    transform_multiverse_id = Column(VARCHAR(db.id_length))
    rarity = Column(Enum("common", "uncommon", "rare", "special", "mythic", "other", "promo"))
    text = Column(VARCHAR(1000))

    def __init__(self, **kwargs):
        super(MtgCard, self).__init__(**kwargs)

    @classmethod
    def db_model_from_class(cls, mtg_card_instance):
        mtg_card_properties = dict(mtg_card_instance)
        subtypes = mtg_card_properties.pop('subtypes')
        if len(subtypes) > 2:
            # TODO: log this
            print "More than two subtypes on card {mtg_card_instance.multiverse_id}!".format(**locals())
        mtg_card_properties['subtype1'], mtg_card_properties['subtype2'] = subtypes
        return cls(**dict(mtg_card_properties))

class MtgCardSetModel(db.Base, db.DefaultMixin, db.IdMixin, MtgCardSet):

    __tablename__ = 'sets'
    name = Column(VARCHAR(200))
    code = Column(VARCHAR(10))
    block = Column(VARCHAR(200))
    release_date = Column(Date)
    set_type = Column(Enum('core', 'expansion', 'promo'))

    def __init__(self, **kwargs):
        super(MtgCardSet, self).__init__(**kwargs)

class ManaCostModel(db.Base, db.DefaultMixin, db.IdMixin):

    __tablename__ = 'mana_costs'

    green_cost = Column(Integer)
    black_cost = Column(Integer)
    red_cost = Column(Integer)
    blue_cost = Column(Integer)
    white_cost = Column(Integer)
    colorless_cost = Column(Integer)
    x = Column(Integer)
    converted_mana_cost = Column(Integer)
    phyrexian = Column(VARCHAR(200))
    hybrid = Column(VARCHAR(200))

# dynamically create the color columns
