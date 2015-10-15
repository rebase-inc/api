
from rebase.common.database import DB

from rebase.models.remote_project import RemoteProject

class GithubProject(RemoteProject):
    __pluralname__ = 'github_projects'

    id = DB.Column(DB.Integer, DB.ForeignKey('remote_project.id', ondelete='CASCADE'), primary_key=True)
    
    __mapper_args__ = { 'polymorphic_identity': 'github_project' }

    @classmethod
    def query_by_user(cls, user):
        return super(cls, cls).query_by_user(user)

    def allowed_to_be_created_by(self, user):
        return super().allowed_to_be_created_by(user)

    def allowed_to_be_modified_by(self, user):
        return super().allowed_to_be_modified_by(user)

    def allowed_to_be_deleted_by(self, user):
        return super().allowed_to_be_deleted_by(user)

    def allowed_to_be_viewed_by(self, user):
        return super().allowed_to_be_viewed_by(user)

    def __repr__(self):
        return '<GithubProject[id:{} "{}"]>'.format(self.id, self.name)
