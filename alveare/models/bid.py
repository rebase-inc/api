
from alveare.common.database import DB

from .auction import Auction
from .contractor import Contractor
from .work_offer import WorkOffer

class Bid(DB.Model):

    id =        DB.Column(DB.Integer, primary_key=True)

    # note these 2 together form a primary key, so bid_id is redundant
    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id'))
    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id'))

    auction =       DB.relationship(Auction,    uselist=False)
    contractor =    DB.relationship(Contractor, uselist=False)
    work_offers =   DB.relationship('WorkOffer', backref='bid', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=False)

    def __init__(self, auction, contractor):
        self.auction = auction
        self.contractor = contractor

    def __repr__(self):
        return '<Bid[auction({}), contractor({})]>'.format(self.auction_id, self.contractor_id)

