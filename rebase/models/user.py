import datetime
import itertools

from flask.ext.login import login_user, logout_user
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import aliased
from werkzeug.security import generate_password_hash, check_password_hash

from rebase.common.database import DB, PermissionMixin, query_by_user_or_id
from rebase.common.query import query_from_class_to_user
import rebase.models.organization
import rebase.models.manager

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
        from rebase.models.contractor import Contractor
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.last_seen = datetime.datetime.now()
        self.set_password(password)
        self.current_role = None

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def set_role(self, role):
        from rebase.models.contractor import Contractor
        if role:
            self.current_role = self.roles.filter_by(type=role).first()
        else:
            self.current_role = self.roles.first()
        if not self.current_role:
            # TODO raise instead when user doesn't have a role
            # we should first create a Role instance and then add the role as a param of the User __init__
            self.current_role = Contractor(self)
        return self.current_role

    @classmethod
    def query_by_user(cls, user, user_id=None):
        return cls.get_all(user)

    def filter_by_id(self, query):
        return query.filter(User.id==self.id)

    @classmethod
    def get_all(cls, user, another_user=None):
        return query_by_user_or_id(
            cls,
            lambda user: cls.as_manager(user).union(cls.as_contractor(user)).union(cls.as_user(user)),
            cls.filter_by_id,
            user, another_user
        )

    @classmethod
    def as_manager(cls, current_user, user_id=None):
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
    def as_manager_get_other_managers(cls, user, user_id=None):
        import rebase.models
        query = query_from_class_to_user(User, [
            rebase.models.manager.Manager,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)
        if user_id:
            query = query.filter(User.id==user_id)
        return query

    @classmethod
    def as_manager_get_cleared_contractors(cls, user, user_id=None):
        import rebase.models
        query = query_from_class_to_user(User, [
            rebase.models.contractor.Contractor,
            rebase.models.code_clearance.CodeClearance,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)
        if user_id:
            query = query.filter(User.id==user_id)
        return query

    @classmethod
    def as_manager_get_nominated_users(cls, user, user_id=None):
        import rebase.models
        query = query_from_class_to_user(User, [
            rebase.models.contractor.Contractor,
            rebase.models.nomination.Nomination,
            rebase.models.ticket_set.TicketSet,
            rebase.models.bid_limit.BidLimit,
            rebase.models.ticket_snapshot.TicketSnapshot,
            rebase.models.ticket.Ticket,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)
        if user_id:
            query = query.filter(User.id==user_id)
        return query

    @classmethod
    def as_contractor(cls, current_user, user_id=None):
        return cls.as_contractor_get_managers(current_user, user_id)\
            .union(cls.as_contractor_get_cleared_contractors(current_user, user_id))

    @classmethod
    def as_contractor_get_managers(cls, current_user, user_id=None):
        import rebase.models
        UserAlias = aliased(User)
        query = DB.session.query(UserAlias)\
            .select_from(User)\
            .join(rebase.models.contractor.Contractor)\
            .join(rebase.models.code_clearance.CodeClearance)\
            .join(rebase.models.project.Project)\
            .join(rebase.models.organization.Organization)\
            .join(rebase.models.manager.Manager)\
            .join(UserAlias)
        if user_id:
            query = query.filter(UserAlias.id == user_id)
        return query

    @classmethod
    def as_contractor_get_cleared_contractors(cls, current_user, user_id=None):
        import rebase.models
        UserAlias = aliased(User)
        CodeClearanceAlias = aliased(rebase.models.CodeClearance)
        ContractorAlias = aliased(rebase.models.Contractor)
        query = DB.session.query(UserAlias)\
            .select_from(User)\
            .join(rebase.models.contractor.Contractor)\
            .join(rebase.models.code_clearance.CodeClearance)\
            .join(rebase.models.project.Project)\
            .join(CodeClearanceAlias)\
            .join(ContractorAlias)\
            .join(UserAlias)
        if user_id:
            query = query.filter(UserAlias.id == user_id)
        return query

    @classmethod
    def as_user(cls, current_user, user_id=None):
        return cls.query.filter(cls.id==current_user.id)

    def allowed_to_be_created_by(self, user):
        return True

    def allowed_to_be_modified_by(self, user):
        if user.admin:
            return True
        return self.id == user.id

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_modified_by(user)

    def allowed_to_be_viewed_by(self, user):
        return self.query_by_user(user, self.id)

    # flask login helper functions
    def is_admin(self): return self.admin
    def is_authenticated(self): return True
    def is_active(self): return True
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)
    def get_role(self): return self.current_role

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

