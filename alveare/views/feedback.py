from marshmallow import fields, Schema

class FeedbackSchema(Schema):
    id =         fields.Integer()
    auction =    fields.Nested('AuctionSchema', only=('id',))
    contractor = fields.Nested('ContractorSchema', only=('id',), required=True)
    message =    fields.String(required=True)

    def make_object(self, data):
        from alveare.models import Feedback
        if data.get('id'):
            feedback = Feedback.query.get(data.get('id'))
            if not feedback:
                raise ValueError('No feedback with id {id}'.format(**data))
            return feedback
        return Feedback(**data)

serializer = FeedbackSchema(only=('id','auction', 'contractor', 'message'))
deserializer = FeedbackSchema(only=('auction', 'contractor', 'message'), strict=True)
update_deserializer = FeedbackSchema('message',)
