
from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema
from rebase.models.work_repo import WorkRepo
from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.models import WorkRepo

class WorkRepoSchema(RebaseSchema):
    model = WorkRepo

    id =    fields.Integer()
    url =   fields.String()
    clone = fields.String()
    project = SecureNestedField('ProjectSchema', only=('id',), default=None)

    @post_load
    def make_work_repo(self, data):
        self._get_or_make_object(data)

serializer = WorkRepoSchema()
deserializer = WorkRepoSchema(only=tuple()) # TODO: Use load_only/dump_only instead
update_deserializer = WorkRepoSchema(context={'raw': True})

