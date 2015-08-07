from sqlalchemy.orm import validates

from rebase.common.database import DB, PermissionMixin, query_by_user_or_id
from rebase.common.query import query_from_class_to_user

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
        return query_by_user_or_id(cls, cls.get_all, user)

    @classmethod
    def _all(cls, user, id=None):
        return cls.as_manager(user).union(cls.as_contractor(user))


    @classmethod
    def query_by_user(cls, user):
        return cls.get_all(user)

    def filter_by_id(self, query):
        return query.filter(Review.id==self.id)

    @classmethod
    def get_all(cls, user, comment=None):
        return query_by_user_or_id(
            cls,
            cls._all,
            cls.filter_by_id,
            user, comment
        )

    @classmethod
    def as_manager(cls, user):
        import rebase.models
        return query_from_class_to_user(Review, [
            rebase.models.work.Work,
            rebase.models.work_offer.WorkOffer,
            rebase.models.ticket_snapshot.TicketSnapshot,
            rebase.models.ticket.Ticket,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)

    def as_contractor(user):
        import rebase.models
        return query_from_class_to_user(Review, [
            rebase.models.work.Work,
            rebase.models.work_offer.WorkOffer,
            rebase.models.contractor.Contractor,
        ], user)

    def allowed_to_be_created_by(self, user):
        if user.is_admin():
            return True
        return self.work.offer.contractor.user == user

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        return self.get_all(user, self).limit(100).all()

    def __repr__(self):
        return '<Review[{}] rating={}>'.format(self.id, self.rating)