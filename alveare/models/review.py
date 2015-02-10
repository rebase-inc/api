
from alveare.common.database import DB

class Review(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    rating = DB.Column(DB.Integer, nullable=False)

    def __init__(self):
        pass

    def __repr__(self):
        return '<Review[id:{}] rating={}>'.format(self.id, self.rating)

