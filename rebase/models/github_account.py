
from rebase.common.database import DB, PermissionMixin

class GithubAccount(DB.Model, PermissionMixin):
    __pluralname__ = 'github_accounts'

    id =            DB.Column(DB.Integer, primary_key=True)
    user_id =       DB.Column(DB.Integer, DB.ForeignKey('user.id', ondelete='CASCADE'))
    account_id =    DB.Column(DB.Integer, nullable=False)
    login =         DB.Column(DB.String, nullable=False)
    access_token =  DB.Column(DB.String, nullable=False)
    product =       DB.Column(DB.String, nullable=False) # product is either 'app' or 'code2resume'
    remote_work_history_id = DB.Column(DB.Integer, DB.ForeignKey('remote_work_history.id', ondelete='CASCADE'))

    orgs = DB.relationship('GithubOrgAccount', backref='account', cascade="all, delete-orphan", passive_deletes=True)
    contributed_repos = DB.relationship('GithubContributedRepo', backref='account', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, user, account_id, login, access_token, product):
        '''
        user: a User object
        login: Github login field from the authenticated user
        access_token: the secret OAuth token TODO: encrypt
        '''
        self.user = user
        self.account_id = account_id
        self.login = login
        self.access_token = access_token
        self.product = product

    def query_by_user(user):
        if user.is_admin():
            return GithubAccount.query
        return GithubAccount.query.filter(GithubAccount.user==user)

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return user.is_admin() or self.user == user

    def __repr__(self):
        return '<GithubAccount[{}]>'.format(self.id)

    @classmethod
    def setup_queries(cls, models):
        cls.as_contractor_path = cls.as_manager_path = []
