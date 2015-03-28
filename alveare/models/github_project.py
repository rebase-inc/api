
from alveare.common.database import DB

from alveare.models.remote_project import RemoteProject

class GithubProject(RemoteProject):
    __pluralname__ = 'github_projects'

    id = DB.Column(DB.Integer, DB.ForeignKey('remote_project.id', ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'github_project' }

    def __init__(self, organization, name):
        self.organization = organization
        self.name = name

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
        return '<GithubProject[id:{}]>'.format(self.id)

