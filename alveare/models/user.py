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

    def query_for(self, model):
        queries = dict(
            auction = self.auction_query,
            nomination = self.nomination_query,
            bid = self.bid_query,
            feedback = self.feedback_query,
            contract = self.contract_query,
            work_offer = self.work_offer_query,
        )
        if model.__tablename__ not in queries:
            print('WARNING: All instances of {} are being returned unfiltered!\n'.format(model.__tablename__))
            return model.query
        else:
            return queries[model.__tablename__]()

    @property
    def manager_roles(self):
        return self.roles.filter_by(type = 'manager')

    @property
    def contractor_roles(self):
        return self.roles.filter_by(type = 'contractor')

    @property
    def manager_for_organizations(self):
        return [manager.organization.id for manager in self.manager_roles]

    def auction_query(self):
        from alveare.models import Auction, Organization, TicketSet, BidLimit, TicketSnapshot, Ticket, Project
        query = Auction.query
        if self.is_admin(): return query

        auctions_approved_for = []
        for contractor in self.contractor_roles.all():
            auctions_approved_for.extend(contractor.auctions_approved_for)

        all_filters = []
        if auctions_approved_for:
            all_filters.append(Organization.id.in_(auctions_approved_for))
        if self.manager_for_organizations:
            all_filters.append(Organization.id.in_(self.manager_for_organizations))
        if not all_filters:
            return query.filter(sql.false())
        query = query.join(Auction.ticket_set)
        query = query.join(TicketSet.bid_limits)
        query = query.join(BidLimit.ticket_snapshot)
        query = query.join(TicketSnapshot.ticket)
        query = query.join(Ticket.project)
        query = query.join(Project.organization)
        return query.filter(or_(*all_filters))

    def work_offer_query(self):
        from alveare.models import WorkOffer, Contractor, Bid, Auction, TicketSet
        from alveare.models import BidLimit, TicketSnapshot, Ticket , Organization
        query = WorkOffer.query

        if self.is_admin(): return query

        query = query.join(WorkOffer.contractor)
        query = query.join(Contractor.user)

        all_filters = []
        if self.manager_for_organizations:
            query = query.join(WorkOffer.bid)
            query = query.join(Bid.auction)
            query = query.join(Auction.ticket_set)
            query = query.join(TicketSet.bid_limits)
            query = query.join(BidLimit.ticket_snapshot)
            query = query.join(TicketSnapshot.ticket)
            query = query.join(Ticket.organization)
            all_filters.append(Organization.id.in_(self.manager_for_organizations))

        all_filters.append(User.id == self.id)
        return query.filter(or_(*all_filters))

    def contract_query(self):
        from alveare.models import Contract, Bid, Contractor, User
        query = Contract.query
        if self.is_admin():
            return query
        query = query.join(Contract.bid)
        query = query.join(Bid.auction)
        query = query.join(Bid.contractor)
        query = query.join(Contractor.user)

        all_filters = []
        if self.manager_for_organizations:
            all_filters.append(User.id.in_([m.user.id for m in self.manager_roles]))
        all_filters.append(User.id == self.id)
        return query.filter(or_(*all_filters))

    def bid_query(self):
        from alveare.models import Bid, Contractor, User
        query = Bid.query
        if self.is_admin():
            return query
        query = query.join(Bid.contractor)
        query = query.join(Contractor.user)

        all_filters = []
        if self.manager_for_organizations:
            all_filters.append(User.id.in_([m.user.id for m in self.manager_roles]))
        all_filters.append(User.id == self.id)
        return query.filter(or_(*all_filters))

    def feedback_query(self):
        from alveare.models import Feedback, Contractor, User
        query = Feedback.query
        if self.is_admin():
            return query
        query = query.join(Feedback.contractor)
        query = query.join(Contractor.user)

        auctions_approved_for = []
        for contractor in self.contractor_roles.all():
            auctions_approved_for.extend(contractor.auctions_approved_for)

        all_filters = []
        if auctions_approved_for:
            all_filters.append(Feedback.auction.organization_id.in_(self.manager_for_organizations))
        all_filters.append(User.id == self.id)
        return query.filter(or_(*all_filters))

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
        from alveare.models import Nomination, Auction, Bid, WorkOffer
        if self.is_admin(): return True

        if isinstance(instance, Nomination):
            organization_id = instance.ticket_set.bid_limits[0].ticket_snapshot.ticket.organization.id
            return bool(organization_id in self.manager_for_organizations)
        elif isinstance(instance, Auction):
            organization_id = instance.ticket_set.bid_limits[0].ticket_snapshot.ticket.organization.id
            return bool(organization_id in self.manager_for_organizations)
        elif isinstance(instance, Bid):
            return bool(instance.contractor.user == self)
        elif isinstance(instance, WorkOffer):
            return bool(instance.contractor.user == self)
        else:
            return True


    def allowed_to_delete(self, instance):
        return self.allowed_to_modify(instance)

    def allowed_to_modify(self, instance):
        if self.is_admin(): return True

        from alveare.models import Nomination, Auction, Bid, Project, Feedback, Contract, WorkOffer
        if isinstance(instance, Nomination):
            organization_id = instance.ticket_set.bid_limits[0].ticket_snapshot.ticket.project.organization.id
            return bool(organization_id in self.manager_for_organizations)
        elif isinstance(instance, Auction):
            organization_id = instance.ticket_set.bid_limits[0].ticket_snapshot.ticket.project.organization.id
            return bool(organization_id in self.manager_for_organizations)
        elif isinstance(instance, Bid):
            return bool(instance.contractor.user == self)
        elif isinstance(instance, Feedback):
            return bool(instance.contractor.user == self)
        elif isinstance(instance, Contract):
            return bool(instance.bid.contractor.user == self)
        elif isinstance(instance, Project):
            from alveare.models import Manager
            return bool(self.manager_roles.filter(Manager.organization_id == instance.organization.id).all())
        elif isinstance(instance, WorkOffer):
            return bool(instance.contractor.user == self)
        else:
            return True

    def allowed_to_get(self, instance):
        if self.is_admin(): return True

        # If you're allowed to modify, you must be allowed to get.
        # The inverse is not true, however.
        # Until we find a counter example, I think this is reasonable.
        if self.allowed_to_modify(instance): return True

        from alveare.models import Nomination, Auction, Bid, Project, Feedback, Contract, WorkOffer
        if isinstance(instance, Auction):
            users_approved = [nomination.contractor.user.id for nomination in instance.approved_talents]
            return bool(self.id in users_approved)
        elif isinstance(instance, Nomination):
            return False # hack until we get to the point where we can remove the else: return True statement below
        elif isinstance(instance, Contract):
            return bool(instance.bid.auction.organization.id in self.manager_for_organizations)
        elif isinstance(instance, Bid):
            return bool(instance.auction.organization.id in self.manager_for_organizations)
        elif isinstance(instance, Feedback):
            return bool(instance.auction.organization.id in self.manager_for_organizations)
        elif isinstance(instance, Project):
            return bool(instance.organization_id in self.manager_for_organizations)
        elif isinstance(instance, WorkOffer):
            return bool(instance.bid and instance.bid.auction.organization.id in self.manager_for_organizations)
        else:
            return True

    def __repr__(self):
        return '<User[id:{}] first_name={} last_name={} email={}>'.format(self.id, self.first_name, self.last_name, self.email)

