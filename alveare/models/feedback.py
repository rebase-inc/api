
from alveare.common.database import DB

class Feedback(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __init__(self, busyness):
        pass

    def __repr__(self):
        return '<Feedback[id:{}] >'.format(self.id)
