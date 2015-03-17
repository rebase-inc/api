
from alveare.common.database import DB

class SkillRequirement(DB.Model):
    __pluralname__ = 'skill_requirements'

    id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), primary_key=True)

    ticket_matches = DB.relationship('TicketMatch', backref='skill_requirement', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, ticket):
        self.ticket = ticket

    def __repr__(self):
        return '<SkillRequirement[{}]>'.format(self.id)

