
from alveare.common.database import DB, PermissionMixin

class SkillRequirement(DB.Model, PermissionMixin):
    __pluralname__ = 'skill_requirements'

    id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), primary_key=True)

    ticket_matches = DB.relationship('TicketMatch', backref='skill_requirement', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, ticket):
        self.ticket = ticket

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
        return '<SkillRequirement[{}]>'.format(self.id)

