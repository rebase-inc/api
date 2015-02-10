
from alveare.common.database import DB

class Auction(DB.Model):

    id =                DB.Column(DB.Integer,   primary_key=True)
    duration =          DB.Column(DB.DateTime,  nullable=False)
    finish_work_by =    DB.Column(DB.DateTime,  nullable=False)
    redundancy =        DB.Column(DB.Integer,   nullable=False)

    def __init__(self, duration, finish_work_by, redundancy):
        self.duration = duration
        self.finish_work_by = finish_work_by
        self.redundancy = redundancy

    def __repr__(self):
        return '<Auction[id:{}] finish_work_by={}>'.format(self.id, self.finish_work_by)
