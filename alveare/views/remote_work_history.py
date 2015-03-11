from marshmallow import fields, Schema
from alveare.models.remote_work_history import RemoteWorkHistory
from alveare.models.contractor import Contractor
from flask.ext.restful import abort

class RemoteWorkHistorySchema(Schema):
    id =                fields.Integer()
    github_accounts =   fields.Nested('GithubAccountSchema', only=('id', 'user_name'), many=True)

    def make_object(self, data):
        rwh = RemoteWorkHistory.query.get(data['id'])
        if rwh:
            data.pop('id')
            for field, value in data:
                setattr(rwh, field, value)
            return rwh
        contractor = Contractor.query.get_or_404(data['id'])
        rwh = RemoteWorkHistory(contractor)
        return rwh

deserializer =          RemoteWorkHistorySchema()
update_deserializer =   RemoteWorkHistorySchema()
serializer =            RemoteWorkHistorySchema()
