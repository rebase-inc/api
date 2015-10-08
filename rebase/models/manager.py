from sqlalchemy.orm import validates

from werkzeug.local import LocalProxy

from rebase.models.role import Role
from rebase.models.user import User
from rebase.models.contractor import Contractor

from rebase.common.database import DB, PermissionMixin

class Manager(Role):
    __pluralname__ = 'managers'
    id =            DB.Column(DB.Integer, DB.ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    project_id =    DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)

    __mapper_args__ = { 'polymorphic_identity': 'manager' }

    def __init__(self, user, project):
        self.user = user
        self.project = project

    def __repr__(self):
        return '<Manager[{}] {} {} (org {})>'.format(
            self.id,
            self.user.first_name,
            self.user.last_name,
            self.project_id
        )

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        return Manager.as_owner(user).limit(1).first()

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return self.project.allowed_to_be_viewed_by(user)

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.Project,
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.Project,
            models.CodeClearance,
            models.Contractor,
        ]

        cls.as_manager_path = [
            models.Project,
            models.Manager
        ]
