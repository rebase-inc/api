
from alveare.common.database import DB

class GithubAccount(DB.Model):
    __pluralname__ = 'github_accounts'

    id =                        DB.Column(DB.Integer, primary_key=True)
    remote_work_history_id =    DB.Column(DB.Integer, DB.ForeignKey('remote_work_history.id', ondelete='CASCADE'))
    user_name =                 DB.Column(DB.String, nullable=False)
    auth_token =                DB.Column(DB.String)

    def __init__(self, remote_work_history, user_name, auth_token=None):
        self.remote_work_history = remote_work_history
        self.user_name = user_name
        self.auth_token = auth_token


    def __repr__(self):
        return '<GithubAccount[{}] user_name={}>'.format(self.contractor_id, self.user_name)
