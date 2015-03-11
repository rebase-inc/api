from marshmallow import fields, Schema
from alveare.models.remote_ticket import RemoteTicket
from alveare.models.project import Project
from alveare.views.skill_requirement import SkillRequirementSchema
from flask.ext.restful import abort

class RemoteTicketSchema(Schema):
    id =            fields.Integer(required=True)
    title =         fields.String()
    description =   fields.String()
    project_id =    fields.Integer()
    number =        fields.Integer()

    skill_requirement =    fields.Nested(SkillRequirementSchema,  only=('id',))
    snapshots =             fields.Nested('TicketSnapshotSchema',   only=('id',), many=True)
    comments =              fields.Nested('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        remote_ticket = RemoteTicket.query.get_or_404(data['id'])
        data.pop('id')
        for field, value in data.items():
            setattr(remote_ticket, field, value)
        return remote_ticket


deserializer =          RemoteTicketSchema(skip_missing=True)
update_deserializer =   RemoteTicketSchema()
serializer =            RemoteTicketSchema()
