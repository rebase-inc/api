
from alveare.common.database import DB

class Feedback(DB.Model):

    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True)
    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id', ondelete='CASCADE'), primary_key=True)

    contractor = DB.relationship('Contractor', uselist=False, backref=DB.backref('feedbacks', cascade='all, delete-orphan', passive_deletes=True))

    def __init__(self, auction, contractor):
        self.auction = auction
        self.contractor = contractor

    def __repr__(self):
        return '<Feedback[auction({}), contractor({})] >'.format(self.auction_id, self.contractor_id)
