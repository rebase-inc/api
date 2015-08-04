from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.models.contractor import Contractor
from flask.ext.restful import abort
from rebase.common.database import get_or_make_object, SecureNestedField

class RemoteWorkHistorySchema(RebaseSchema):
    id =                fields.Integer()
    contractor = SecureNestedField('ContractorSchema', only=('id'))
    github_accounts = SecureNestedField('GithubAccountSchema', only=('id', 'user_name'), many=True)

    def make_object(self, data):
        from rebase.models import RemoteWorkHistory
        return get_or_make_object(RemoteWorkHistory, data)

serializer =            RemoteWorkHistorySchema(only=('id','github_accounts'))
deserializer =          RemoteWorkHistorySchema(only=('contractor',))
update_deserializer =   RemoteWorkHistorySchema()
