
from alveare.common.database import DB

class Feedback(DB.Model):

    id =        DB.Column(DB.Integer, primary_key=True)

    # note these 2 together form a primary key, so bid_id is redundant
    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'))
    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id', ondelete='CASCADE'))
    
    message =       DB.Column(DB.String, nullable=False)

    def __init__(self, auction, contractor, message):
        self.auction = auction
        self.contractor = contractor
        self.message = message

    def __repr__(self):
        return '<Feedback[auction({}), contractor({})] >'.format(self.auction_id, self.contractor_id)
