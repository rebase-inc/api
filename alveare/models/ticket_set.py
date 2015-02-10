
from alveare.common.database import DB

class TicketSet(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    def __repr__(self):
        return '<Ticketset[id:{}]>'.format(self.id)

