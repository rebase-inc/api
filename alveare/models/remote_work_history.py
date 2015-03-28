
from sqlalchemy.orm import validates
from alveare.common.database import DB, PermissionMixin

from .contractor import Contractor

class RemoteWorkHistory(DB.Model, PermissionMixin):
    __pluralname__ = 'remote_work_histories'

    id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True, nullable=False)

    github_accounts = DB.relationship('GithubAccount', backref='remote_work_history', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, contractor):
        self.contractor = contractor

    @validates('contractor')
    def validate_contractor(self, field, value):
        if value and not isinstance(value, Contractor):
            raise ValueError('{} field on {} must be {} not {}'.format(field, self.__tablename__, Contractor, type(value)))
        return value

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
        return '<RemoteWorkHistory[{}] >'.format(self.id)
