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
        return cls.get_all(user)

    def filter_by_id(self, query):
        return query.filter(SkillRequirement.id==self.id)

    @classmethod
    def get_all(cls, user, skill_requirement=None):
        return query_by_user_or_id(
            cls,
            cls.as_manager,
            cls.filter_by_id,
            user, skill_requirement
        )

    @classmethod
    def as_manager(cls, user):
        import alveare.models
        return query_from_class_to_user(cls, [
            alveare.models.ticket.Ticket,
            alveare.models.project.Project,
            alveare.models.organization.Organization,
            alveare.models.manager.Manager,
        ], user)

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.get_all(user, self).limit(1).all()

    def __repr__(self):
        return '<SkillRequirement[{}]>'.format(self.id)
