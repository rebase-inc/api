from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.models.code_repository import CodeRepository
from alveare.common.database import get_or_make_object, SecureNestedField

class CodeRepositorySchema(AlveareSchema):
    id =   fields.Integer()
    url =  fields.String()
    project = SecureNestedField('ProjectSchema', only=('id',), default=None)

    def make_object(self, data):
        from alveare.models import CodeRepository
        return get_or_make_object(CodeRepository, data)

serializer = CodeRepositorySchema()
deserializer = CodeRepositorySchema(only=tuple())
update_deserializer = CodeRepositorySchema()
update_deserializer.make_object = lambda data: data 

