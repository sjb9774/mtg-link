# this class is meant to simply ensure that derived classes will always have attributes
# some attributes defined, those attributes being enumerated in __fields__. Just avoids
# having to write self.var = None for classes that have a lot of attributes that may needs
# to be defined but not necessarily initialized
class SmartObject(object):

    __fields__ = []

    def __init__(self, **kwargs):
        for field in self.__fields__:
            setattr(self, field, kwargs.get(field, None))

    def __iter__(self):
        for field in self.__fields__:
            yield field, getattr(self, field)


class MtgCardSet(SmartObject):

    __fields__ = ['name', 'code', 'block', 'release_date', 'set_type']

    def __init__(self, **kwargs):
        super(MtgCardSet, self).__init__(**kwargs)


class MtgCard(SmartObject):

    __fields__ = ['name', 'colors', 'type', 'subtype', 'legendary', 'artist', 'set',
                  'promo', 'foil', 'power', 'toughness', 'mana_cost', 'loyalty',
                  'transform', 'half', 'rarity', 'multiverse_id', 'text', 'converted_mana_cost']

    def __init__(self, **kwargs):
        super(MtgCard, self).__init__(**kwargs)

    def __iter__(self):
        for field in self.__fields__:
            if field != 'set':
                yield field, getattr(self, field)
            else:
                yield field, getattr(self, field).code if getattr(self, field) else None

from mtg_link.mtg.colors import Color

class ManaSymbol:

    def __init__(self, colors=None, x=False, phyrexian=False, count=1):
        self.colors = []
        self._color_abbrs = []
        if colors:
            self.colorless = False
            for color in colors:
                c = Color(color)
                if c.abbreviation not in self._color_abbrs:
                    self.colors.append(c)
                    self._color_abbrs.append(c.abbreviation)
        else:
            self.colorless = True
            self._color_abbrs = ['N']

        if not self.colorless and count != 1:
            raise ValueError('Count must always be 1 for X and colored mana symbols')

        if colors and x:
            raise ValueError('X-cost mana-symbols aren\'t colored.')

        self.count = count
        self.x = x
        self.phyrexian = phyrexian

    def symbol(self):
        return '{' + '/'.join(sorted(self._color_abbrs)) + '}'

    def converted_mana_cost(self):
        if self.x:
            return 0
        else:
            return self.count

    def get_colors(self):
        return sorted(self.colors)

    def is_hybrid(self):
        return len(self.get_colors()) > 1

    def __call__(self):
        return self.symbol()

    def __repr__(self):
        return '<ManaSymbol instance "{symbol}" at {address}>'.format(symbol=self(),
                                                                      address=hex(id(self)))
