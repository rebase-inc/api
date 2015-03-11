from alveare.common.database import DB

class Bid(DB.Model):

    id =        DB.Column(DB.Integer, primary_key=True)

    # note these 2 together form a primary key, so bid_id is redundant
    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id', ondelete='CASCADE'),      nullable=False)
    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'),   nullable=False)

    work_offers =   DB.relationship('WorkOffer',
            backref=DB.backref('bid', cascade='all, delete-orphan', single_parent=True),
            lazy='dynamic')

    contract = DB.relationship('Contract', backref='bid', cascade='all, delete-orphan', uselist=False)

    def __init__(self, auction, contractor):
        from alveare.models import WorkOffer
        self.auction = auction
        self.contractor = contractor
        self.work_offers = WorkOffer.query.filter(WorkOffer.contractor == contractor,
            WorkOffer.ticket_snapshot_id.in_([bl.snapshot.id for bl in auction.ticket_set.bid_limits]))

    def __repr__(self):
        return '<Bid[auction({}), contractor({})]>'.format(self.auction_id, self.contractor_id)

