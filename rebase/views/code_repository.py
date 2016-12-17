from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.code_repository import CodeRepository


class CodeRepositorySchema(RebaseSchema):
    id =   fields.Integer()
    url =  fields.String()

    @post_load
    def make_code_repository(self, data):
        from rebase.models import CodeRepository
        return self._get_or_make_object(CodeRepository, data)


serializer = CodeRepositorySchema()
deserializer = CodeRepositorySchema(only=tuple())
update_deserializer = CodeRepositorySchema(context={'raw': True})
