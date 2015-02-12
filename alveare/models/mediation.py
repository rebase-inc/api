from sqlalchemy.orm import validates

import datetime

from alveare.common.database import DB

class Mediation(DB.Model):
    id =            DB.Column(DB.Integer, primary_key=True)
    dev_answer =    DB.Column(DB.Integer, nullable=True)
    client_answer = DB.Column(DB.Integer, nullable=True)
    timeout =       DB.Column(DB.DateTime, nullable=False)
    work_id =       DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)

    arbitration =   DB.relationship('Arbitration', backref='mediation', uselist=False, cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, work, timeout = datetime.datetime.now() + datetime.timedelta(days=3)):
        self.work = work
        self.timeout = timeout

    def __repr__(self):
        return '<Mediation[id:{}] >'.format(self.id)

    @validates('work')
    def validate_work_offer(self, field, value):
        if not hasattr(value, 'offer'):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, 'Work type'))
        return value
