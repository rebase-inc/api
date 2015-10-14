import datetime

from sqlalchemy.orm import validates

from rebase.common.database import DB, PermissionMixin

class Review(DB.Model, PermissionMixin):
    __pluralname__ = 'reviews'

    id = DB.Column(DB.Integer, primary_key=True)
    _rating = DB.Column(DB.Integer)
    created = DB.Column(DB.DateTime, nullable=False)
    work_id = DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)

    comments = DB.relationship('Comment', lazy='dynamic', backref='review', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, work):
        if work.review:
            raise ValueError('Work is already reviewed!')
        self.work = work
        self._rating = 0
        self.created = datetime.datetime.now()

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, new_rating):
        if not isinstance(new_rating, int):
            raise ValueError('{} field on {} must be {}'.format('rating', self.__tablename__, int))
        if new_rating < 1 or new_rating > 5:
            raise ValueError('{} field on {} must be {}'.format('rating', self.__tablename__, 'from 1 to 5'))
        self._rating = new_rating

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_modified_by(self, user):
        if user.is_admin():
            return True
        return self.role_to_query_fn(user)(user).filter(Review.id==self.id).first()

    allowed_to_be_viewed_by = allowed_to_be_modified_by

    def __repr__(self):
        return '<Review[{}] rating={}>'.format(self.id, self.rating)

    @classmethod
    def setup_queries(cls, models):
        cls.as_contractor_path = [
            models.Work,
            models.WorkOffer,
            models.Contractor,
        ]

        cls.as_manager_path = [
            models.Work,
            models.WorkOffer,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Manager,
        ]

        cls.as_owner_path = cls.as_manager_path
