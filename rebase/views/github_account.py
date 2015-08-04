from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.models.github_account import GithubAccount
from rebase.models.remote_work_history import RemoteWorkHistory
from flask.ext.restful import abort
from rebase.common.database import get_or_make_object, SecureNestedField

class GithubAccountSchema(RebaseSchema):
    id =                        fields.Integer()
    user_name =                 fields.String(required=True)
    auth_token =                fields.String(required=True)
    remote_work_history =       SecureNestedField('RemoteWorkHistorySchema', only=('id',), required=True)

    def make_object(self, data):
        from rebase.models import GithubAccount
        return get_or_make_object(GithubAccount, data)

serializer =            GithubAccountSchema()
deserializer =          GithubAccountSchema(exclude=('id'), strict=True)
update_deserializer =   GithubAccountSchema()
update_deserializer.make_object = lambda data: data
