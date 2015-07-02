from ConfigParser import ConfigParser

class Config(object):

    def __init__(self, path, auto_write):
        self._parser = ConfigParser()
        self._parser.readfp(open(path))
        self._path = path
        self._auto_write = auto_write

    def __getattr__(self, attr_name):
        if hasattr(self._parser, attr_name):
            return getattr(self._parser, attr_name)
        else:
            return ConfigSection(attr_name, self._parser, self._path, self.auto_write)

    def all(self):
        d = {}
        for section in self._parser.sections():
            d[section] = {}
            for name, value in self._parser.items(section):
                d[section][name] = value

        return d


class ConfigSection(object):

    def __init__(self, name, parser, path, auto_write=True):
        set_attr = super(ConfigSection, self).__setattr__
        set_attr('__parser', parser)
        set_attr('__name', name)
        set_attr('__path', path)
        set_attr('__auto_write', auto_write)

    def __getattr__(self, attr_name):
        get_attr = super(ConfigSection, self).__getattribute__
        p = get_attr('__parser')
        if attr_name in ('__name', '__parser', '__path', '__auto_write'):
            return get_attr(attr_name)
        elif p.has_option(get_attr('__name'), attr_name):
            return p.get(get_attr('__name'), attr_name)
        else:
            return None

    def __setattr__(self, attr_name, value):
        if attr_name in ('_ConfigSection__name', '_ConfigSection__parser'):
            super(ConfigSection, self).__setattr__(attr_name, value)
        else:
            get_attr = super(ConfigSection, self).__getattribute__
            p = get_attr('__parser')
            if not p.has_section(get_attr('__name')):
                p.add_section(get_attr('__name'))
            p.set(get_attr('__name'), attr_name, value)
            if get_attr('__auto_write'):
                p.write(open(get_attr('__path'), 'r+'))

config = Config('./conf.cfg')
