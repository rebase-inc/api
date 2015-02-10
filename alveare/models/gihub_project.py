
from alveare.common.database import DB

class GithubProject(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<GithubProject[id:{}]>'.format(self.id)

