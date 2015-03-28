from alveare.common.database import DB, PermissionMixin

from .review import Review
from .mediation import Mediation
from .ticket import Ticket

class Comment(DB.Model, PermissionMixin):
    __pluralname__ = 'comments'

    id =        DB.Column(DB.Integer, primary_key=True)
    content =   DB.Column(DB.String,  nullable=False)

    review_id = DB.Column(DB.Integer, DB.ForeignKey('review.id', ondelete='CASCADE'), nullable=True)
    mediation_id = DB.Column(DB.Integer, DB.ForeignKey('mediation.id', ondelete='CASCADE'), nullable=True)
    ticket_id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), nullable=True)

    def __init__(self, parent, content=None):
        if isinstance(parent, Review):
            self.review = parent
        elif isinstance(parent, Mediation):
            self.mediation = parent
        elif isinstance(parent, Ticket):
            self.ticket = parent
        else:
            raise Exception('Unknown parent type for comment')
        self.content = content

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
        abbreviated_content = self.content[0:15]
        if self.content != abbreviated_content:
            abbreviated_content += '...'
        return '<Comment[{}] "{}">'.format(self.id, abbreviated_content)

