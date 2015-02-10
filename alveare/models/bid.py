
from alveare.common.database import DB

class Bid(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<Bid[id:{}]>'.format(self.id)

