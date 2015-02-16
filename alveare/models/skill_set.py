
from alveare.common.database import DB

class SkillSet(DB.Model):

    contractor_id =  DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return '<SkillSet[{}]>'.format(self.contractor_id)

