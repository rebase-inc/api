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
    def setup_queries(cls, models):
        cls.as_contractor_path = [
            models.InternalProject,
            models.CodeClearance,
            models.Contractor,
        ]

        cls.as_manager_path = [
            models.InternalProject,
            models.Manager,
        ]

        cls.as_owner_path = cls.as_manager_path
