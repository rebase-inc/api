from marshmallow import fields, Schema
from alveare.models.github_account import GithubAccount
from alveare.models.remote_work_history import RemoteWorkHistory
from flask.ext.restful import abort

class GithubAccountSchema(Schema):
    id =                        fields.Integer()
    remote_work_history_id =    fields.Integer()
    user_name =                 fields.String()
    auth_token =                fields.String()

    def make_object(self, data):
        if 'id' in data.keys():
            account = GithubAccount.query.get_or_404(data['id'])
            for field, value in data.items():
                setattr(account, field, value)
            return account
        rwh = RemoteWorkHistory.query.get_or_404(data['remote_work_history_id'])
        account = GithubAccount(rwh, data['user_name'])
        if 'auth_token' in data.keys():
            account.auth_token = data['auth_token']
        return account

deserializer =          GithubAccountSchema(exclude=('id'))
update_deserializer =   GithubAccountSchema()
serializer =            GithubAccountSchema()
