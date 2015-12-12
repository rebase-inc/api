import datetime

from flask.ext.login import current_user

from rebase.common.database import DB, PermissionMixin
from rebase.models.comment import Comment

class Blockage(DB.Model, PermissionMixin):
    __pluralname__ = 'blockages'

    id =            DB.Column(DB.Integer, primary_key=True)
    created =       DB.Column(DB.DateTime, nullable=False)
    ended =         DB.Column(DB.DateTime, nullable=True)
    work_id =       DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)
    comments =      DB.relationship('Comment', backref='blockage', lazy='joined', cascade='all, delete-orphan', passive_deletes=True, order_by='Comment.created')

    def __init__(self, work, comment):
        self.work = work
        self.created = datetime.datetime.now()
        Comment(current_user, comment, blockage=self)

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
            models.Organization,
            models.Manager,
        ]

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.found(self, user)

    def __repr__(self):
        return '<Blockage[id:{}] >'.format(self.id)
