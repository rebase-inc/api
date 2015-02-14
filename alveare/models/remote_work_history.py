
from sqlalchemy.orm import validates
from alveare.common.database import DB

from .contractor import Contractor

class RemoteWorkHistory(DB.Model):

    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id'), primary_key=True, nullable=False)

    contractor = DB.relationship('Contractor', uselist=False, backref=DB.backref('remote_work_history', cascade='all, delete-orphan'))

    def __init__(self, contractor):
        self.contractor = contractor

    @validates('contractor')
    def validate_work_offer(self, field, value):
        if not isinstance(value, Contractor):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, Contractor))
        return value

    def __repr__(self):
        return '<RemoteWorkHistory[{}] >'.format(self.contractor_id)
