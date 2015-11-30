from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema
from rebase.models.remote_ticket import RemoteTicket
from rebase.models.project import Project
from rebase.views.skill_requirement import SkillRequirementSchema
from rebase.common.database import get_or_make_object, SecureNestedField
from flask.ext.restful import abort

class RemoteTicketSchema(RebaseSchema):
    id =          fields.Integer(required=True)
    title =       fields.String()
    number =      fields.Integer()

    project =           SecureNestedField('ProjectSchema', only=('id',))
    skill_requirement = SecureNestedField(SkillRequirementSchema,  only=('id',))
    snapshots =         SecureNestedField('TicketSnapshotSchema',   only=('id',), many=True)
    comments =          SecureNestedField('CommentSchema',          only=('id',), many=True)

    @post_load
    def make_remote_ticket(self, data):
        from rebase.models import RemoteTicket
        return get_or_make_object(RemoteTicket, data)


serializer =            RemoteTicketSchema()
deserializer =          RemoteTicketSchema()
update_deserializer =   RemoteTicketSchema()
update_deserializer.make_object = lambda data: data
