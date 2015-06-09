from sqlalchemy.sql import false
from alveare.common.database import DB, PermissionMixin, query_by_user_or_id
from alveare.common.query import query_from_class_to_user

class SkillRequirement(DB.Model, PermissionMixin):
    __pluralname__ = 'skill_requirements'

    id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), primary_key=True)

    ticket_matches = DB.relationship('TicketMatch', backref='skill_requirement', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, ticket):
        self.ticket = ticket

    @classmethod
    def query_by_user(cls, user):
        return query_by_user_or_id(cls, cls.get_all, user)

    @classmethod
    def get_all(cls, user, id=None):
        return cls.as_manager(user, id)

    @classmethod
    def as_manager(cls, user, id=None):
        import alveare.models
        return query_from_class_to_user(SkillRequirement, [
            alveare.models.ticket.Ticket,
            alveare.models.project.Project,
            alveare.models.organization.Organization,
            alveare.models.manager.Manager,
        ], user, id)

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return self.as_manager(user, self.id).limit(1).all()

    def __repr__(self):
        return '<SkillRequirement[{}]>'.format(self.id)
