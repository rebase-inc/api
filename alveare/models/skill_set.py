
from alveare.common.database import DB

class SkillSet(DB.Model):

    id =  DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True)

    def __init__(self, contractor):
        self.contractor = contractor

    def __repr__(self):
        return '<SkillSet[{}]>'.format(self.id)

