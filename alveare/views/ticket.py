from marshmallow import fields
from rebase.common.schema import AlveareSchema
from rebase.models.ticket import Ticket
from rebase.common.database import get_or_make_object, SecureNestedField

class TicketSchema(AlveareSchema):
    id =            fields.Integer()
    title =         fields.String(required=True)
    description =   fields.String(required=True)
    discriminator = fields.String()

    project =           SecureNestedField('ProjectSchema',          only=('id',), allow_null=True)
    skill_requirement = SecureNestedField('SkillRequirementSchema', only=('id',), allow_null=True)
    snapshots =         SecureNestedField('TicketSnapshotSchema',   only=('id',), many=True)
    comments =          SecureNestedField('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        from rebase.models import Ticket
        return get_or_make_object(Ticket, data)

serializer =            TicketSchema(skip_missing=True)
deserializer =          TicketSchema(strict=True)
update_deserializer =   TicketSchema()
update_deserializer.make_object = lambda data: data
