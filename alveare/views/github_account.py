from marshmallow import fields, Schema
from alveare.models.github_account import GithubAccount
from alveare.models.remote_work_history import RemoteWorkHistory
from flask.ext.restful import abort
from alveare.common.database import get_or_make_object

class GithubAccountSchema(Schema):
    id =                        fields.Integer()
    remote_work_history =       fields.Nested('RemoteWorkHistorySchema', only=('id',), required=True)
    user_name =                 fields.String(required=True)
    auth_token =                fields.String(required=True)

    def make_object(self, data):
        from alveare.models import GithubAccount
        return get_or_make_object(GithubAccount, data)

serializer =            GithubAccountSchema()
deserializer =          GithubAccountSchema(exclude=('id'), strict=True)
update_deserializer =   GithubAccountSchema()
update_deserializer.make_object = lambda data: data 
