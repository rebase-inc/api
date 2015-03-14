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

    def _update_object(self, data):
        from alveare.models import Feedback
        feedback_id = data.get('id', None)
        if not feedback_id:
            raise ValueError('No feedback id provided!')
        feedback = Feedback.query.get(feedback_id)
        for key, value in data.items():
            setattr(feedback, key, value)
        return feedback

serializer = FeedbackSchema(only=('id','auction', 'contractor', 'message'))
deserializer = FeedbackSchema(only=('auction', 'contractor', 'message'), strict=True)
update_deserializer = FeedbackSchema('message',)
update_deserializer.make_object = update_deserializer._update_object



