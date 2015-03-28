
from alveare.common.database import DB, PermissionMixin

class CodeRepository(DB.Model, PermissionMixin):
    __pluralname__ = 'code_repositories'

    id = DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), primary_key=True)

    def __init__(self, project):
        self.project = project

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
        return '<CodeRepository[id:{}]>'.format(self.id)

