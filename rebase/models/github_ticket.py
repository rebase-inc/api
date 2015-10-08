
from rebase.common.database import DB
from rebase.models import RemoteTicket

class GithubTicket(RemoteTicket):
    __pluralname__ = 'github_tickets'

    id =        DB.Column(DB.Integer, DB.ForeignKey('remote_ticket.id', ondelete='CASCADE'), primary_key=True)
    number =    DB.Column(DB.Integer, nullable=False)

    __mapper_args__ = { 'polymorphic_identity': 'github_ticket' }

    def __init__(self, project, number, title='NOTIMPLEMENTED', description='NOTIMPLEMENTED'):
        self.project = project
        self.number = number
        self.title = title #this should be pulled from github
        self.description = title #this should be pulled from github

    @classmethod
    def setup_queries(cls, models):
        cls.as_contractor_path = [
            models.GithubProject,
            models.CodeClearance,
            models.Contractor,
        ]

        cls.as_manager_path = [
            models.GithubProject,
            models.Manager,
        ]

        cls.as_owner_path = cls.as_manager_path

    def __repr__(self):
        return '<GithubTicket[id:{}] number={}>'.format(self.id, self.number)

