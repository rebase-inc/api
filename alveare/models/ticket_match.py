
from alveare.common.database import DB
from alveare.models.job_fit import JobFit

class TicketMatch(DB.Model):
    __pluralname__ = 'ticket_matches'
    __table_args__ = (DB.ForeignKeyConstraint(  ['contractor_id',           'auction_id'],
                                                [JobFit.contractor_id,   JobFit.auction_id], ondelete='SET NULL'), {})

    skill_requirement_id =  DB.Column(DB.Integer, DB.ForeignKey('skill_requirement.id', ondelete='CASCADE'), primary_key=True)
    skill_set_id =          DB.Column(DB.Integer, DB.ForeignKey('skill_set.id',         ondelete='CASCADE'), primary_key=True)
    contractor_id =         DB.Column(DB.Integer, nullable=True)
    auction_id =            DB.Column(DB.Integer, nullable=True)
    score =                 DB.Column(DB.Integer, nullable=False)

    skill_set =             DB.relationship('SkillSet',         backref='ticket_matches', uselist=False)
    skill_requirement =     DB.relationship('SkillRequirement', backref='ticket_matches', uselist=False)
    job_fit =               DB.relationship('JobFit',           backref='ticket_matches', uselist=False)

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

