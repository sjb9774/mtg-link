#!/usr/bin/env python
if __name__ == '__main__':
    import requests
    import os
    import sys
    from mtg_link.models.magic import MtgCardModel
    gatherer_url = 'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={multiverse_id}&type=card'
    cards = MtgCardModel.filter(MtgCardModel.multiverse_id != None).order_by(MtgCardModel.set_id).all()
    total_cards = len(cards)
    for num, card in enumerate(cards, start=1):
        if not os.path.exists(os.path.expanduser('~/Projects/mtg-link/DATA/images/{set}'.format(set=card.set.code))):
            os.makedirs(os.path.expanduser('~/Projects/mtg-link/DATA/images/{set}'.format(set=card.set.code)))
        card_path = os.path.expanduser('~/Projects/mtg-link/DATA/images/{set}/{name} - {mid}.png'.format(set=card.set.code,
                                                                                               name=card.name,
                                                                                               mid=card.multiverse_id))
        if os.path.exists(card_path):
            print '{card_path} for {card.name} ({card.multiverse_id}) already exists, skipping.'.format(**locals())
        else:
            while True:
                print 'Ripping card #{num} of {total_cards} ({card.name} - {card.multiverse_id} of {card.set.code})'.format(**locals())
                try:
                    r = requests.get(gatherer_url.format(multiverse_id=card.multiverse_id))
                    break
                except requests.exceptions.ConnectionError:
                    retry = input('Connection down! Enter "r" to retry or anything else to abort.')
                    if retry.lower() != 'r':
                        sys.exit(0)
            if r.status_code in (200, ):
                with open(card_path, 'w+') as f:
                    f.write(r.content)
            else:
                print 'Problem with request for card {card.multiverse_id} ({card.name}), status code {code}'.format(card=card, code=r.status_code)
