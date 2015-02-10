
from alveare.common.database import DB

class TalentMatch(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    score = DB.Column(DB.Integer, nullable=False)

    def __init__(self, score):
        self.score = score

    def __repr__(self):
        return '<TalentMatch[id:{}] score={}>'.format(self.id, self.score)

