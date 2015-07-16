from mtg_link import db
db.drop_tables(drop_all=True)
from mtg_link.models.magic import *
db.initialize()
