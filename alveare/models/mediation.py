
from alveare.common.database import DB

class Mediation(DB.Model):
    id =            DB.Column(DB.Integer, primary_key=True)
    dev_answer =    DB.Column(DB.Integer, nullable=False)
    client_answer = DB.Column(DB.Integer, nullable=False)
    outcome =       DB.Column(DB.Integer, nullable=False)
    timeout =       DB.Column(DB.DateTime, nullable=False)

    def __init__(self, timeout):
        self.timeout = timeout

    def __repr__(self):
        return '<Mediation[id:{}] >'.format(self.id)

