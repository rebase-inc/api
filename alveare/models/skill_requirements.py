
from alveare.common.database import DB

class SkillRequirements(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<SkillRequirements[id:{}]>'.format(self.id)

