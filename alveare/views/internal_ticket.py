from marshmallow import fields, Schema
from alveare.models.internal_ticket import InternalTicket
from alveare.models.project import Project
from alveare.views.skill_requirements import SkillRequirementsSchema
from flask.ext.restful import abort

class InternalTicketSchema(Schema):
    id =            fields.Integer()
    title =         fields.String()
    description =   fields.String()
    project_id =    fields.Integer()

    skill_requirements =    fields.Nested(SkillRequirementsSchema,  only=('id',))
    snapshots =             fields.Nested('TicketSnapshotSchema',   only=('id',), many=True)
    comments =              fields.Nested('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        if data.get('id'):
            internal_ticket = InternalTicket.query.get_or_404(data['id'])
            data.pop('id')
            for field, value in data.items():
                setattr(internal_ticket, field, value)
            return internal_ticket
        project = Project.query.get_or_404(data['project_id'])
        new_internal_ticket = InternalTicket(project, data['title'], data['description'])
        return new_internal_ticket


deserializer =          InternalTicketSchema(exclude=('id', 'snapshots', 'skill_requirements'))
update_deserializer =   InternalTicketSchema()
serializer =            InternalTicketSchema()
