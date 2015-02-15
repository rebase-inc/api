
from alveare.common.database import DB

class GithubAccount(DB.Model):

    account_id =    DB.Column(DB.Integer, primary_key=True)
    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('remote_work_history.contractor_id', ondelete='CASCADE'))
    user_name =     DB.Column(DB.String, nullable=False)

    def __init__(self, remote_work_history, user_name):
        self.remote_work_history = remote_work_history
        self.user_name = user_name

    def __repr__(self):
        return '<GithubAccount[{}] user_name={}>'.format(self.contractor_id, self.user_name)
