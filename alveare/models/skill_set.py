
from alveare.common.database import DB

class SkillSet(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<SkillSet[id:{}]>'.format(self.id)

