import datetime
import itertools

from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from alveare.common.database import DB, PermissionMixin
import alveare.models.organization
import alveare.models.manager

class User(DB.Model, PermissionMixin):
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
        self.set_password(password)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    @classmethod
    def query_by_user(cls, user):
        if user.admin:
            return cls.query
        return cls.get_all_as_manager(user)\
            .union(cls.get_all_as_user(user))
            #.union(cls.get_all_as_contractor(user))\

    @classmethod
    def get_all_as_manager(cls, current_user, user_id=None):
        '''
        As a manager, there are 3 types of users you can read:
        - other managers in your org
        - cleared contractors for all projects in your org
        - nominated contractors for all projects in your org
        '''
        return cls.as_manager_get_other_managers(current_user, user_id)\
            .union(cls.as_manager_get_cleared_contractors(current_user, user_id))\
            .union(cls.as_manager_get_nominated_users(current_user, user_id))

    @classmethod
    def as_manager_get_other_managers(cls, current_user, user_id=None):
        query = cls.query.filter(cls.id==current_user.id)
        query = query\
            .join(alveare.models.manager.Manager)\
            .join(alveare.models.organization.Organization)\
            .join(alveare.models.manager.Manager)\
            .join(alveare.models.user.User)
        if user_id:
            query = query.filter(cls.id==user_id)
        return query

    @classmethod
    def as_manager_get_cleared_contractors(cls, current_user, user_id=None):
        query = cls.query.filter(cls.id==current_user.id)
        query = query\
            .join(alveare.models.manager.Manager)\
            .join(alveare.models.organization.Organization)\
            .join(alveare.models.project.Project)\
            .join(alveare.models.code_clearance.CodeClearance)\
            .join(alveare.models.contractor.Contractor)\
            .join(User)
        if user_id:
            query = query.filter(cls.id==user_id)
        return query

    @classmethod
    def as_manager_get_nominated_users(cls, current_user, user_id=None):
        query = cls.query.filter(cls.id==current_user.id)
        query = query\
            .join(alveare.models.manager.Manager)\
            .join(alveare.models.organization.Organization)\
            .join(alveare.models.project.Project)\
            .join(alveare.models.ticket.Ticket)\
            .join(alveare.models.ticket_snapshot.TicketSnapshot)\
            .join(alveare.models.bid_limit.BidLimit)\
            .join(alveare.models.ticket_set.TicketSet)\
            .join(alveare.models.nomination.Nomination)\
            .join(alveare.models.contractor.Contractor)\
            .join(cls)
        if user_id:
            query = query.filter(cls.id==user_id)
        return query

    @classmethod
    def get_all_as_contractor(cls, current_user, user_id=None):
        return cls.as_contractor_get_managers(current_user, user_id)\
            .join(cls.as_contractor_get_cleared_contractors(current_user, user_id))

    @classmethod
    def as_contractor_get_managers(cls, current_user, user_id=None):
        query = cls.query.filter(cls.id==current_user.id)
        query = query\
            .join(alveare.models.contractor.Contractor)\
            .join(alveare.models.code_clearance.CodeClearance)\
            .join(alveare.models.project.Project)\
            .join(alveare.models.organization.Organization)\
            .join(alveare.models.manager.Manager)\
            .join(cls)
        if user_id:
            query = query.filter(cls.id==user_id)
        return query

    @classmethod
    def as_contractor_get_cleared_contractors(cls, current_user, user_id=None):
        query = cls.query.filter(cls.id==current_user.id)
        query = query\
            .join(alveare.models.contractor.Contractor)\
            .join(alveare.models.code_clearance.CodeClearance)\
            .join(alveare.models.project.Project)\
            .join(alveare.models.code_clearance.CodeClearance)\
            .join(alveare.models.contractor.Contractor)\
            .join(cls)
        if user_id:
            query = query.filter(cls.id==user_id)
        return query

    @classmethod
    def get_all_as_user(cls, current_user, user_id=None):
        return cls.query.filter(cls.id==current_user.id)

    def allowed_to_be_created_by(self, user):
        return True

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        return self.allowed_to_be_created_by(user)

    # flask login helper functions
    def is_admin(self): return self.admin
    def is_authenticated(self): return True
    def is_active(self): return True
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)
    def get_role(self): return False

    @property
    def manager_roles(self):
        return self.roles.filter_by(type = 'manager')

    @property
    def contractor_roles(self):
        return self.roles.filter_by(type = 'contractor')

    @property
    def manager_for_organizations(self):
        return [manager.organization.id for manager in self.manager_roles]

    def __repr__(self):
        return '<User[id:{}] first_name={} last_name={} email={}>'.format(self.id, self.first_name, self.last_name, self.email)

