if __name__ == "__main__":
    import sys
    print parse_deck(sys.stdin)

def parse_deck(text):
    import re
    import json
    total = 0
    cards = {'total': 0,
             'cards': {}}
    for line in text:
        p = re.compile(r'''(\d+)x?\s*([\w\s\d\-/,'"]+)''')
        g = p.match(line).groups()
        card_quantity = int(g[0])
        card_name = g[1]
        total += card_quantity
        cards['cards'].setdefault(card_name, 0)
        cards['cards'][card_name] += card_quantity
    cards['total'] = total
    return cards
