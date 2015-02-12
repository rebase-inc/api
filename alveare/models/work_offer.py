
import alveare

from alveare.common.database import DB

class WorkOffer(DB.Model):
    id =      DB.Column(DB.Integer, primary_key=True)
    price =   DB.Column(DB.Integer, nullable=False)
    work_id = DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, price):
        self.price = price

    def __repr__(self):
        return '<WorkOffer for {} {}>'.format(self.price, 'dollars')
