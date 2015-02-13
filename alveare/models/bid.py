
from alveare.common.database import DB

from alveare.models.auction import Auction
from alveare.models.contractor import Contractor

class Bid(DB.Model):

    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id'),      primary_key=True)
    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id'),   primary_key=True)

    auction =       DB.relationship(Auction,    uselist=False)
    contractor =    DB.relationship(Contractor, uselist=False)

    def __init__(self, auction, contractor):
        self.auction = auction
        self.contractor = contractor

    def __repr__(self):
        return '<Bid[auction({}), contractor({})]>'.format(self.auction_id, self.contractor_id)

