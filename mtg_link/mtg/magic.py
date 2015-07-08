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

    __fields__ = ['name', 'color', 'type', 'subtype', 'legendary', 'artist', 'set',
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
