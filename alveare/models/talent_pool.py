
from alveare.common.database import DB

class TalentPool(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<TalentPool[id:{}]>'.format(self.id)

