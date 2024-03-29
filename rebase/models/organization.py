from rebase.common.database import DB, PermissionMixin


class Organization(DB.Model, PermissionMixin):
    __pluralname__ = 'organizations'

    id =   DB.Column(DB.Integer, primary_key=True)
    type = DB.Column(DB.String)
    name = DB.Column(DB.String)

    owners =        DB.relationship('Owner', backref=DB.backref('organization', lazy='joined', uselist=False), cascade='all, delete-orphan', passive_deletes=False, innerjoin=True)
    projects =      DB.relationship('Project', backref='organization', lazy='joined', cascade="all, delete-orphan", passive_deletes=True)
    bank_account =  DB.relationship('BankAccount', backref='organization', uselist=False, cascade='all, delete-orphan', passive_deletes=True)

    # fancy helper relationship
    tickets = DB.relationship('Ticket',
            secondary='project',
            primaryjoin='Organization.id == Project.organization_id',
            secondaryjoin='Project.id == Ticket.project_id',
            backref=DB.backref('organization', uselist=False),
            viewonly=True)

    __mapper_args__ = {
        'polymorphic_identity': 'organization',
        'polymorphic_on': type
    }

    def __init__(self, name, user):
        from rebase.models.owner import Owner
        self.name = name
        Owner(user, self)

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

    def allowed_to_be_created_by(self, user):
        return True
    
    def allowed_to_be_modified_by(self, user):
        if user.admin:
            return True
        return self.as_owner(user).one()

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_modified_by(user)

    def allowed_to_be_viewed_by(self, user):
        return True
        return self.found(self, user)

    def __repr__(self):
        return '<Organization[{}] "{}" >'.format(self.id, self.name)

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.Project,
            models.CodeClearance,
            models.Contractor,
        ]

        cls.as_manager_path = [
            models.Project,
            models.Manager
        ]
