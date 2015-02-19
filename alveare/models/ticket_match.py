
from alveare.common.database import DB

class TicketMatch(DB.Model):
    __table_args__ = (DB.ForeignKeyConstraint(  ['contractor_id',               'auction_id'],
                                                ['talent_match.contractor_id',  'talent_match.auction_id']), {})

    skill_requirements_id = DB.Column(DB.Integer, DB.ForeignKey('skill_requirements.id', ondelete='CASCADE'), primary_key=True)
    skill_set_id =          DB.Column(DB.Integer, DB.ForeignKey('skill_set.id',          ondelete='CASCADE'), primary_key=True)
    contractor_id =         DB.Column(DB.Integer)
    auction_id =            DB.Column(DB.Integer)
    score =                 DB.Column(DB.Integer, nullable=False)

    skill_set =             DB.relationship('SkillSet',             backref='talent_matches', uselist=False)
    skill_requirements =    DB.relationship('SkillRequirements',    backref='talent_matches', uselist=False)

    def __init__(self, skill_set, skill_requirements, score):
        self.skill_set = skill_set
        self.skill_requirements = skill_requirements
        self.score = score

    def __repr__(self):
        return '<TicketMatch[Contractor({}), Ticket({})] score={}>'.format(self.id, self.score)

