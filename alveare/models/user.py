import datetime
import itertools

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import or_, sql

from flask.ext.login import login_user, logout_user

from werkzeug.security import generate_password_hash, check_password_hash

from alveare.common.database import DB
from alveare.models import Auction

class User(DB.Model):
    __pluralname__ = 'users'

    id =                DB.Column(DB.Integer,   primary_key=True)
    first_name =        DB.Column(DB.String,    nullable=False)
    last_name =         DB.Column(DB.String,    nullable=False)
    email =             DB.Column(DB.String,    nullable=False)
    hashed_password =   DB.Column(DB.String,    nullable=False)
    last_seen =         DB.Column(DB.DateTime,  nullable=False)
    roles =             DB.relationship('Role', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    admin =             DB.Column(DB.Boolean,   nullable=False, default=False)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hashed_password = generate_password_hash(password)
        self.last_seen = datetime.datetime.now()
        self._manager_roles = None
        self._contractor_roles = None

    def check_password(self, password):
        if not password:
            return False
        return check_password_hash(self.hashed_password, password)

    # flask login helper functions
    def is_admin(self): return self.admin
    def is_authenticated(self): return True
    def is_active(self): return True
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)
    def get_role(self): return

    @hybrid_property
    def manager_roles(self):
        return self.roles.filter_by(type = 'manager')

    @hybrid_property
    def contractor_roles(self):
        return self.roles.filter_by(type = 'contractor')

    @hybrid_property
    def auction_query(self):
        # if you're admin, you can see everything
        from alveare.models import Auction
        query = Auction.query
        if self.is_admin():
            return query

        manager_for_organization = [manager.organization.id for manager in self.manager_roles]
        auctions_approved_for = []
        for contractor in self.contractor_roles.all():
            auctions_approved_for.extend(contractor.auctions_approved_for)

        all_filters = []
        if auctions_approved_for:
            all_filters.append(Auction.id.in_(auctions_approved_for))
        if manager_for_organization:
            all_filters.append(Auction.organization_id.in_(manager_for_organization))
        if not all_filters:
            return query.filter(sql.false())
        return query.filter(or_(*all_filters))

    @hybrid_property
    def nomination_query(self):
        ''' you should be able to see a nomination if you're a manager for the organization that owns the ticket_set '''
        from alveare.models import Nomination, TicketSet, BidLimit, TicketSnapshot, Ticket, Organization, Project, Contractor
        query = Nomination.query
        if self.is_admin(): return query

        # TODO: Make this part of the filter
        manager_for_organization = [manager.organization.id for manager in self.manager_roles]

        if manager_for_organization:
            query = Nomination.query
            query = query.join(Nomination.ticket_set)
            query = query.join(TicketSet.bid_limits)
            query = query.join(BidLimit.ticket_snapshot)
            query = query.join(TicketSnapshot.ticket)
            query = query.join(Ticket.project)
            query = query.join(Project.organization)
            query = query.filter(Organization.id.in_(manager_for_organization))
            return query
        else:
            return query.filter(sql.false())

    def allowed_to_delete(self, instance):
        return self.allowed_to_modify(instance)

    def allowed_to_modify(self, instance):
        if self.is_admin(): return True

        from alveare.models import Nomination
        if isinstance(instance, Nomination):
            # TODO: Optimize
            manager_for_organization = [manager.organization.id for manager in self.manager_roles]
            return (instance.ticket_set.bid_limits[0].ticket_snapshot.ticket.project.organization.id in manager_for_organization)
        else:
            return True

    def allowed_to_get(self, instance):
        if self.is_admin(): return True

        from alveare.models import Nomination
        if isinstance(instance, Nomination):
            managers = instance.ticket_set.bid_limits[0].ticket_snapshot.ticket.project.organization.managers
            return set(self.manager_roles) & set(managers)
        else:
            return True

    def __repr__(self):
        return '<User[id:{}] first_name={} last_name={} email={}>'.format(self.id, self.first_name, self.last_name, self.email)

