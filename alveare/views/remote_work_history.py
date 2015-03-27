from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.models.contractor import Contractor
from flask.ext.restful import abort
from alveare.common.database import get_or_make_object

class RemoteWorkHistorySchema(AlveareSchema):
    id =                fields.Integer()
    contractor = fields.Nested('ContractorSchema', only=('id'))
    github_accounts = fields.Nested('GithubAccountSchema', only=('id', 'user_name'), many=True)

    def make_object(self, data):
        from alveare.models import RemoteWorkHistory
        return get_or_make_object(RemoteWorkHistory, data)

serializer =            RemoteWorkHistorySchema(only=('id','github_accounts'))
deserializer =          RemoteWorkHistorySchema(only=('contractor',))
update_deserializer =   RemoteWorkHistorySchema()
