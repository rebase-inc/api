
from marshmallow import fields, Schema

class CreditSchema(Schema):
    id = fields.Integer()
    work = fields.Nested('WorkSchema', only='id')
    price = fields.Integer()
    paid = fields.Boolean()

    def make_object(self, data):
        from alveare.models import Credit
        return Credit(**data)
