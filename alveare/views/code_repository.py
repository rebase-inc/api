from marshmallow import fields, Schema
from alveare.models.code_repository import CodeRepository
from alveare.common.database import get_or_make_object, update_object

class CodeRepositorySchema(Schema):
    id = fields.Integer()

    def make_object(self, data):
        from alveare.models import CodeRepository
        return get_or_make_object(CodeRepository, data)

serializer = CodeRepositorySchema()
deserializer = CodeRepositorySchema(only=tuple())
update_deserializer = CodeRepositorySchema()
update_deserializer.make_object = lambda data: data 

