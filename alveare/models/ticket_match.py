
from alveare.common.database import DB, PermissionMixin
from alveare.models.job_fit import JobFit

class TicketMatch(DB.Model, PermissionMixin):
    __pluralname__ = 'ticket_matches'

    skill_requirement_id =  DB.Column(DB.Integer, DB.ForeignKey('skill_requirement.id', ondelete='CASCADE'), primary_key=True)
    skill_set_id =          DB.Column(DB.Integer, DB.ForeignKey('skill_set.id',         ondelete='CASCADE'), primary_key=True)
    contractor_id = DB.Column(DB.Integer, nullable=True)
    ticket_set_id = DB.Column(DB.Integer, nullable=True)
    score =                 DB.Column(DB.Integer, nullable=False)

    __table_args__ = (
        DB.ForeignKeyConstraint(
            [contractor_id, ticket_set_id],
            [JobFit.contractor_id, JobFit.ticket_set_id],
            ondelete='SET NULL'
        ), {})

    def __init__(self, skill_set, skill_requirement, score):
        self.skill_set = skill_set
        self.skill_requirement = skill_requirement
        self.score = score

    @classmethod
    def query_by_user(cls, user):
        return cls.query

    def allowed_to_be_created_by(self, user):
        return True

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        return self.allowed_to_be_created_by(user)

    def __repr__(self):
        return '<TicketMatch[SkillSet({}), SkillRequirement({})] score={}>'.format(
            skill_set_id,
            skill_requirement_id,
            self.score
        )

