from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.models.internal_ticket import InternalTicket
from alveare.common.database import get_or_make_object, SecureNestedField

class InternalTicketSchema(AlveareSchema):
    id =            fields.Integer()
    title =         fields.String(required=True)
    description =   fields.String(required=True)
    discriminator = fields.String()

    project =           SecureNestedField('ProjectSchema',          only=('id',), allow_null=True)
    skill_requirement = SecureNestedField('SkillRequirementSchema', only=('id',), allow_null=True)
    snapshots =         SecureNestedField('TicketSnapshotSchema',   only=('id',), many=True)
    comments =          SecureNestedField('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        from alveare.models import InternalTicket
        return get_or_make_object(InternalTicket, data)

serializer =            InternalTicketSchema(skip_missing=True)
deserializer =          InternalTicketSchema(strict=True)
update_deserializer =   InternalTicketSchema()
update_deserializer.make_object = lambda data: data
