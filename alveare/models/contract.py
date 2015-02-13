
from alveare.common.database import DB

from alveare.models.term_sheet  import TermSheet
from alveare.models.auction     import Auction
from alveare.models.bid         import Bid
from alveare.models.contractor  import Contractor

class Contract(DB.Model):

    id =   DB.Column(DB.Integer, primary_key=True)
    bid_id =        DB.Column(DB.Integer, DB.ForeignKey('bid.id'), nullable=False)

    bid =           DB.relationship(Bid,  uselist=False)

    def __init__(self, bid):
        self.bid = bid

    def __repr__(self):
        return '<Contract[{}]>'.format(self.id)

