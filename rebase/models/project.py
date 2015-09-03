
from rebase.common.database import DB, PermissionMixin
from rebase.common.exceptions import NoRole, UnknownRole
import rebase.models.manager
import rebase.models.contractor
import rebase.models.code_clearance

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
        if user.admin:
            return cls.query
        return cls.get_all_as_manager(user).union(cls.get_cleared_projects(user))

    @classmethod
    def get_all_as_manager(cls, user):
        return cls.query\
            .join(rebase.models.organization.Organization)\
            .join(rebase.models.manager.Manager)\
            .filter(rebase.models.manager.Manager.user == user)

    @classmethod
    def get_cleared_projects(cls, user):
        ''' Return all projects for which user has a clearance '''
        return cls.query\
            .join(rebase.models.code_clearance.CodeClearance)\
            .join(rebase.models.contractor.Contractor)\
            .filter(rebase.models.contractor.Contractor.user == user)

    def allowed_to_be_created_by(self, user):
        if user.is_admin():
            return True
        return rebase.models.organization.Organization.query\
            .filter(rebase.models.organization.Organization.id == self.organization.id)\
            .join(rebase.models.manager.Manager)\
            .filter(rebase.models.manager.Manager.user == user)\
            .first()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        return Project.get_all_as_manager(user)\
            .union(Project.get_cleared_projects(user))\
            .filter(Project.id == self.id)\
            .first()
