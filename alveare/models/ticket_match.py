
from alveare.common.database import DB
from alveare.models.job_fit import JobFit

class TicketMatch(DB.Model):
    __table_args__ = (DB.ForeignKeyConstraint(  ['contractor_id',           'auction_id'],
                                                [JobFit.contractor_id,   JobFit.auction_id]), {})

    skill_requirements_id = DB.Column(DB.Integer, DB.ForeignKey('skill_requirements.id', ondelete='CASCADE'), primary_key=True)
    skill_set_id =          DB.Column(DB.Integer, DB.ForeignKey('skill_set.id',          ondelete='CASCADE'), primary_key=True)
    contractor_id =         DB.Column(DB.Integer, nullable=True)
    auction_id =            DB.Column(DB.Integer, nullable=True)
    score =                 DB.Column(DB.Integer, nullable=False)

    skill_set =             DB.relationship('SkillSet',             backref='ticket_matches', uselist=False)
    skill_requirements =    DB.relationship('SkillRequirements',    backref='ticket_matches', uselist=False)
    job_fit =               DB.relationship('JobFit', uselist=False)

    def __init__(self, skill_set, skill_requirements, score):
        self.skill_set = skill_set
        self.skill_requirements = skill_requirements
        self.score = score

    def __repr__(self):
        return '<TicketMatch[SkillSet({}), SkillRequirement({})] score={}>'.format(
            skill_set_id,
            skill_requirements_id,
            self.score
        )

