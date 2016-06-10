import datetime
from logging import getLogger

from flask.ext.login import UserMixin
from sqlalchemy import and_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import aliased
from werkzeug.security import generate_password_hash, check_password_hash

from rebase.common.database import DB, PermissionMixin
from rebase.common.query import query_from_class_to_user


logger = getLogger()


class User(DB.Model, PermissionMixin, UserMixin):
    __pluralname__ = 'users'

    id =                DB.Column(DB.Integer,   primary_key=True)
    type =              DB.Column(DB.String)
    name =              DB.Column(DB.String,    nullable=False)
    email =             DB.Column(DB.String,    nullable=False, unique=True)
    hashed_password =   DB.Column(DB.String,    nullable=False)
    last_seen =         DB.Column(DB.DateTime,  nullable=False)
    roles =             DB.relationship('Role', backref='user', cascade='all, delete-orphan', passive_deletes=True)
    photo =             DB.relationship('Photo', backref='user', cascade="all, delete-orphan", passive_deletes=True, uselist=False)
    admin =             DB.Column(DB.Boolean,   nullable=False, default=False)
    github_accounts =   DB.relationship('GithubAccount', backref='user', cascade='all, delete-orphan', passive_deletes=True)
    ssh_public_keys =   DB.relationship('SSHKey', backref='user', cascade='all, delete-orphan', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __init__(self, name, email, password):
        from rebase.models.contractor import Contractor
        self.name = name
        self.email = email
        self.last_seen = datetime.datetime.now()
        self.set_password(password)
        self.current_role = None

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def set_role(self, role_id):
        from rebase.models.contractor import Contractor
        from rebase.models.role import Role
        role = Role.query.get(role_id)
        if role and role.user == self:
            self.current_role = role
        else:
            self.current_role = Role.query.filter(and_(Role.type=='manager', Role.user==self)).first()
            if not self.current_role:
                self.current_role = Role.query.filter(and_(Role.type=='contractor', Role.user==self)).first()
                if not self.current_role:
                    # TODO raise instead when user doesn't have a role
                    # we should first create a Role instance and then add the role as a param of the User __init__
                    self.current_role = Contractor(self)
        return self.current_role

    @classmethod
    def as_owner(cls, user):
        return cls.as_manager(user)

    @classmethod
    def as_contractor(cls, user):
        return cls.as_contractor_get_managers(user)\
            .union(cls.as_contractor_get_cleared_contractors(user))

    @classmethod
    def as_manager(cls, user):
        '''
        As a manager, there are 3 types of users you can read:
        - other managers in your project
        - cleared contractors for all projects in your project
        - nominated contractors for all projects in your project
        '''
        return cls.as_manager_get_other_managers(user)\
            .union(cls.as_manager_get_cleared_contractors(user))\
            .union(cls.as_manager_get_nominated_users(user))

    @classmethod
    def as_manager_get_other_managers(cls, user, user_id=None):
        import rebase.models
        query = query_from_class_to_user(User, [
            rebase.models.Manager,
            rebase.models.Project,
            rebase.models.Manager,
        ], user)
        if user_id:
            query = query.filter(User.id==user_id)
        return query

    @classmethod
    def as_manager_get_cleared_contractors(cls, user, user_id=None):
        import rebase.models
        query = query_from_class_to_user(User, [
            rebase.models.Contractor,
            rebase.models.CodeClearance,
            rebase.models.Project,
            rebase.models.Manager,
        ], user)
        if user_id:
            query = query.filter(User.id==user_id)
        return query

    @classmethod
    def as_manager_get_nominated_users(cls, user, user_id=None):
        import rebase.models
        query = query_from_class_to_user(User, [
            rebase.models.Contractor,
            rebase.models.Nomination,
            rebase.models.TicketSet,
            rebase.models.BidLimit,
            rebase.models.TicketSnapshot,
            rebase.models.Ticket,
            rebase.models.Project,
            rebase.models.Manager,
        ], user)
        if user_id:
            query = query.filter(User.id==user_id)
        return query

    @classmethod
    def as_contractor_get_managers(cls, current_user, user_id=None):
        import rebase.models
        UserAlias = aliased(User)
        query = DB.session.query(UserAlias)\
            .select_from(User)\
            .join(rebase.models.Contractor)\
            .join(rebase.models.CodeClearance)\
            .join(rebase.models.Project)\
            .join(rebase.models.Manager)\
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
            .join(rebase.models.Contractor)\
            .join(rebase.models.CodeClearance)\
            .join(rebase.models.Project)\
            .join(CodeClearanceAlias)\
            .join(ContractorAlias)\
            .join(UserAlias)
        if user_id:
            query = query.filter(UserAlias.id == user_id)
        return query

    def allowed_to_be_created_by(self, user):
        return True

    def allowed_to_be_modified_by(self, user):
        if user.admin:
            return True
        return self.id == user.id

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_modified_by(user)

    def allowed_to_be_viewed_by(self, user):
        return True

    def is_admin(self):
        return self.admin

    # flask login helper functions
    def get_id(self):
        return str(self.id)

    def get_role(self): return self.current_role

    @property
    def manager_roles(self):
        return filter(lambda role: role.type=='manager', self.roles)

    @property
    def contractor_roles(self):
        return filter(lambda role: role.type=='contractor', self.roles)

    @property
    def manager_for_projects(self):
        return [manager.project.id for manager in self.manager_roles]

    def __repr__(self):
        return '<User[id:{}] {} email={}>'.format(self.id, self.name, self.email)



