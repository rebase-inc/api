from sqlalchemy.orm import validates

from alveare.common.database import DB

class Credit(DB.Model):
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

    def pay_off(self):
        self.paid = True

    def __repr__(self):
        return '<Credit for {} {}>'.format(self.price, 'dollars')

    @validates('price')
    def validate_price(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value
