from marshmallow import fields, Schema

from alveare.views.review import ReviewSchema
from alveare.views.mediation import MediationSchema
from alveare.views.debit import DebitSchema
from alveare.views.credit import CreditSchema
from alveare.views.work_offer import WorkOfferSchema

# TODO: Figure out why this schema is sooooooooooooo slow
class WorkSchema(Schema):
    id = fields.Integer()
    state = fields.String()
    review = fields.Nested(ReviewSchema, exclude=['work'], default=None)
    mediation = fields.Nested(MediationSchema, only=('id','state'), attribute='mediation_rounds', many=True)
    debit = fields.Nested(DebitSchema, only='id', default=None)
    credit = fields.Nested(CreditSchema, only='id', default=None)
    offer = fields.Nested(WorkOfferSchema, only='id', default=None)

    def make_object(self, data):
        from alveare.models import Work
        if data.get('id'):
            work = Work.query.get(data.get('id'))
            if not work:
                raise ValueError('No work with id {id}'.format(**data))
            return work
        return Work(**data)

serializer = WorkSchema(only=('id','state','mediation','review','debit','credit','offer'), skip_missing=True)
