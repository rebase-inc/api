
from alveare.common.database import DB, PermissionMixin
import alveare.models.manager
import alveare.models.contractor
import alveare.models.code_clearance

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

    def get_all_as_manager(user):
        return Project.query\
            .join(alveare.models.organization.Organization)\
            .join(alveare.models.manager.Manager)\
            .filter(alveare.models.manager.Manager.user == user)

    def get_cleared_projects(user):
        ''' Return all projects for which user has a clearance '''
        return Project.query\
            .join(alveare.models.code_clearance.CodeClearance)\
            .join(alveare.models.contractor.Contractor)\
            .filter(alveare.models.contractor.Contractor.user == user)

    def allowed_to_be_created_by(self, user):
        if user.is_admin():
            return True
        return alveare.models.organization.Organization.query\
            .filter(alveare.models.organization.Organization.id == self.organization.id)\
            .join(alveare.models.manager.Manager, alveare.models.manager.Manager.user == user)\
            .limit(100).all()

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        return Project.get_all_as_manager(user)\
            .filter(Project.id == self.id)\
            .union(Project.get_cleared_projects(user).filter(Project.id == self.id))\
            .limit(100).all()
