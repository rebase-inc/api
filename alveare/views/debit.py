

from marshmallow import fields, Schema

from alveare.views import NamespacedSchema

class DebitSchema(Schema):
    id = fields.Integer()
    work = fields.Nested('WorkSchema', only='id')
    price = fields.Integer()
    paid = fields.Boolean()

    def make_object(self, data):
        from alveare.models import Debit
        return Debit(**data)