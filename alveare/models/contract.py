
from alveare.common.database import DB

from alveare.models.term_sheet  import TermSheet
from alveare.models.auction     import Auction
from alveare.models.bid         import Bid
from alveare.models.contractor  import Contractor

class Contract(DB.Model):

    __table_args__ = (
        DB.ForeignKeyConstraint(
            ['auction_id', 'contractor_id'],
            ['bid.auction_id', 'bid.contractor_id']),
    )

    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id'),      primary_key=True, nullable=False)
    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id'),   primary_key=True, nullable=False)

    bid =           DB.relationship(Bid,        uselist=False)

    def __init__(self, bid):
        self.bid = bid

    def __repr__(self):
        return '<Contract[({},{},{})]>'.format(self.auction_id, self.contractor_id, self.term_sheet_id)

