
from alveare.common.database import DB

class GithubAccount(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    user_name = DB.Column(DB.String, nullable=False)

    def __init__(self, user_name):
        self.user_name = user_name

    def __repr__(self):
        return '<GithubAccount[id:{}] user_name={}>'.format(self.id, self.user_name)
