
from alveare.common.database import DB
from alveare.models.ticket import Ticket
import alveare.models.organization
import alveare.models.manager
import alveare.models.project

class InternalTicket(Ticket):
    __pluralname__ = 'internal_tickets'

    id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'internal_ticket' }

    def __init__(self, project, title, description=''):
        self.project = project
        self.title = title
        self.description = description

    def __repr__(self):
        return '<InternalTicket[id:{}]>'.format(self.id)

    @classmethod
    def query_by_user(cls, user):
        if user.admin:
            return cls.query
        return cls.get_all_as_manager(user).union(cls.get_cleared_projects(user))

    @classmethod
    def get_all_as_manager(cls, user, ticket_id=None):
        query = cls.query
        if ticket_id:
            query = query.filter_by(id=ticket_id)
        return query\
            .join(alveare.models.project.Project)\
            .filter(alveare.models.project.Project.type == 'project')\
            .join(alveare.models.organization.Organization)\
            .join(alveare.models.manager.Manager)\
            .filter(alveare.models.manager.Manager.user == user)

    @classmethod
    def get_cleared_projects(cls, user):
        ''' Return all projects for which user has a clearance '''
        return cls.query\
            .join(alveare.models.project.Project)\
            .filter(alveare.models.project.Project.type == 'project')\
            .join(alveare.models.code_clearance.CodeClearance)\
            .join(alveare.models.contractor.Contractor)\
            .filter(alveare.models.contractor.Contractor.user == user)

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        return InternalTicket.get_all_as_manager(user, self.id).limit(100).all()

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return InternalTicket.get_cleared_projects(user)\
            .filter(InternalTicket.id == self.id)\
            .union(InternalTicket.get_all_as_manager(user).filter(InternalTicket.id==self.id))\
            .limit(100).all()
