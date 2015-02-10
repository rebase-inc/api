from sqlalchemy.orm import validates

from alveare.common.database import DB

class Credit(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    price = DB.Column(DB.Integer, nullable=False)

    def __init__(self, price):
        self.price = price

    def __repr__(self):
        return '<Credit for {} {}>'.format(self.price, 'dollars')

    @validates('price')
    def validate_price(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value
