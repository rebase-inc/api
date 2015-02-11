from sqlalchemy.orm import validates

from .review import Review
from .debit import Debit
from .credit import Credit
from .mediation import Mediation
from .work_offer import WorkOffer
from alveare.common.database import DB

class Work(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)

    review =            DB.relationship('Review',    backref='work', uselist=False)
    debit =             DB.relationship('Debit',     backref='work', uselist=False)
    credit =            DB.relationship('Credit',    backref='work', uselist=False)
    offer =             DB.relationship('WorkOffer', backref='work', uselist=False)
    mediation_rounds =  DB.relationship('Mediation', backref='work', lazy='dynamic')

    def __init__(self, work_offer):
        self.offer = work_offer

    def start_mediation(self):
        self.mediation_rounds.append(Mediation())

    @validates('offer')
    def validate_work_offer(self, field, value):
        if not isinstance(value, WorkOffer):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, WorkOffer))
        return value


    def __repr__(self):
        return '<Work[{}] from Offer[{}]>'.format(self.id, self.offer.id)

