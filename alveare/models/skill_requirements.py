
from alveare.common.database import DB

class SkillRequirements(DB.Model):

    id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), primary_key=True)

    def __init__(self, ticket):
        self.ticket = ticket

    def __repr__(self):
        return '<SkillRequirements[{}]>'.format(self.id)

