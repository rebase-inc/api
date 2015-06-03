
from alveare.common.database import DB, PermissionMixin
import alveare.models.organization
import alveare.models.manager
import alveare.models.project

class Ticket(DB.Model, PermissionMixin):
    __pluralname__ = 'tickets'

    id =            DB.Column(DB.Integer, primary_key=True)
    title =         DB.Column(DB.String, nullable=False)
    description =   DB.Column(DB.String, nullable=False)
    project_id =    DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    discriminator = DB.Column(DB.String)

    skill_requirement =     DB.relationship('SkillRequirement',     backref='ticket', cascade='all, delete-orphan', passive_deletes=False, uselist=False)
    snapshots =             DB.relationship('TicketSnapshot',       backref='ticket', cascade='all, delete-orphan', passive_deletes=False)
    comments =              DB.relationship('Comment',              backref='ticket', cascade='all, delete-orphan', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'ticket',
        'polymorphic_on': discriminator
    }

    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def query_by_user(cls, user):
        if user.admin:
            return cls.query
        return cls.get_all_as_manager(user).union(cls.get_cleared_projects(user))

    @classmethod
    def get_all_as_manager(cls, user, ticket_id=None, project_type=None):
        query = cls.query
        if ticket_id:
            query = query.filter_by(id=ticket_id)
        query = query.join(alveare.models.project.Project)
        if project_type:
            query = query.filter(alveare.models.project.Project.type == project_type)
        return query\
            .join(alveare.models.organization.Organization)\
            .join(alveare.models.manager.Manager)\
            .filter(alveare.models.manager.Manager.user == user)

    @classmethod
    def get_cleared_projects(cls, user, ticket_id=None, project_type=None):
        ''' Return all projects for which user has a clearance '''
        query = cls.query
        if ticket_id:
            query = query.filter_by(id=ticket_id)
        query = query.join(alveare.models.project.Project)
        if project_type:
            query = query.filter(alveare.models.project.Project.type == project_type)
        return query\
            .join(alveare.models.code_clearance.CodeClearance)\
            .join(alveare.models.contractor.Contractor)\
            .filter(alveare.models.contractor.Contractor.user == user)

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        return Ticket.get_all_as_manager(user, self.id).limit(100).all()

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return Ticket.get_cleared_projects(user, self.id).union(
            Ticket.get_all_as_manager(user, self.id)
        ).limit(100).all()

    def __repr__(self):
        return '<Ticket[{}] title="{}">'.format(self.id, self.title)
