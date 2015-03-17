from sqlalchemy.orm import validates

from .mediation import Mediation

from alveare.common.database import DB

class Arbitration(DB.Model):
    __pluralname__ = 'arbitrations'

    id =            DB.Column(DB.Integer, primary_key=True)
    mediation_id =  DB.Column(DB.Integer, DB.ForeignKey('mediation.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, mediation):
        self.mediation = mediation

    def __repr__(self):
        return '<Arbitration[id:{}] for {}>'.format(self.id, self.mediation)

    @validates('mediation')
    def validate_work_offer(self, field, value):
        if not isinstance(value, Mediation):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, Mediation))
        return value


