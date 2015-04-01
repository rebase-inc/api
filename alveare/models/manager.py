from sqlalchemy.orm import validates

from alveare.models.role import Role
from alveare.models.user import User
from alveare.models.contractor import Contractor
import alveare.models.organization

from alveare.common.database import DB, PermissionMixin

class Manager(Role):
    __pluralname__ = 'managers'
    id =                DB.Column(DB.Integer, DB.ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    organization_id =   DB.Column(DB.Integer, DB.ForeignKey('organization.id', ondelete='CASCADE'))

    __mapper_args__ = { 'polymorphic_identity': 'manager' }

    def __init__(self, user, organization):
        if not isinstance(user, User):
            raise ValueError('{} field on {} must be {} not {}'.format(
                'user',
                self.__tablename__,
                User,
                type(user)
            ))
        if not isinstance(organization, alveare.models.organization.Organization):
            raise ValueError(
                '{} field on {} must be {} not {}'.format(
                    'organization',
                    self.__tablename__,
                    alveare.models.organization.Organization,
                    type(organization))
            )
        self.user = user
        self.organization = organization

    def __repr__(self):
        return '<Manager[{}] {} {} (org {})>'.format(
            self.id,
            self.user.first_name,
            self.user.last_name,
            self.organization_id
        )

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
