
from rebase.common.database import DB, PermissionMixin

# this model isn't really a github account. It's more of a Github app authorization
class GithubAccount(DB.Model, PermissionMixin):
    __pluralname__ = 'github_accounts'

    app_id =                DB.Column(DB.String,    DB.ForeignKey('github_o_auth_app.client_id', ondelete='CASCADE'),   primary_key=True)
    github_user_id =        DB.Column(DB.Integer,   DB.ForeignKey('github_user.id', ondelete='CASCADE'),                primary_key=True)
    user_id =               DB.Column(DB.Integer,   DB.ForeignKey('user.id', ondelete='CASCADE'),                       primary_key=True)

    access_token =          DB.Column(DB.String, nullable=False)
    remote_work_history_id =DB.Column(DB.Integer, DB.ForeignKey('remote_work_history.id', ondelete='CASCADE'))

    orgs =                  DB.relationship('GithubOrgAccount', backref='account', cascade="all, delete-orphan", passive_deletes=True)
    contributed_repos =     DB.relationship('GithubContributedRepo', backref='account', cascade="all, delete-orphan", passive_deletes=True)

    filter_based_on_current_role = False

    def __init__(self, github_oauth_app, github_user, user, access_token):
        '''
        access_token: the secret OAuth token
        TODO: encrypt access_token
        '''
        self.app = github_oauth_app
        self.github_user = github_user
        self.user = user
        self.access_token = access_token

    @property
    def id(self):
        return (self.app_id, self.github_user_id, self.user_id)

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return user.is_admin() or self.user == user

    def __repr__(self):
        return '<GithubAccount[{}]>'.format((self.app_id, self.github_user_id, self.user_id))

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = cls.as_contractor_path = cls.as_manager_path = []


