# -*- coding: utf8 -*-
import json
import os
import mtg_link

def _get_raw_card_data(*sets):
    with open(os.path.abspath(os.path.dirname(mtg_link.__file__)) + '/DATA/all_sets.json', 'r') as cards_file:
        # it's a single-line JSON file
        CARD_DATA = json.loads(unicode(cards_file.readline().replace('−', '-').replace('∞', 'infinity'), 'utf8').encode('utf-8'))
    import pudb; pudb.set_trace()
    if sets:
        return {kw: arg for kw, arg in CARD_DATA.iteritems() if kw in sets}
    else:
        return CARD_DATA

def get_card_data(*sets):
    data = _get_raw_card_data(*sets)
    for set_code in data:
        card_generator = (card_dict for card_dict in data[set_code].pop('cards'))
        data[set_code]['cards'] = card_generator
        yield set_code, data[set_code]
