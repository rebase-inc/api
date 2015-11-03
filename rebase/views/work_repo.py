from os.path import join

from flask import current_app
from marshmallow import fields

from rebase.common.schema import RebaseSchema
from rebase.models.work_repo import WorkRepo
from rebase.common.database import get_or_make_object, SecureNestedField

class WorkRepoSchema(RebaseSchema):
    id =   fields.Integer()
    url =  fields.String()
    project = SecureNestedField('ProjectSchema', only=('id',), default=None)

    def make_object(self, data):
        from rebase.models import WorkRepo
        return get_or_make_object(WorkRepo, data)


@WorkRepoSchema.data_handler
def make_final_url(serializer, data, obj):
    repo_path = join(current_app.config['WORK_REPOS_ROOT'], data['url'])
    data['url'] = '{hostname}:{path}'.format(
        hostname=current_app.config['WORK_REPOS_HOST'],
        path=repo_path
    )
    return data

serializer = WorkRepoSchema()
deserializer = WorkRepoSchema(only=tuple())
update_deserializer = WorkRepoSchema()
update_deserializer.make_object = lambda data: data 

