
from alveare.common.database import DB

class TicketSnapshot(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    date = DB.Column(DB.DateTime, nullable=False)

    def __init__(self, date):
        self.date = date

    def __repr__(self):
	    return '<TicketSnapshot[id:{}] date: {}>'.format(self.id, self.date)
