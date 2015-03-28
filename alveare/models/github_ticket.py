
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
        return '<GithubTicket[id:{}] number={}>'.format(self.id, self.number)

