
from alveare.common.database import DB
from alveare.models.job_fit import JobFit

class TicketMatch(DB.Model):
    __pluralname__ = 'ticket_matches'
    __table_args__ = (DB.ForeignKeyConstraint(  ['contractor_id',           'ticket_set_id'],
                                                [JobFit.contractor_id,   JobFit.ticket_set_id], ondelete='SET NULL'), {})

    skill_requirement_id =  DB.Column(DB.Integer, DB.ForeignKey('skill_requirement.id', ondelete='CASCADE'), primary_key=True)
    skill_set_id =          DB.Column(DB.Integer, DB.ForeignKey('skill_set.id',         ondelete='CASCADE'), primary_key=True)
    contractor_id =         DB.Column(DB.Integer, nullable=True)
    ticket_set_id =         DB.Column(DB.Integer, nullable=True)
    score =                 DB.Column(DB.Integer, nullable=False)

    def __init__(self, skill_set, skill_requirement, score):
        self.skill_set = skill_set
        self.skill_requirement = skill_requirement
        self.score = score

    def __repr__(self):
        return '<TicketMatch[SkillSet({}), SkillRequirement({})] score={}>'.format(
            skill_set_id,
            skill_requirement_id,
            self.score
        )

