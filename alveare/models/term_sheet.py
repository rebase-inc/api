
from alveare.common.database import DB

class TermSheet(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    legalese = DB.Column(DB.String, nullable=False)

    def __init__(self, legalese):
        self.legalese = legalese

    def __repr__(self):
        return '<TermSheet[id:{}]>'.format(self.id)

