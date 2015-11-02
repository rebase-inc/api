
from rebase.common.database import DB, PermissionMixin
from rebase.common.exceptions import NoRole, UnknownRole

class Project(DB.Model, PermissionMixin):
    __pluralname__ = 'projects'

    id =                DB.Column(DB.Integer, primary_key=True)
    name =              DB.Column(DB.String, nullable=False)
    organization_id =   DB.Column(DB.Integer, DB.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)
    type =              DB.Column(DB.String)
    deploy =            DB.Column(DB.String)
    test =              DB.Column(DB.String)
    readme =            DB.Column(DB.String)

    work_repo =         DB.relationship('WorkRepo',         backref='project', cascade="all, delete-orphan", passive_deletes=False, uselist=False)
    tickets =           DB.relationship('Ticket',           backref='project', cascade="all, delete-orphan", passive_deletes=True)
    clearances =        DB.relationship('CodeClearance',    backref='project', cascade="all, delete-orphan", passive_deletes=True)
    managers =          DB.relationship('Manager',          backref='project', cascade='all, delete-orphan', passive_deletes=False)

    __mapper_args__ = {
        'polymorphic_identity': 'project',
        'polymorphic_on': type
    }

    def __init__(self, organization, name):
        from rebase.models import Manager, WorkRepo
        self.name = name
        self.organization = organization
        self.work_repo = WorkRepo(self)
        for owner in organization.owners:
            Manager(owner.user, self)

    def __repr__(self):
        return '<Project[{}] "{}" for "{}" >'.format(self.id, self.name, self.organization)

    def allowed_to_be_created_by(self, user):
        return self.organization.found(self, user)

    def allowed_to_be_modified_by(self, user):
        return self.found(self, user)

    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.found(self, user)

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
