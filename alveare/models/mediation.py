import datetime

from alveare.common.database import DB

class Mediation(DB.Model):
    id =            DB.Column(DB.Integer, primary_key=True)
    dev_answer =    DB.Column(DB.Integer, nullable=True)
    client_answer = DB.Column(DB.Integer, nullable=True)
    outcome =       DB.Column(DB.Integer, nullable=True)
    timeout =       DB.Column(DB.DateTime, nullable=False)
    work_id =       DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, work, timeout = datetime.datetime.now() + datetime.timedelta(days=3)):
        self.work = work
        self.timeout = timeout

    def __repr__(self):
        return '<Mediation[id:{}] >'.format(self.id)

