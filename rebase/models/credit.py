from sqlalchemy.orm import validates

from rebase.common.database import DB, PermissionMixin

class Credit(DB.Model, PermissionMixin):
    __pluralname__ = 'credits'

    id =      DB.Column(DB.Integer, primary_key=True)
    price =   DB.Column(DB.Integer, nullable=False)
    paid =    DB.Column(DB.Boolean, nullable=False, default=False)
    work_id = DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, work, price):
        if not hasattr(work, 'debit'):
            raise ValueError('work must be of a Work type')
        if work.credit:
            raise ValueError('Work is already credited!')
        self.work = work
        self.price = price

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.Work,
            models.WorkOffer,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.Work,
            models.WorkOffer,
            models.Bid,
            models.Contractor,
        ]
        cls.as_manager_path = [
            models.Work,
            models.WorkOffer,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Manager
        ]

    def allowed_to_be_created_by(self, user):
        return self.work.allowed_to_be_created_by(user)

    allowed_to_be_deleted_by = allowed_to_be_created_by
    allowed_to_be_modified_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.work.allowed_to_be_viewed_by(user)

    def __repr__(self):
        return '<Credit for {} {}>'.format(self.price, 'dollars')

    @validates('price')
    def validate_price(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value
