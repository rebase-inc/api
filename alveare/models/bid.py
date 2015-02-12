
from alveare.common.database import DB

from .work_offer import WorkOffer

class Bid(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    work_offers = DB.relationship('WorkOffer', backref='bid', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self):
        pass

    def __repr__(self):
        return '<Bid[id:{}]>'.format(self.id)

