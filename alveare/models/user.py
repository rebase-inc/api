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
    email =             DB.Column(DB.String,    nullable=False, unique=True)
    hashed_password =   DB.Column(DB.String,    nullable=False)
    last_seen =         DB.Column(DB.DateTime,  nullable=False)
    roles =             DB.relationship('Role', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    admin =             DB.Column(DB.Boolean,   nullable=False, default=False)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.last_seen = datetime.datetime.now()
        self._manager_roles = None
        self._contractor_roles = None
        self.set_password(password)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

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
    def manager_for_organizations(self):
        return [manager.organization.id for manager in self.manager_roles]

    @hybrid_property
    def auction_query(self):
        # if you're admin, you can see everything
        from alveare.models import Auction
        query = Auction.query
        if self.is_admin():
            return query

        auctions_approved_for = []
        for contractor in self.contractor_roles.all():
            auctions_approved_for.extend(contractor.auctions_approved_for)

        all_filters = []
        if auctions_approved_for:
            all_filters.append(Auction.id.in_(auctions_approved_for))
        if self.manager_for_organizations:
            all_filters.append(Auction.organization_id.in_(self.manager_for_organizations))
        if not all_filters:
            return query.filter(sql.false())
        return query.filter(or_(*all_filters))

    @hybrid_property
    def bid_query(self):
        from alveare.models import Bid
        query = Bid.query
        if self.is_admin():
            return query

        auctions_approved_for = []
        for contractor in self.contractor_roles.all():
            auctions_approved_for.extend(contractor.auctions_approved_for)

        all_filters = []
        if auctions_approved_for:
            all_filters.append(Bid.auction.organization_id.in_(self.manager_for_organizations))
        all_filters.append(Bid.contractor.user.id == self.id)
        return query.filter(or_(*all_filters))

    @hybrid_property
    def nomination_query(self):
        ''' you should be able to see a nomination if you're a manager for the organization that owns the ticket_set '''
        from alveare.models import (
            Nomination,
            TicketSet,
            BidLimit,
            TicketSnapshot,
            Ticket,
            Organization,
            Project,
            Contractor,
        )
        query = Nomination.query
        if self.is_admin(): return query

        # TODO: Make this part of the filter

        if self.manager_for_organizations:
            query = Nomination.query
            query = query.join(Nomination.ticket_set)
            query = query.join(TicketSet.bid_limits)
            query = query.join(BidLimit.ticket_snapshot)
            query = query.join(TicketSnapshot.ticket)
            query = query.join(Ticket.project)
            query = query.join(Project.organization)
            query = query.filter(Organization.id.in_(self.manager_for_organizations))
            return query
        else:
            return query.filter(sql.false())

    def allowed_to_create(self, instance):
        return self.allowed_to_modify(instance)

    def allowed_to_delete(self, instance):
        return self.allowed_to_modify(instance)

    def allowed_to_modify(self, instance):
        if self.is_admin(): return True

        from alveare.models import (
            Nomination,
            Auction,
            Bid,
            Project,
        )
        if isinstance(instance, Nomination):
            # TODO: Optimize
            organization_id = instance.ticket_set.bid_limits[0].ticket_snapshot.ticket.project.organization.id
            return bool(organization_id in self.manager_for_organizations)
        elif isinstance(instance, Auction):
            organization_id = instance.ticket_set.bid_limits[0].ticket_snapshot.ticket.project.organization.id
            return bool(organization_id in self.manager_for_organizations)
        elif isinstance(instance, Bid):
            return bool(instance.contractor.user == self)
        elif isinstance(instance, Project):
            from alveare.models import Manager
            return bool(self.manager_roles.filter(Manager.organization_id == instance.organization.id).all())
        else:
            return True

    def allowed_to_get(self, instance):
        if self.is_admin(): return True

        # If you're allowed to modify, you must be allowed to get.
        # The inverse is not true, however.
        # Until we find a counter example, I think this is reasonable.
        if self.allowed_to_modify(instance): return True

        from alveare.models import (Nomination,
                                    Auction,
                                    Bid,
                                    Project,
                                    )
        if isinstance(instance, Auction):
            users_approved = [nomination.contractor.user.id for nomination in instance.approved_talents]
            return bool(self.id in users_approved)
        elif isinstance(instance, Nomination):
            return False # hack until we get to the point where we can remove the else: return True statement below
        elif isinstance(instance, Bid):
            organization = instance.auction.ticket_set.bid_limit.ticket_snapshot.ticket.project.organization
            return bool(organization.id in self.manager_for_organizations)
        elif isinstance(instance, Project):
            return bool(instance.organization_id in self.manager_for_organizations)
        else:
            return True

    def __repr__(self):
        return '<User[id:{}] first_name={} last_name={} email={}>'.format(self.id, self.first_name, self.last_name, self.email)

