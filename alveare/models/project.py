
from alveare.common.database import DB, PermissionMixin

class Project(DB.Model, PermissionMixin):
    __pluralname__ = 'projects'

    id =                DB.Column(DB.Integer, primary_key=True)
    name =              DB.Column(DB.String, nullable=False)
    organization_id =   DB.Column(DB.Integer, DB.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)
    type =              DB.Column(DB.String)

    code_repository =   DB.relationship('CodeRepository',   backref='project', cascade="all, delete-orphan", passive_deletes=True, uselist=False)
    tickets =           DB.relationship('Ticket',           backref='project', cascade="all, delete-orphan", passive_deletes=True)
    clearances =        DB.relationship('CodeClearance',    backref='project', cascade="all, delete-orphan", passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'project',
        'polymorphic_on': type
    }

    def __init__(self, organization, name):
        self.organization = organization
        self.name = name

    def __repr__(self):
        return '<Project[{}] "{}" for "{}" >'.format(self.id, self.name, self.organization)

    @classmethod
    def query_by_user(cls, user):
        return cls.query

    def allowed_to_be_created_by(self, user):
        from alveare.models import Manager
        if user.is_admin():
            return True
        organizations = user.manager_for_organizations
        return self.organization_id in organizations

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        return bool(self.organization.id in user.manager_for_organizations)
