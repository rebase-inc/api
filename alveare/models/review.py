from sqlalchemy.orm import validates

from alveare.common.database import DB, PermissionMixin

class Review(DB.Model, PermissionMixin):
    __pluralname__ = 'reviews'

    id =      DB.Column(DB.Integer, primary_key=True)
    rating =  DB.Column(DB.Integer, nullable=False)
    work_id = DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)

    comments = DB.relationship('Comment', lazy='dynamic', backref='review', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, work, rating):
        if not isinstance(rating, int):
            raise ValueError('{} field on {} must be {}'.format('rating', self.__tablename__, int))
        if rating < 1 or rating > 5:
            raise ValueError('{} field on {} must be {}'.format('rating', self.__tablename__, 'from 1 to 5'))
        if work.review:
            raise ValueError('Work is already reviewed!')
        self.work = work
        self.rating = rating

    @classmethod
    def query_by_user(cls, user):
        return cls.query

    def allowed_to_be_created_by(self, user):
        return True

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        return self.allowed_to_be_created_by(user)

    def __repr__(self):
        return '<Review[{}] rating={}>'.format(self.id, self.rating)
