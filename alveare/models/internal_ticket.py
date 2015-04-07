
from alveare.common.database import DB
from alveare.models.ticket import Ticket

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
        return super(cls, cls)\
            .get_all_as_manager(user, project_type='project')\
            .union(super(cls, cls).get_cleared_projects(user, project_type='project'))

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        return InternalTicket.get_all_as_manager(user, self.id, 'project').limit(100).all()

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return InternalTicket.get_cleared_projects(user, self.id, 'project').union(
            InternalTicket.get_all_as_manager(user, self.id, 'project')
        ).limit(100).all()
