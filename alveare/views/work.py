from marshmallow import fields, Schema

from alveare.views import NamespacedSchema
from alveare.views.review import ReviewSchema
from alveare.views.mediation import MediationSchema
from alveare.views.debit import DebitSchema
from alveare.views.credit import CreditSchema

class WorkSchema(Schema):
    id = fields.Integer()
    state = fields.String()
    review = fields.Nested(ReviewSchema, exclude=('work',))
    mediation = fields.Nested(MediationSchema, attribute='mediation_rounds', exclude=('work',), many=True)
    debit = fields.Nested(DebitSchema, only=('price',))
    credit = fields.Nested(CreditSchema, only=('price',))

    def make_object(self, data):
        from alveare.models import Work
        return Work(**data)

serializer = WorkSchema(only=('id','state','review','mediation'))
