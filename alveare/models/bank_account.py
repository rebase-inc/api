from sqlalchemy.orm import validates

from alveare.common.database import DB

class BankAccount(DB.Model):
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
