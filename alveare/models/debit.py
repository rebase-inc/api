
from alveare.common.database import DB

class Debit(DB.model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    def __init__(self, price):
        self.price = price

    def __repr__(self):
        return '<Debit for {} {}>'.format(self.price, 'dollars')
