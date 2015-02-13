
from alveare.common.database import DB

from alveare.models.auction import Auction
from alveare.models.contractor import Contractor
from .work_offer import WorkOffer

class Bid(DB.Model):

    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id'),      primary_key=True)
    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id'),   primary_key=True)

    auction =       DB.relationship(Auction,    uselist=False)
    contractor =    DB.relationship(Contractor, uselist=False)
    work_offers =   DB.relationship('WorkOffer', backref='bid', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, auction, contractor):
        self.auction = auction
        self.contractor = contractor

    def __repr__(self):
        return '<Bid[auction({}), contractor({})]>'.format(self.auction_id, self.contractor_id)

