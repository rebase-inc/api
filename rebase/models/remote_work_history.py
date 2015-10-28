
from sqlalchemy.orm import validates
from rebase.common.database import DB, PermissionMixin

from .contractor import Contractor

class RemoteWorkHistory(DB.Model, PermissionMixin):
    __pluralname__ = 'remote_work_histories'

    id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True)

    github_repos = DB.relationship('GithubContributedRepo', backref='remote_work_history', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, contractor):
        self.contractor = contractor

    @validates('contractor')
    def validate_contractor(self, field, value):
        if value and not isinstance(value, Contractor):
            raise ValueError('{} field on {} must be {} not {}'.format(field, self.__tablename__, Contractor, type(value)))
        return value

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.Contractor,
            models.CodeClearance,
            models.Project,
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.Contractor,
        ]
        cls.as_manager_path = [
            models.Contractor,
            models.CodeClearance,
            models.Project,
            models.Manager
        ]

    def allowed_to_be_created_by(self, user):
        return self.contractor.allowed_to_be_created_by(user)

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.contractor.allowed_to_be_viewed_by(user)

    def __repr__(self):
        return '<RemoteWorkHistory[{}] >'.format(self.id)
