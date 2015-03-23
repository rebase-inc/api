from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.models.remote_ticket import RemoteTicket
from alveare.models.project import Project
from alveare.views.skill_requirement import SkillRequirementSchema
from flask.ext.restful import abort

class RemoteTicketSchema(AlveareSchema):
    id =          fields.Integer(required=True)
    title =       fields.String()
    description = fields.String()
    project =     fields.Nested('ProjectSchema', only=('id',))
    number =      fields.Integer()

    skill_requirement =    fields.Nested(SkillRequirementSchema,  only=('id',))
    snapshots =             fields.Nested('TicketSnapshotSchema',   only=('id',), many=True)
    comments =              fields.Nested('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        from alveare.models import RemoteTicket
        return get_or_make_object(RemoteTicket, data)


serializer =            RemoteTicketSchema()
deserializer =          RemoteTicketSchema(skip_missing=True)
update_deserializer =   RemoteTicketSchema()
update_deserializer.make_object = lambda data: data
