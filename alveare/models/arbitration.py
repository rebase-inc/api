from sqlalchemy.orm import validates

from alveare.common.database import DB

class Arbitration(DB.Model):
    id =            DB.Column(DB.Integer, primary_key=True)
    outcome =       DB.Column(DB.Integer, nullable=False) # TODO: Implement correctly

    def __init__(self, outcome):
        self.outcome = outcome

    def __repr__(self):
        return '<Arbitration[id:{}] >'.format(self.id)

    @validates('outcome')
    def validate_outcome(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value

