
from alveare.common.database import DB

class Contractor(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    busyness = DB.Column(DB.Integer, nullable=False)

    def __init__(self, busyness):
        self.busyness = busyness

    def __repr__(self):
        return '<Contractor[id:{}] title="{}", busyness="{}">'.format(self.id, self.busyness)
