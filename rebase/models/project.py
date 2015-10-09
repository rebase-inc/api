
from rebase.common.database import DB, PermissionMixin
from rebase.common.exceptions import NoRole, UnknownRole

class Project(DB.Model, PermissionMixin):
    __pluralname__ = 'projects'

    id =                DB.Column(DB.Integer, primary_key=True)
    name =              DB.Column(DB.String, nullable=False)
    organization_id =   DB.Column(DB.Integer, DB.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)
    type =              DB.Column(DB.String)

    code_repository =   DB.relationship('CodeRepository',   backref='project', cascade="all, delete-orphan", passive_deletes=True, uselist=False)
    tickets =           DB.relationship('Ticket',           backref='project', cascade="all, delete-orphan", passive_deletes=True)
    clearances =        DB.relationship('CodeClearance',    backref='project', cascade="all, delete-orphan", passive_deletes=True)
    managers =          DB.relationship('Manager',          backref='project', cascade='all, delete-orphan', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'project',
        'polymorphic_on': type
    }

    def __init__(self, organization, name):
        from rebase.models.manager import Manager
        self.name = name
        self.organization = organization
        for owner in organization.owners:
            Manager(owner.user, self)

    def __repr__(self):
        return '<Project[{}] "{}" for "{}" >'.format(self.id, self.name, self.organization)

    def allowed_to_be_created_by(self, user):
        if user.is_admin():
            return True
        return Project.as_owner(user).one()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        return Project.query_by_user(user).limit(1).first()

    @classmethod
    def setup_queries(cls, models):
        cls.filter_based_on_current_role = False

        cls.as_owner_path = [
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.CodeClearance,
            models.Contractor,
        ]

        cls.as_manager_path = [
            models.Manager
        ]
