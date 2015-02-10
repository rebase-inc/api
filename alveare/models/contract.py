
from alveare.common.database import DB

class Contract(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __init__(self):
        pass

    def __repr__(self):
        return '<Contract[id:{}]>'.format(self.id)

