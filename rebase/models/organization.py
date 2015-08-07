from rebase.common.database import DB, PermissionMixin
import rebase.models.manager
#from rebase.models.project import Project
#from rebase.models.code_clearance import CodeClearance
#from rebase.models.contractor import Contractor

class Organization(DB.Model, PermissionMixin):
    __pluralname__ = 'organizations'

    id =   DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String)

    managers =      DB.relationship('Manager', backref=DB.backref('organization', lazy='joined', uselist=False), cascade='all, delete-orphan', passive_deletes=True, innerjoin=True)
    projects =      DB.relationship('Project', backref='organization', lazy='joined', cascade="all, delete-orphan", passive_deletes=True)
    bank_account =  DB.relationship('BankAccount', backref='organization', uselist=False, cascade='all, delete-orphan', passive_deletes=True)

    # fancy helper relationship
    tickets = DB.relationship('Ticket',
            secondary='project',
            primaryjoin='Organization.id == Project.organization_id',
            secondaryjoin='Project.id == Ticket.project_id',
            backref=DB.backref('organization', uselist=False),
            viewonly=True)

    @property
    def ticket_snapshots(self):
        ticket_snapshots = []
        for ticket in self.tickets:
            for snapshot in ticket.snapshots:
                ticket_snapshots.append(snapshot)
        return ticket_snapshots

    @property
    def bid_limits(self):
        bid_limits = []
        for snapshot in self.ticket_snapshots:
            if snapshot.bid_limit:
                bid_limits.append(snapshot.bid_limit)
        return bid_limits

    @property
    def ticket_sets(self):
        ticket_sets = []
        for bid_limit in self.bid_limits:
            ticket_set = bid_limit.ticket_set
            if ticket_set and ticket_set not in ticket_sets:
                ticket_sets.append(ticket_set)
        return ticket_sets

    @property
    def auctions(self):
        auctions = []
        for ticket_set in self.ticket_sets:
            auction = ticket_set.auction
            if auction and auction not in auctions:
                auctions.append(auction)
        return auctions

    def __init__(self, name, user):
        self.name = name
        self.managers.append(rebase.models.manager.Manager(user, self)) # you must have at least one manager

    @classmethod
    def query_by_user(cls, user):
        if user.admin:
            return cls.query
        return cls.get_all_as_manager(user).union(cls.get_all_as_contractor(user))

    def get_all_as_manager(user):
        return Organization.query.filter(Organization.managers.any(rebase.models.manager.Manager.user == user))

    def get_all_as_contractor(user):
        return Organization.query\
            .join(rebase.models.project.Project)\
            .join(rebase.models.code_clearance.CodeClearance)\
            .join(rebase.models.contractor.Contractor)\
            .filter(rebase.models.contractor.Contractor.user==user)

    def allowed_to_be_created_by(self, user):
        return True
    
    def in_managers(self, user):
        return Organization.get_all_as_manager(user).filter(Organization.id == self.id)

    def allowed_to_be_modified_by(self, user):
        if user.admin:
            return True
        return self.in_managers(user).limit(100).all()

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_modified_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return self.in_managers(user)\
            .union(Organization.get_all_as_contractor(user).filter(Organization.id==self.id))\
            .limit(100).all()

    def __repr__(self):
        return '<Organization[{}] "{}" >'.format(self.id, self.name)
