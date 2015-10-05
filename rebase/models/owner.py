from sqlalchemy.orm import validates

from werkzeug.local import LocalProxy

from rebase.models.role import Role
from rebase.models.user import User
from rebase.models.organization import Organization

from rebase.common.database import DB, PermissionMixin

class Owner(Role):
    __pluralname__ = 'owners'
    id =                DB.Column(DB.Integer, DB.ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    organization_id =   DB.Column(DB.Integer, DB.ForeignKey('organization.id', ondelete='CASCADE'))

    __mapper_args__ = { 'polymorphic_identity': 'owner' }

    def __init__(self, user, org):
        if not isinstance(user, User):
            if isinstance(user, LocalProxy) and isinstance(user._get_current_object(), User):
                pass
            else:
                raise ValueError('{} field on {} must be {} not {}'.format(
                    'user',
                    self.__tablename__,
                    User,
                    type(user._get_current_object())
                ))
        if not isinstance(org, Organization):
            raise ValueError(
                '{} field on {} must be {} not {}'.format(
                    'organization',
                    self.__tablename__,
                    Organization,
                    type(org))
            )
        self.user = user
        self.organization = org

    def __repr__(self):
        return '<Owner[{}] {} {} (org {})>'.format(
            self.id,
            self.user.first_name,
            self.user.last_name,
            self.organization_id
        )

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        return Owner.get_all_as_owner(user, self.id).limit(100).all()

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return Owner.get_all_as_owner(user, self.id)\
            .union(Owner.get_cleared_owners(user, self.id))\
            .limit(100).all()

    @classmethod
    def setup_queries(cls, _):
        cls.as_owner_path = [
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.Work,
            models.WorkOffer,
            models.Contractor,
        ]

        cls.as_manager_path = [
            models.Work,
            models.WorkOffer,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Manager,
        ]
