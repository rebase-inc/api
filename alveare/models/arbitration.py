from sqlalchemy.orm import validates

from .mediation import Mediation

from alveare.common.database import DB, PermissionMixin

class Arbitration(DB.Model, PermissionMixin):
    __pluralname__ = 'arbitrations'

    id =            DB.Column(DB.Integer, primary_key=True)
    mediation_id =  DB.Column(DB.Integer, DB.ForeignKey('mediation.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, mediation):
        self.mediation = mediation

    def __repr__(self):
        return '<Arbitration[id:{}] for {}>'.format(self.id, self.mediation)

    @classmethod
    def query_by_user(cls, user):
        return cls.query

    def allowed_to_be_created_by(self, user):
        return True

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        return self.allowed_to_be_created_by(user)

    @validates('mediation')
    def validate_work_offer(self, field, value):
        if not isinstance(value, Mediation):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, Mediation))
        return value


