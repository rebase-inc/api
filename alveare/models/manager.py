from sqlalchemy.orm import validates

from alveare.models.role import Role
from alveare.models.user import User
from alveare.models.contractor import Contractor
from alveare.models.organization import Organization

from alveare.common.database import DB

class Manager(Role):
    __pluralname__ = 'managers'
    id =                DB.Column(DB.Integer, DB.ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    organization_id =   DB.Column(DB.Integer, DB.ForeignKey('organization.id', ondelete='CASCADE'))

    __mapper_args__ = { 'polymorphic_identity': 'manager' }

    def __init__(self, user, organization):
        if not isinstance(user, User):
            raise ValueError('{} field on {} must be {} not {}'.format('user', self.__tablename__, User, type(user)))
        if not isinstance(organization, Organization):
            raise ValueError('{} field on {} must be {} not {}'.format('organization', self.__tablename__, Organization, type(user)))
        self.user = user
        self.organization = organization

    def __repr__(self):
        return '<Manager[{}]>'.format(self.id)
