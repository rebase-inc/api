
from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema
from rebase.models.work_repo import WorkRepo
from rebase.common.database import get_or_make_object, SecureNestedField

class WorkRepoSchema(RebaseSchema):
    id =    fields.Integer()
    url =   fields.String()
    clone = fields.String()
    project = SecureNestedField('ProjectSchema', only=('id',), default=None)

    @post_load
    def make_work_repo(self, data):
        from rebase.models import WorkRepo
        return get_or_make_object(WorkRepo, data)


serializer = WorkRepoSchema()
deserializer = WorkRepoSchema(only=tuple())
update_deserializer = WorkRepoSchema()
update_deserializer.make_object = lambda data: data 

