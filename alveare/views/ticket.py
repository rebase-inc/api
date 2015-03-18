from marshmallow import fields, Schema
from alveare.models.ticket import Ticket
from alveare.views.skill_requirement import SkillRequirementSchema
from flask.ext.restful import abort
from alveare.common.database import get_or_make_object

class TicketSchema(Schema):
    id =            fields.Integer()
    title =         fields.String()
    description =   fields.String()

    project =           fields.Nested('ProjectSchema', only=('id',))
    skill_requirement = fields.Nested(SkillRequirementSchema,   only=('id',))
    snapshots =         fields.Nested('TicketSnapshotSchema',   only=('id',), many=True)
    comments =          fields.Nested('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        from alveare.models import Ticket
        return get_or_make_object(Ticket, data)


serializer =            TicketSchema()
deserializer =          TicketSchema(exclude=('id','project','skill_requirement','snapshots','comments'))
update_deserializer =   TicketSchema()
update_deserializer.make_object = lambda data: data
