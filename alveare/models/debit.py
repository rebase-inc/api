
from alveare.common.database import DB

class Debit(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    price = DB.Column(DB.Integer, nullable=False)

    def __init__(self, price):
        self.price = price

    def __repr__(self):
        return '<Debit for {} {}>'.format(self.price, 'dollars')
