from sqlalchemy.orm import validates

from alveare.common.database import DB, PermissionMixin, query_by_user_or_id

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

    @classmethod
    def query_by_user(cls, user):
        return query_by_user_or_id(cls, cls.get_all, user)

    @classmethod
    def get_all(cls, user, account=None):
        return cls.as_contractor(user, account)\
            .union(cls.as_manager(user, account))

    @classmethod
    def as_contractor(cls, user, bank_account_id=None):
        import alveare.models.contractor
        query = cls.query\
            .join(alveare.models.contractor.Contractor)\
            .filter(alveare.models.contractor.Contractor.user==user)
        if bank_account_id:
            query = query.filter(cls.id==bank_account_id)
        return query

    @classmethod
    def as_manager(cls, user, bank_account_id=None):
        import alveare.models.organization
        query = cls.query\
            .join(alveare.models.organization.Organization)\
            .join(alveare.models.Manager)\
            .filter(alveare.models.manager.Manager.user==user)
        if bank_account_id:
            query = query.filter(cls.id==bank_account_id)
        return query

    def allowed_to_be_created_by(self, user):
        return user.admin or self.get_all(user, self.id).all()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return self.get_all(user, self.id).all()

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
