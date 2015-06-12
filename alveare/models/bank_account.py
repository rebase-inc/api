from sqlalchemy.orm import validates

from alveare.common.database import DB, PermissionMixin, query_by_user_or_id
from alveare.common.query import query_from_class_to_user

class BankAccount(DB.Model, PermissionMixin):
    __pluralname__ = 'bank_accounts'

    id =                DB.Column(DB.Integer, primary_key=True)
    organization_id =   DB.Column(DB.Integer, DB.ForeignKey('organization.id', ondelete='CASCADE'), nullable=True)
    contractor_id =     DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), nullable=True)
    name =              DB.Column(DB.String, nullable=False)
    routing_number =    DB.Column(DB.Integer, nullable=False)
    account_number =    DB.Column(DB.Integer, nullable=False)

    def __init__(self, name, routing_number, account_number, organization=None, contractor=None):
        self.name = name
        self.routing_number = routing_number
        self.account_number = account_number

        self.organization = organization
        self.contractor = contractor

    def filter_by_id(self, query):
        return query.filter(BankAccount.id==self.id)

    @classmethod
    def as_contractor(cls, user):
        import alveare.models
        return query_from_class_to_user(BankAccount, [alveare.models.contractor.Contractor], user)

    @classmethod
    def as_manager(cls, user, bank_account_id=None):
        import alveare.models
        return query_from_class_to_user(BankAccount, [
            alveare.models.organization.Organization,
            alveare.models.manager.Manager,
        ], user)

    @classmethod
    def get_all(cls, user, account=None):
        return query_by_user_or_id(
            cls,
            lambda user: cls.as_manager(user).union(cls.as_contractor(user)),
            BankAccount.filter_by_id,
            user,
            account
        )

    @classmethod
    def query_by_user(cls, user):
        return cls.get_all(user)

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        if self.organization:
            return self.organization.allowed_to_be_modified_by(user)
        if self.contractor:
            return self.contractor.allowed_to_be_modified_by(user)
        raise ValueError('BankAccount instance is missing an organization or a contractor')

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by
    allowed_to_be_viewed_by = allowed_to_be_created_by

    def __repr__(self):
        return '<BankAccount[{}] name="{}" routing={} account={}>'.format(self.id, self.name, self.routing_number, self.account_number)

    @validates('routing_number')
    def validate_routing(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        if len(str(abs(value))) != 9:
            raise ValueError('{} field on {} must be {} digits'.format(field, self.__tablename__, 9))
        return value

    @validates('account_number')
    def validate_account(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value
