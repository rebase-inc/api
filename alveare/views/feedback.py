from marshmallow import fields, Schema
from alveare.common.resource import get_or_make_object, update_object

class FeedbackSchema(Schema):
    id =         fields.Integer()
    auction =    fields.Nested('AuctionSchema', only=('id',))
    contractor = fields.Nested('ContractorSchema', only=('id',), required=True)
    message =    fields.String(required=True)

    def make_object(self, data):
        from alveare.models import Feedback
        return get_or_make_object(Feedback, data)

    def _update_object(self, data):
        from alveare.models import Feedback
        return update_object(Feedback, data)

serializer = FeedbackSchema(only=('id','auction', 'contractor', 'message'))
deserializer = FeedbackSchema(only=('auction', 'contractor', 'message'), strict=True)
update_deserializer = FeedbackSchema('message',)
update_deserializer.make_object = update_deserializer._update_object



