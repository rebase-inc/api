from marshmallow import fields
from rebase.common.schema import AlveareSchema
from rebase.models.code_repository import CodeRepository
from rebase.common.database import get_or_make_object, SecureNestedField

class CodeRepositorySchema(AlveareSchema):
    id =   fields.Integer()
    url =  fields.String()
    project = SecureNestedField('ProjectSchema', only=('id',), default=None)

    def make_object(self, data):
        from rebase.models import CodeRepository
        return get_or_make_object(CodeRepository, data)

serializer = CodeRepositorySchema()
deserializer = CodeRepositorySchema(only=tuple())
update_deserializer = CodeRepositorySchema()
update_deserializer.make_object = lambda data: data 

