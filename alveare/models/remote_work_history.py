
from sqlalchemy.orm import validates
from alveare.common.database import DB

from .contractor import Contractor

class RemoteWorkHistory(DB.Model):

    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True, nullable=False)

    def __init__(self, contractor):
        self.contractor = contractor

    @validates('contractor')
    def validate_contractor(self, field, value):
        if value and not isinstance(value, Contractor):
            raise ValueError('{} field on {} must be {} not {}'.format(field, self.__tablename__, Contractor, type(value)))
        return value

    def __repr__(self):
        return '<RemoteWorkHistory[{}] >'.format(self.contractor_id)
