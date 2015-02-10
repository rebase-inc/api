
from alveare.common.database import DB

class RemoteProject(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<RemoteProject[id:{}]>'.format(self.id)

