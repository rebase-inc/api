
from alveare.common.database import DB
from alveare.models import RemoteTicket

class GithubTicket(RemoteTicket):
    __pluralname__ = 'github_tickets'

    id =        DB.Column(DB.Integer, DB.ForeignKey('remote_ticket.id', ondelete='CASCADE'), primary_key=True)
    number =    DB.Column(DB.Integer, nullable=False)

    __mapper_args__ = { 'polymorphic_identity': 'github_ticket' }

    def __init__(self, project, number):
        self.project = project
        self.number = number
        self.title = 'NOTIMPLEMENTED' #this should be pulled from github
        self.description = 'NOTIMPLEMENTED' #this should be pulled from github

    def __repr__(self):
        return '<GithubTicket[id:{}] number={}>'.format(self.id, self.number)

