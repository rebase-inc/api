
from alveare.common.database import DB

class RemoteWorkHistory(DB.Model):

    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id'), primary_key=True, nullable=False)

    contractor = DB.relationship('Contractor', uselist=False, backref=DB.backref('remote_work_history', cascade='all, delete-orphan'))

    def __init__(self, contractor):
        self.contractor = contractor

    def __repr__(self):
        return '<RemoteWorkHistory[{}] >'.format(self.contractor_id)
