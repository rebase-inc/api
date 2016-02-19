from sqlalchemy import and_

from rebase.common.database import DB, PermissionMixin
from rebase.common.query import query_by_user_or_id, query_from_class_to_user
from rebase.models.job_fit import JobFit

class TicketMatch(DB.Model, PermissionMixin):
    __pluralname__ = 'ticket_matches'

    skill_requirement_id =  DB.Column(DB.Integer, DB.ForeignKey('skill_requirement.id', ondelete='CASCADE'), primary_key=True)
    skill_set_id =          DB.Column(DB.Integer, DB.ForeignKey('skill_set.id',         ondelete='CASCADE'), primary_key=True)
    contractor_id =         DB.Column(DB.Integer, nullable=True)
    ticket_set_id =         DB.Column(DB.Integer, nullable=True)
    score =                 DB.Column(DB.Integer, nullable=False)

    __table_args__ = (
        DB.ForeignKeyConstraint(
            [contractor_id, ticket_set_id],
            [JobFit.contractor_id, JobFit.ticket_set_id],
            ondelete='SET NULL'
        ), {})

    def __init__(self, skill_set, skill_requirement, score=-1):
        self.skill_requirement = skill_requirement
        self.skill_set = skill_set
        self.score = score

    @classmethod
    def query_by_user(cls, user):
        return cls.get_all(user)

    def filter_by_id(self, query):
        return query.filter(
            and_(
                TicketMatch.skill_set_id==self.skill_set_id,
                TicketMatch.skill_requirement_id==self.skill_requirement_id
            )
        )

    @classmethod
    def get_all(cls, user, instance=None):
        return query_by_user_or_id(cls, cls.as_manager, TicketMatch.filter_by_id, user, instance)

    @classmethod
    def as_manager(cls, user):
        import rebase.models
        return query_from_class_to_user(TicketMatch, [
            rebase.models.skill_requirement.SkillRequirement,
            rebase.models.ticket.Ticket,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.get_all(user, self).limit(1).all()

    def __repr__(self):
        return '<TicketMatch[SkillSet({}), SkillRequirement({})] score={}>'.format(
            self.skill_set_id,
            self.skill_requirement_id,
            self.score
        )

