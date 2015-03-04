from marshmallow import fields, Schema
from alveare.models.code_repository import CodeRepository

class CodeRepositorySchema(Schema):
    id = fields.Integer()

serializer = CodeRepositorySchema(only=('id',))
