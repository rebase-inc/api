
from alveare.common.database import DB

class GithubTicket(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    number = DB.Column(DB.Integer, nullable=False)

    def __init__(self, number):
        self.number = number

    def __repr__(self):
        return '<GithubTicket[id:{}] number={}>'.format(self.id, self.number)

