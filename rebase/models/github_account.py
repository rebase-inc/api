
from rebase.common.database import DB, PermissionMixin

class GithubAccount(DB.Model, PermissionMixin):
    __pluralname__ = 'github_accounts'

    id =            DB.Column(DB.Integer, primary_key=True)
    user_id =       DB.Column(DB.Integer, DB.ForeignKey('user.id', ondelete='CASCADE'))
    login =         DB.Column(DB.String, nullable=False)
    access_token =  DB.Column(DB.String, nullable=False)

    work_history =  DB.relationship('GithubRepository', lazy='dynamic', backref='work_history', cascade='all, delete-orphan', passive_deletes=True)
    managing =      DB.relationship('GithubRepository', lazy='dynamic', backref='managing', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, user, login, access_token):
        ''' 
        user: a User object
        login: Github login field from the authenticated user
        access_token: the secret OAuth token TODO: encrypt
        '''
        self.user = user
        self.login = login
        self.access_token = access_token

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
