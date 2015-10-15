from sqlalchemy.orm import validates

from werkzeug.local import LocalProxy

from rebase.models import (
    Role,
    User,
)

from rebase.common.database import DB, PermissionMixin

class Owner(Role):
    __pluralname__ = 'owners'
    id =                DB.Column(DB.Integer, DB.ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    organization_id =   DB.Column(DB.Integer, DB.ForeignKey('organization.id', ondelete='CASCADE'))

    __mapper_args__ = { 'polymorphic_identity': 'owner' }

    def __init__(self, user, org):
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
        return self.query_by_user(user).limit(1).first()

    @classmethod
    def setup_queries(cls, models):
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
