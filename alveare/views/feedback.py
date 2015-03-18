from marshmallow import fields, Schema
from alveare.common.database import get_or_make_object

class FeedbackSchema(Schema):
    id =         fields.Integer()
    auction =    fields.Nested('AuctionSchema', only=('id',))
    contractor = fields.Nested('ContractorSchema', only=('id',), required=True)
    message =    fields.String(required=True)

    def make_object(self, data):
        from alveare.models import Feedback
        return get_or_make_object(Feedback, data)

serializer = FeedbackSchema(only=('id','auction', 'contractor', 'message'))
deserializer = FeedbackSchema(only=('auction', 'contractor', 'message'), strict=True)
update_deserializer = FeedbackSchema()
update_deserializer.make_object = lambda data: data 

