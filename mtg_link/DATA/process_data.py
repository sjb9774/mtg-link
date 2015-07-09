from mtg_link.mtg.magic import MtgCardSet, MtgCard, ManaSymbol
from mtg_link.mtg.colors import Color
from mtg_link.mtg import TYPES, ALL_COLOR_COMBINATIONS
from mtg_link.models.magic import MtgCardSetModel, MtgCardModel, ManaCostModel, ManaSymbolModel
from mtg_link.DATA import get_card_data
from mtg_link import db
import re

def do_data_process():
    CARD_DATA = get_card_data()
    mtg = {}
    mana_symbols = ManaSymbolModel.all()
    if not mana_symbols:
        prep_mana_symbols()
        mana_symbols = ManaSymbolModel.all()
    mana_symbol_dict = {}
    card_set_prop_map = {
        'releaseDate': 'release_date',
        'type': 'set_type'
    }

    card_prop_map = {
        'cmc': 'converted_mana_cost',
        'manaCost': 'mana_cost',
        'multiverseid': 'multiverse_id',
        'subtypes': 'subtype',
        'types': 'type',
        'names': 'transform'
    }
    transform_map = {}
    mana_cost_regx_str = r'\s*\{([\w\d/])\}\s*'
    mana_cost_regx = re.compile(mana_cost_regx_str)
    for set_code, set_data in CARD_DATA:
        mtg[set_code] = {'set': None, 'cards': []}
        mtg[set_code]['set'] = make_instance(MtgCardSetModel, card_set_prop_map, **set_data)
        for card_dict in set_data['cards']:
            if 'manaCost' not in card_dict:
                # defaults all costs to zero
                cost = ManaCostModel()
            else:
                mana_cost = card_dict.pop('manaCost')
                mana_symbols = []
                for token in mana_cost_regx.findall(mana_cost):
                    if token.isdigit():
                        symbol = ManaSymbol(count=int(token))
                    elif token.lower() in ('x', 'y', 'z'): # Ultimate Nightmare of Wizard's of the Coast Customer Service :\
                        symbol = ManaSymbol(x=True)
                    else:
                        colors = token.split('/')
                        symbol = ManaSymbol(colors=colors)
                    mana_symbols.append(symbol)
                    cost = ManaCostModel.from_mana_symbols(*mana_symbols)
                    card_dict['mana_cost_id'] = cost.id

            if not card_dict.get('colors'):
                colors = None
            else:
                colors = [Color(c) for c in card_dict.pop('colors')]
                colors = sorted([c.abbreviation for c in colors])
                colors = '/'.join(colors)

            for type_type in ('types', 'subtypes'):
                if card_dict.get(type_type):
                    lowercase_types = [t.lower() for t in card_dict.pop(type_type)]
                    if len(lowercase_types) == 1:
                        lowercase_types.append(None)
                    main_types = lowercase_types[:2]
                    other_types = lowercase_types[2:]
                    for i in (1, 0):
                        if main_types[i] not in TYPES:
                            other_types.insert(i, lowercase_types[i])
                            main_types[i] = None

                    card_dict[type_type[:-1] + '1'], card_dict[type_type[:-1] + '2'] = lowercase_types[:2]
                    card_dict['other_' + type_type] = str(other_types)

            card = make_instance(MtgCardModel,
                                 card_prop_map,
                                 mana_cost=cost,
                                 colors=colors,
                                 set_id=mtg[set_code]['set'].id,
                                 **card_dict)

            # it's a transform card
            if card_dict.get('layout') == 'double-faced':
                # if the other side of this card has been found already, there will be
                # an entry in transform map mapping this card's name to the model of the other side
                transform = transform_map.get(card.name)
                if transform:
                    card.transform_multiverse_id = transform.multiverse_id
                # if the other side has not been found, make an entry in transform_map, the cards
                # will be linked once the other card is found
                else:
                    transform_name = [name for name in card_dict['names'] if name != card_dict['name']][0]
                    transform_map[transform_name] = card
            mtg[set_code]['cards'].append(card)

    return mtg

def make_instance(cls, property_map, **kwargs):
    new_dict = {}
    instance = cls()
    for kw, arg in kwargs.iteritems():
        # if the name is mapped to something new in the property_map
        # and the mapped name is a valid attribute in MtgCardSet
        if property_map.get(kw) and hasattr(instance, property_map[kw]):
            new_dict[property_map[kw]] = arg
        # if the kwarg passed is an attribute of cls but not in the property_map,
        # go ahead and set it, so we don't have to specify map instances where the
        # property name doesn't change (eg, no "name": "name", "code": "code"...)
        elif hasattr(instance, kw):
            new_dict[kw] = arg
    return cls(**new_dict)

def mysql_dump(data):
    """
    data = {
        ...
        "THS": {
            "set": <MtgCardSetModel at 0x000000>,
            "cards": [<MtgCardModel at 0x000001>, <MtgCardModel at 0x000002>, ...]
        },
        "BNG": ...
    }
    """
    for set_code, info_dict in data.iteritems():
        set = info_dict['set'].insert()
        for card in info_dict['cards']:
            card.mana_cost.insert()
            card.set = set.id
            card.insert()
    # db.Session.commit()

def prep_mana_symbols():
    for cc in [comb for comb in ALL_COLOR_COMBINATIONS if len(comb) <= 2]:
        for b in (True, False):
            ms = ManaSymbolModel()
            ms.phyrexian = b
            for c in cc:
                setattr(ms, c, True)
            ms.insert(commit=False)

    colorless = ManaSymbolModel()
    colorless.insert(commit=False)

    for label in ('x', 'y', 'z'):
        x_cost = ManaSymbolModel()
        x_cost.x = True
        x_cost.value = 0
        x_cost.label = label
        x_cost.insert(commit=False)
    db.Session.commit()

if __name__ == "__main__":
    mtg_data = do_data_process()
    prep_mana_symbols()
    mysql_dump(mtg_data)
