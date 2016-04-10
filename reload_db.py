from mtg_link import db
db.drop_tables(drop_all=True)
from mtg_link.models.magic import *
from mtg_link.models.users import *
from mtg_link.models.sessions import *
from mtg_link.models.decks import *
db.initialize()
