from marshmallow import fields, Schema
from alveare.models.ticket import Ticket
from alveare.views.skill_requirements import SkillRequirementSchema
from flask.ext.restful import abort

class TicketSchema(Schema):
    id =            fields.Integer()
    title =         fields.String()
    description =   fields.String()
    project_id =    fields.Integer()

    skill_requirement =     fields.Nested(SkillRequirementSchema,   only=('id',))
    snapshots =             fields.Nested('TicketSnapshotSchema',   only=('id',), many=True)
    comments =              fields.Nested('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        ticket = Ticket.query.get_or_404(data['id'])
        data.pop('id')
        for field, value in data.items():
            setattr(ticket, field, value)
        return ticket


deserializer =          TicketSchema(exclude=('id',))
update_deserializer =   TicketSchema()
serializer =            TicketSchema()
