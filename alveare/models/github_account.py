
from alveare.common.database import DB, PermissionMixin

class GithubAccount(DB.Model, PermissionMixin):
    __pluralname__ = 'github_accounts'

    id =                        DB.Column(DB.Integer, primary_key=True)
    remote_work_history_id =    DB.Column(DB.Integer, DB.ForeignKey('remote_work_history.id', ondelete='CASCADE'))
    user_name =                 DB.Column(DB.String, nullable=False)
    auth_token =                DB.Column(DB.String)

    def __init__(self, remote_work_history, user_name, auth_token=None):
        self.remote_work_history = remote_work_history
        self.user_name = user_name
        self.auth_token = auth_token

    @classmethod
    def query_by_user(cls, user):
        return cls.query

    def allowed_to_be_created_by(self, user):
        return True

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        return self.allowed_to_be_created_by(user)


    def __repr__(self):
        return '<GithubAccount[{}] user_name={}>'.format(self.contractor_id, self.user_name)
