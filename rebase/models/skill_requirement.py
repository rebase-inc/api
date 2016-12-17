from rebase.common.database import DB, PermissionMixin

class SkillRequirement(DB.Model, PermissionMixin):
    __pluralname__ = 'skill_requirements'

    id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), primary_key=True)
    skills = DB.Column(DB.PickleType, nullable=True)

    ticket_matches = DB.relationship('TicketMatch', backref='skill_requirement', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, ticket, skills=None):
        self.ticket = ticket
        self.skills = skills or {}

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.Ticket,
            models.Project,
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.Ticket,
            models.Project,
            models.CodeClearance,
            models.Contractor,
        ]
        cls.as_manager_path = [
            models.Ticket,
            models.Project,
            models.Manager
        ]

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.ticket.allowed_to_be_viewed_by(user)

    def __repr__(self):
        return '<SkillRequirement[{}]>'.format(self.id)
