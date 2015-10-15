
from sqlalchemy.orm import validates
from rebase.common.database import DB, PermissionMixin

from .contractor import Contractor

class RemoteWorkHistory(DB.Model, PermissionMixin):
    __pluralname__ = 'remote_work_histories'

    id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True, nullable=False)

    def __init__(self, contractor):
        self.contractor = contractor

    @validates('contractor')
    def validate_contractor(self, field, value):
        if value and not isinstance(value, Contractor):
            raise ValueError('{} field on {} must be {} not {}'.format(field, self.__tablename__, Contractor, type(value)))
        return value

    @classmethod
    def query_by_user(cls, user):
        from rebase.models import Contractor
        if user.admin:
            return cls.query
        return cls.query.join(Contractor).filter(Contractor.user == user)

    def allowed_to_be_created_by(self, user):
        if user.is_admin():
            return True
        return RemoteWorkHistory.query_by_user(user).first()

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        return self.allowed_to_be_created_by(user)

    def __repr__(self):
        return '<RemoteWorkHistory[{}] >'.format(self.id)
