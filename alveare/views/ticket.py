from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.models.ticket import Ticket
from alveare.views.skill_requirement import SkillRequirementSchema
from flask.ext.restful import abort
from alveare.common.database import get_or_make_object, SecureNestedField

class TicketSchema(AlveareSchema):
    id =            fields.Integer()
    title =         fields.String()
    description =   fields.String()

    project =           SecureNestedField('ProjectSchema', only=('id',))
    skill_requirement = SecureNestedField(SkillRequirementSchema,   only=('id',))
    snapshots =         SecureNestedField('TicketSnapshotSchema',   only=('id',), many=True)
    comments =          SecureNestedField('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        from alveare.models import Ticket
        return get_or_make_object(Ticket, data)


serializer =            TicketSchema()
deserializer =          TicketSchema(exclude=('id','project','skill_requirement','snapshots','comments'))
update_deserializer =   TicketSchema()
update_deserializer.make_object = lambda data: data
