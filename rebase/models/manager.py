
from rebase.models.role import Role
from rebase.common.database import DB

class Manager(Role):
    __pluralname__ = 'managers'

    id =            DB.Column(DB.Integer, DB.ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    project_id =    DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)

    __mapper_args__ = { 'polymorphic_identity': 'manager' }

    def __init__(self, user, project):
        self.user = user
        self.project = project

    def __repr__(self):
        return '<Manager[{}, [{}]] {})>'.format(
            self.id,
            self.project.name,
            self.user.name
        )

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        return Manager.as_manager(user).limit(1).first()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.found(self, user)

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
