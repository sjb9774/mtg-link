from mtg_link import db
from mtg_link.models.magic import MtgCardModel, MtgCardSetModel
from mtg_link.models.decks import Deck, XDeckCard
from datetime import datetime
import re

def parse_card(string):
    ''' Parses a string in the form "2x Merfolk Looter (M10)" and returns a
    tuple with the card model instance and the quantity of that card'''

    string = string.strip()
    if not string[0].isdigit():
        raise ValueError('String not formatted correctly')

    regex_str = r'(\d+)x?\s+([^(]+)\s*(?:\(([^)]+)\))?'
    rgx = re.compile(regex_str)
    quant, name, set_code = rgx.match(string).groups()
    quant = int(quant)
    name = name.strip()
    if set_code:
        set_code = set_code.strip()

    card_query = db.Session.query(MtgCardModel).join(MtgCardSetModel).filter(MtgCardModel.name == name)
    if set_code:
        card_query = card_query.filter(MtgCardSetModel.code == set_code)
    else:
        card_query = card_query.order_by(MtgCardSetModel.release_date.desc())

    card = card_query.first()
    if not card:
        if set_code:
            raise StandardError("No cards matched '{card}' from set '{set_code}'".format(card=name, set_code=set_code))
        else:
            raise StandardError("No cards matched '{card}'.".format(card=name))

    return card, quant

def create_deck(deck_list, root_deck_id=None):
    deck = Deck()
    deck.root_deck_id = root_deck_id
    deck.create_date = datetime.now()
    if root_deck_id:
        last_index = Deck.filter_by(root_deck_id=root_deck_id).order_by(Deck.deck_index.desc()).all()
        deck.deck_index = last_index + 1

    xcards = []
    for card_string in deck_list:
        card, quant = parse_card(card_string)
        xcard = XDeckCard()
        xcard.quantity = quant
        xcard.card_id = card.id
        xcard.deck_id = deck.id
        xcards.append(xcard)

    return deck, xcards
