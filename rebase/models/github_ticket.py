import datetime

from rebase.common.database import DB
from rebase.models import RemoteTicket

class GithubTicket(RemoteTicket):
    __pluralname__ = 'github_tickets'

    id =        DB.Column(DB.Integer, DB.ForeignKey('remote_ticket.id', ondelete='CASCADE'), primary_key=True)
    number =    DB.Column(DB.Integer, nullable=False)

    __mapper_args__ = { 'polymorphic_identity': 'github_ticket' }

    def __init__(self, project, number, title, created):
        from rebase.models.skill_requirement import SkillRequirement
        self.project = project
        self.title = title
        self.number = number
        self.created = created
        self.skill_requirement = SkillRequirement(self)

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

