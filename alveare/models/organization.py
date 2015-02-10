
from alveare.common.database import DB

class Organization(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<Organization[id:{}]>'.format(self.id)

