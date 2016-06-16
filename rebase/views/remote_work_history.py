from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.contractor import Contractor
from flask.ext.restful import abort

class RemoteWorkHistorySchema(RebaseSchema):
    id =              fields.Integer()
    analyzing =       fields.Boolean()
    contractor =      SecureNestedField('ContractorSchema', only=('id'))
    github_accounts = SecureNestedField('GithubAccountSchema', only=('app_id', 'github_user_id', 'user_id', 'github_user'), many=True)

    @post_load
    def make_remote_work_history(self, data):
        from rebase.models import RemoteWorkHistory
        return self._get_or_make_object(RemoteWorkHistory, data)

serializer =            RemoteWorkHistorySchema(only=('id','github_accounts'))
deserializer =          RemoteWorkHistorySchema(only=('contractor',))
update_deserializer =   RemoteWorkHistorySchema()
