import datetime

from rebase.common.database import DB
from rebase.models.ticket import Ticket

class InternalTicket(Ticket):
    __pluralname__ = 'internal_tickets'

    id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'internal_ticket' }

    def __init__(self, project, title, description=''):
        self.project = project
        self.title = title
        self.description = description
        self.created = datetime.datetime.now()

    def __repr__(self):
        return '<InternalTicket[id:{}]>'.format(self.id)

    @classmethod
    def query_by_user(cls, user):
        if user.admin:
            return cls.query
        return super(cls, cls).role_to_query_fn(user)(user, project_type='project')

    def allowed_to_be_created_by(self, user):
        return self.project.allowed_to_be_modified_by(user)

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.project.allowed_to_be_viewed_by(user)
