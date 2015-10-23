from functools import partialmethod

from sqlalchemy.orm import aliased

from rebase.common.database import DB, PermissionMixin

class SkillSet(DB.Model, PermissionMixin):
    __pluralname__ = 'skill_sets'

    id =  DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True)
    skills =  DB.Column(DB.PickleType, nullable=True)

    ticket_matches = DB.relationship('TicketMatch', backref='skill_set', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, contractor, skills=None):
        self.contractor = contractor
        self.skills = skills or {}

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.Contractor,
            models.CodeClearance,
            models.Project,
            models.Organization,
            models.Owner,
        ]
        OtherContractorsCodeClearance = aliased(models.CodeClearance)
        cls.as_contractor_path = [
            models.Contractor,
            models.CodeClearance,
            models.Project,
            OtherContractorsCodeClearance,
            models.Contractor
        ]
        cls.as_manager_path = [
            models.Contractor,
            models.Nomination,
            models.TicketSet,
            models.BidLimit,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Manager
        ]

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.found(self, user)

    def __repr__(self):
        return '<SkillSet[{}]>'.format(self.id)
