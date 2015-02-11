from sqlalchemy.orm import validates

from alveare.common.database import DB

class Review(DB.Model):
    id =      DB.Column(DB.Integer, primary_key=True)
    rating =  DB.Column(DB.Integer, nullable=False)
    work_id = DB.Column(DB.Integer, DB.ForeignKey('work.id'), nullable=False)

    comments = DB.relationship('Comment', lazy='dynamic', backref='review')

    def __init__(self, work, rating):
        if work.review:
            raise ValueError('Work is already reviewd!')
        self.work = work
        self.rating = rating

    def __repr__(self):
        return '<Review[{}] rating={}>'.format(self.id, self.rating)

    @validates('rating')
    def validate_rating(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        if value < 1 or value > 5:
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, 'from 1 to 5'))
        return value
