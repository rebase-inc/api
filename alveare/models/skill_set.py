
from alveare.common.database import DB

class SkillSet(DB.Model):

    id =  DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True, nullable=False)

    def __repr__(self):
        return '<SkillSet[id:{}]>'.format(self.id)

