import datetime
import itertools

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import or_

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

    # flask login helper functions
    def is_admin(self): return self.admin
    def is_authenticated(self): return True
    def is_active(self): return True
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)
    def get_role(self): return

    @hybrid_property
    def auction_query_filters(self):
        # if you're admin, you can see everything
        if self.is_admin():
            return None
        manager_roles = self.roles.filter_by(type = 'manager').all()
        contractor_roles = self.roles.filter_by(type = 'contractor').all()

        manager_for_organization = [manager.organization.id for manager in manager_roles]

        auctions_approved_for = []
        for contractor in contractor_roles:
            auctions_approved_for.extend(contractor.auctions_approved_for)

        all_filters = []
        if auctions_approved_for:
            all_filters.append(Auction.id.in_(auctions_approved_for))
        if manager_for_organization:
            all_filters.append(Auction.organization_id.in_(manager_for_organization))

        if not all_filters:
            return or_(None) #not sure why I have to wrap this in or_

        return or_(*all_filters)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hashed_password = password #hash it!!!
        self.last_seen = datetime.datetime.now()

    def __repr__(self):
        return '<User[id:{}] first_name={} last_name={} email={}>'.format(self.id, self.first_name, self.last_name, self.email)

