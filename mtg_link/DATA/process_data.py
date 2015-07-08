def do_data_process():
    from mtg_link.mtg.magic import MtgCardSet, MtgCard
    from mtg_link.mtg.colors import Color
    from mtg_link.models.magic import MtgCardSetModel, MtgCardModel
    from mtg_link.DATA import get_card_data
    CARD_DATA = get_card_data()
    mtg = {}

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

    for set_code, set_data in CARD_DATA:
        mtg[set_code] = {'set': None, 'cards': []}
        mtg[set_code]['set'] = make_instance(MtgCardSetModel, card_set_prop_map, **set_data)
        for card_dict in set_data['cards']:
            for color in card_dict.pop('colors'):

            card = make_instance(MtgCardModel, card_prop_map, set=mtg[set_code]['set'], **card_dict)
            mtg[set_code]['cards'].append(card)

    for set_code, info_dict in mtg.iteritems():
        set = info_dict['set'].insert()
        for card in info_dict['cards']:
            card.set = set.id
            card.insert()

    return mtg

def make_instance(cls, property_map, **kwargs):
    instance = cls()
    if property_map.get('cmc'):
        pass
    for kw, arg in kwargs.iteritems():
        # if the name is mapped to something new in the property_map
        # and the mapped name is a valid attribute in MtgCardSet
        if property_map.get(kw) and hasattr(instance, property_map[kw]):
            setattr(instance, property_map[kw], arg)
        # if the kwarg passed is an attribute of MtgCardSet but not in the property_map,
        # go ahead and set it, so we don't have to specify map instances where the
        # property name doesn't change (eg, no "name": "name", "code": "code"...)
        elif hasattr(instance, kw):
            setattr(instance, kw, arg)
    return instance

def do_db_dump(data):
    from mtg_link import db

def do_redis_dump(data):
    import redis
    rdb = redis.StrictRedis()
    import pudb; pudb.set_trace()
    for set_code in data:
        rdb.hmset(set_code, dict(data[set_code]['set']))
        for card_obj in data[set_code]['cards']:
            rdb.hmset(card_obj.multiverse_id, dict(card_obj))
