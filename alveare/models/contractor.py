
from alveare.common.database import DB

class Contractor(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    busyness = DB.Column(DB.Integer, nullable=False, default=1)
    first_name = DB.Column(DB.String, nullable=False)
    last_name = DB.Column(DB.String, nullable=False)
    email = DB.Column(DB.String, nullable=False)

    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def __repr__(self):
        return '<Contractor[id:{}] title="{}", busyness="{}">'.format(self.id, self.busyness)
