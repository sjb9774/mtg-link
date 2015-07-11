from mtg_link.mtg.magic import MtgCardSet, MtgCard, ManaSymbol
from mtg_link.mtg.colors import Color
from mtg_link.mtg import TYPES, ALL_COLOR_COMBINATIONS, COLORS
from mtg_link.models.magic import MtgCardSetModel, MtgCardModel, ManaCostModel, ManaSymbolModel
from mtg_link.DATA import get_card_data
from mtg_link import db
import time
import re

def do_data_process():
    stime = time.time()
    print "Beginning card process..."
    CARD_DATA = get_card_data()
    mtg = {}
    mana_costs = []
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
    mana_cost_regx_str = r'\s*\{([\w\d/]+)\}\s*'
    mana_cost_regx = re.compile(mana_cost_regx_str)
    set_time = time.time()
    for set_code, set_data in CARD_DATA:
        print 'Processing set {set_code}...'.format(set_code=set_code)
        mtg[set_code] = {'set': None, 'cards': []}
        mtg[set_code]['set'] = make_instance(MtgCardSetModel, card_set_prop_map, **set_data)
        for card_dict in set_data['cards']:
            cost = {}
            if 'manaCost' not in card_dict:
                # defaults all costs to zero
                if card_dict.get('manaCost'):
                    print 'What the fuck'
                mana_cost = ManaCostModel()
                symbol = mana_symbol_dict.setdefault('colorless', ManaSymbolModel.filter_by(x=False, phyrexian=False, **{k:False for k in COLORS}).first())
                mana_cost.count = 0
                mana_symbol_id = symbol.id
            else:
                raw_mana_cost = card_dict.pop('manaCost')
                # token = {4} or {g/w} or {r} etc...

                for mana_piece in mana_cost_regx.findall(raw_mana_cost):
                    token_parts = mana_piece.split('/')
                    for token in token_parts:
                        if token.isdigit():
                            symbol = mana_symbol_dict.setdefault('colorless', ManaSymbolModel.filter_by(x=False, phyrexian=False, **{k:False for k in COLORS}).first())
                            current = cost.setdefault(symbol, 0)
                            cost[symbol] = current + int(token)
                        elif token.lower() in ('x', 'y', 'z'): # Ultimate Nightmare of Wizard's of the Coast Customer Service :\
                            symbol = mana_symbol_dict.setdefault(ManaSymbol(x=True, label=token.lower()).symbol(),
                                                                 ManaSymbolModel.filter_by(x=True, label=token.lower()).first())
                            current = cost.setdefault(symbol, 0)
                            cost[symbol] += 1
                        else:
                            if len(token) > 1:
                                import pudb; pudb.set_trace()
                            colors = token.split('/')
                            is_phy = ('P' in colors) or ('p' in colors)
                            colors = [c.lower() for c in colors if c.lower() != 'p']
                            if is_phy:
                                print '{name} ({mid}) is phyrexian!'.format(name=card_dict['name'], mid=card_dict.get('multiverse_id'))
                            symbol = mana_symbol_dict.setdefault(ManaSymbol(colors=colors, phyrexian=is_phy).symbol(),
                                                                 ManaSymbolModel.filter_by(phyrexian=is_phy, **{c.lower(): (True if c in colors else False) for c in COLORS}).first())
                            current = cost.setdefault(symbol, 0)
                            cost[symbol] += 1

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
                                 colors=colors,
                                 set_id=mtg[set_code]['set'].id,
                                 **card_dict)

            for symbol, count in cost.iteritems():
                mana_cost = ManaCostModel()
                mana_cost.count = count
                mana_cost.mana_symbol_id = symbol.id
                mana_cost.card_id = card.id
                mana_costs.append(mana_cost)

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
        print 'Set completed, took {duration} seconds.'.format(duration=time.time()-set_time)
        set_time = time.time()
    print 'Processing done, total time {total_time} seconds.'.format(total_time=time.time()-stime)
    return mtg, mana_costs

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
    commit_interval = 100
    cards, costs = data
    num_sets = len(cards.keys())
    j = 0
    for set_code, info_dict in cards.iteritems():
        print "Set #{current} of {total}...".format(current=j, total=num_sets)
        set = info_dict['set'].insert()
        num_cards = len(info_dict['cards'])
        j += 1
        for i, card in enumerate(info_dict['cards']):
            card.set_id = set.id
            card.insert(commit=False)
            if i != 0 and i % commit_interval == 0:
                print "\tCard {current} committed of {total}".format(current=i, total=num_cards)
                db.Session.commit()

    total_costs = len(costs)
    for i, cost in enumerate(costs):
        cost.insert(commit=False)
        if i != 0 and i % commit_interval == 0:
            print "{costs}/{total} mana costs committed.".format(costs=i, total=total_costs)
            db.Session.commit()

def prep_mana_symbols():
    if ManaSymbolModel.all():
        return
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

def gen_print(g, start_msg='Starting...', done_msg='Done!'):
    print start_msg
    problem_size = g.next()
    problem_progress = g.next()
    while problem_progress < problem_size:
        print '\r{prog}/{total}'.format(prog=problem_progress, total=problem_size),
        problem_progress = g.next()
    print done_msg

if __name__ == "__main__":
    try:
        prep_mana_symbols()
        mtg_data = do_data_process()
        mysql_dump(mtg_data)
    except KeyboardInterrupt:
        print 'Rolling back before exit!'
        db.Session.rollback()
        raise
