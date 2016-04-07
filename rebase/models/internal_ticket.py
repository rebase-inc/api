import datetime

from rebase.common.database import DB
from rebase.models.ticket import Ticket

class InternalTicket(Ticket):
    __pluralname__ = 'internal_tickets'

    id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'internal_ticket' }

    def __init__(self, title, first_comment=None, project=None):
        from rebase.models import Comment, SkillRequirement
        from flask.ext.login import current_user
        if project:
            self.project = project
        elif current_user.current_role.type == 'manager':
            self.project = current_user.current_role.project
        else:
            raise ClientError(message='Missing project field')
        self.title = title
        self.created = datetime.datetime.now()
        self.skill_requirement = SkillRequirement(self)
        if first_comment:
            Comment(current_user, first_comment, ticket=self)

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
