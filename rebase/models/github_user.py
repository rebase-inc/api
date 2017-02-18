
from rebase.common.database import DB, PermissionMixin

FREE_SCANS = 5

class GithubUser(DB.Model, PermissionMixin):
    __pluralname__ = 'github_users'

    id =              DB.Column(DB.Integer, primary_key=True, unique=True)
    login =           DB.Column(DB.String, unique=True)
    name =            DB.Column(DB.String)
    email =           DB.Column(DB.String, nullable=True)
    scans_remaining = DB.Column(DB.Integer)
    out_of_date =     DB.Column(DB.Boolean, default = False)

    accounts =          DB.relationship('GithubAccount', backref='github_user', cascade="all, delete-orphan", passive_deletes=True)
    anonymous_user =    DB.relationship('GithubAnonymousUser', backref='github_user', uselist=False, cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, id, login, name, email=None):
        self.id = id
        self.login = login
        self.name = name
        self.email = email
        self.scans_remaining = FREE_SCANS

    def decrement_scans(self):
        if self.scans_remaining > 0:
            self.scans_remaining -= 1
        else:
            raise Exception('No scans left for user {}'.format(self.login))

    def __repr__(self):
        return '<GithubUser[id({}), login({}), name({})]>'.format(self.id, self.login, self.name)

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return True

    @classmethod
    def setup_queries(cls, models):
        cls.filter_based_on_current_role = False
        cls.as_manager_path = cls.as_owner_path = cls.as_contractor_path = []


