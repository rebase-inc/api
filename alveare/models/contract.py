
from alveare.common.database import DB

class Contract(DB.Model):

    id =        DB.Column(DB.Integer, primary_key=True)
    bid_id =    DB.Column(DB.Integer, DB.ForeignKey('bid.id', ondelete='CASCADE'), nullable=False)
    bid =       DB.relationship('Bid',  uselist=False)

    def __init__(self, bid):
        self.bid = bid

    def __repr__(self):
        return '<Contract[{}]>'.format(self.id)

