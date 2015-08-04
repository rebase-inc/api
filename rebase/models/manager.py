from sqlalchemy.orm import validates

from rebase.models.role import Role
from rebase.models.user import User
from rebase.models.contractor import Contractor
import rebase.models.organization

from rebase.common.database import DB, PermissionMixin

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
        if not isinstance(organization, rebase.models.organization.Organization):
            raise ValueError(
                '{} field on {} must be {} not {}'.format(
                    'organization',
                    self.__tablename__,
                    rebase.models.organization.Organization,
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
        if user.admin:
            return cls.query
        return cls.get_all_as_manager(user).union(cls.get_cleared_managers(user))

    @classmethod
    def get_all_as_manager(cls, user, manager_id=None):
        query = cls.query.filter(Manager.user==user)
        query = query\
            .join(rebase.models.organization.Organization)\
            .join(rebase.models.manager.Manager)
        if manager_id:
            query = query.filter_by(id=manager_id)
        return query

    @classmethod
    def get_cleared_managers(cls, user, manager_id=None):
        ''' Return all managers for which user has a clearance '''
        query = cls.query
        if manager_id:
            query = query.filter_by(id=manager_id)
        return query\
            .join(rebase.models.organization.Organization)\
            .join(rebase.models.project.Project)\
            .join(rebase.models.code_clearance.CodeClearance)\
            .join(rebase.models.contractor.Contractor)\
            .filter(rebase.models.contractor.Contractor.user == user)

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        return Manager.get_all_as_manager(user, self.id).limit(100).all()

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return Manager.get_all_as_manager(user, self.id)\
            .union(Manager.get_cleared_managers(user, self.id))\
            .limit(100).all()

