
from alveare.common.database import DB

class Arbitration(DB.Model):
    id =            DB.Column(DB.Integer, primary_key=True)
    outcome =       DB.Column(DB.Integer, nullable=False)

    def __init__(self):
        pass

    def __repr__(self):
        return '<Arbitration[id:{}] >'.format(self.id)

