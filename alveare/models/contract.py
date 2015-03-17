
from alveare.common.database import DB

class Contract(DB.Model):
    __pluralname__ = 'contracts'

    id = DB.Column(DB.Integer, DB.ForeignKey('bid.id', ondelete='CASCADE'), primary_key=True)

    def __init__(self, bid):
        self.bid = bid

    def __repr__(self):
        return '<Contract[{}]>'.format(self.id)

