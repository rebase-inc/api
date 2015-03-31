from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.models.remote_ticket import RemoteTicket
from alveare.models.project import Project
from alveare.views.skill_requirement import SkillRequirementSchema
from alveare.common.database import get_or_make_object, SecureNestedField
from flask.ext.restful import abort

class RemoteTicketSchema(AlveareSchema):
    id =          fields.Integer(required=True)
    title =       fields.String()
    description = fields.String()
    number =      fields.Integer()

    project =           SecureNestedField('ProjectSchema', only=('id',))
    skill_requirement = SecureNestedField(SkillRequirementSchema,  only=('id',))
    snapshots =         SecureNestedField('TicketSnapshotSchema',   only=('id',), many=True)
    comments =          SecureNestedField('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        from alveare.models import RemoteTicket
        return get_or_make_object(RemoteTicket, data)


serializer =            RemoteTicketSchema()
deserializer =          RemoteTicketSchema(skip_missing=True)
update_deserializer =   RemoteTicketSchema()
update_deserializer.make_object = lambda data: data
