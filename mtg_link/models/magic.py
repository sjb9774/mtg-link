from sqlalchemy import Column, VARCHAR, Integer, Boolean, ForeignKey, Enum, Date
from mtg_link import db
from mtg_link.mtg.magic import MtgCard, MtgCardSet, ManaSymbol
from mtg_link.mtg.colors import Color
from mtg_link.mtg import ALL_COLOR_COMBINATIONS, TYPES, SET_TYPES

class MtgCardModel( db.IdMixin, db.Base, db.DefaultMixin, MtgCard):
    __tablename__ = 'cards'

    __fields__ = MtgCard.__fields__ + []

    multiverse_id = Column(Integer)
    name = Column(VARCHAR(200))
    set_id = Column(VARCHAR(db.id_length), ForeignKey('sets.id'))
    colors = Column(Enum(*['/'.join(c) for c in ALL_COLOR_COMBINATIONS]))
    type1 = Column(Enum(*TYPES))
    type2 = Column(Enum(*TYPES))
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
    rarity = Column(Enum("common", "uncommon", "rare", "special", "mythic rare", "other", "promo", "basic land"))
    text = Column(VARCHAR(1000))

    def __init__(self, **kwargs):
        power = None
        toughness = None
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
    set_type = Column(Enum(*SET_TYPES))

    def __init__(self, **kwargs):
        MtgCardSet.__init__(self, **kwargs)
        db.IdMixin.__init__(self)

'''
class ManaCostModel(db.Base, db.DefaultMixin, db.IdMixin):

    __tablename__ = 'mana_costs'

    g_cost = Column(Integer, default=0)
    b_cost = Column(Integer, default=0)
    r_cost = Column(Integer, default=0)
    u_cost = Column(Integer, default=0)
    w_cost = Column(Integer, default=0)

    colorless_cost = Column(Integer, default=0)
    x = Column(Integer, default=0)
    converted_mana_cost = Column(Integer, default=0)

    # Not scalable, but currently all Phyrexian mana using cards have all colored mana
    # as phyrexian, so True here means all colored mana is Phyrexian
    phyrexian = Column(Boolean, default=False)

    # HYBRID MANA
    ## Black
    bg_cost = Column(Integer, default=0)
    br_cost = Column(Integer, default=0)
    bu_cost = Column(Integer, default=0)
    bw_cost = Column(Integer, default=0)

    ## Green
    gr_cost = Column(Integer, default=0)
    gu_cost = Column(Integer, default=0)
    gw_cost = Column(Integer, default=0)

    ## Red
    ru_cost = Column(Integer, default=0)
    rw_cost = Column(Integer, default=0)

    ## Blue
    uw_cost = Column(Integer, default=0)

    ## Hybrid white costs are completely covered in the other colors

    @classmethod
    def from_mana_symbols(cls, *args):
        mana_cost = cls()
        cmc = 0
        for mana_symbol in args:
            attr = None
            if mana_symbol.x:
                attr = 'x'
            elif mana_symbol.is_hybrid():
                prefix = ''.join([c.abbreviation for c in mana_symbol.get_colors()])
                attr = prefix + '_cost'
            elif not mana_symbol.colorless:
                color = mana_symbol.get_colors()[0]
                attr = color.abbreviation + '_cost'

            cmc += mana_symbol.count

            if attr:
                # if None or 0
                if not getattr(mana_cost, attr):
                    setattr(mana_cost, attr, 1)
                else:
                    # increment
                    setattr(mana_cost, attr, getattr(mana_cost, attr) + 1)

            if mana_symbol.phyrexian:
                mana_cost.phyrexian = True
        mana_cost.converted_mana_cost = cmc
        return mana_cost
'''

from sqlalchemy import event
class ManaSymbolModel(db.IdMixin, db.Base, db.DefaultMixin, ManaSymbol):

    __tablename__ = 'mana_symbols'

    r = Column(Boolean, default=False)
    u = Column(Boolean, default=False)
    b = Column(Boolean, default=False)
    g = Column(Boolean, default=False)
    w = Column(Boolean, default=False)
    x = Column(Boolean, default=False)
    value = Column(Integer, default=1)

    label = Column(VARCHAR(10))

    phyrexian = Column(Boolean, default=False)

    def __init__(self, *args, **kwargs):
        db.IdMixin.__init__(self)
        ManaSymbol.__init__(self, **kwargs)


# a couple of functions to bridge the gap between the database representation and the basic representation
@event.listens_for(ManaSymbolModel, 'load')
def set_colors(target, context):
    colors = ('b', 'g', 'r', 'u', 'w')
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
        colors = ('b', 'g', 'r', 'u', 'w')
        mana_symbol = target

        mana_symbol.colors = [Color(abbr) for abbr in colors if getattr(mana_symbol, abbr) and abbr != initiator.key]
        if value:
            mana_symbol.colors.append(Color(initiator.key))

class ManaCostModel(db.IdMixin, db.Base, db.DefaultMixin):

    __tablename__ = 'mana_costs'

    card_id = Column(VARCHAR(db.id_length), ForeignKey('cards.id'))
    mana_symbol_id = Column(VARCHAR(db.id_length), ForeignKey('mana_symbols.id'))
    count = Column(Integer)
