
from alveare.common.database import DB

class RemoteTicket(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<RemoteTicket[id:{}]>'.format(self.id)

