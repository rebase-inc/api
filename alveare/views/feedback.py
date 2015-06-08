from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import get_or_make_object, SecureNestedField

class FeedbackSchema(AlveareSchema):
    id =            fields.Integer()
    auction =       SecureNestedField('AuctionSchema', only=('id',))
    contractor =    SecureNestedField('ContractorSchema', only=('id',), required=True)
    comment =       SecureNestedField('CommentSchema', only=('id',), required=False)

    def make_object(self, data):
        from alveare.models import Feedback
        return get_or_make_object(Feedback, data)

serializer = FeedbackSchema(skip_missing=True)
deserializer = FeedbackSchema(strict=True)
update_deserializer = FeedbackSchema()
update_deserializer.make_object = lambda data: data 

