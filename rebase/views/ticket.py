from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.models.ticket import Ticket
from rebase.common.database import get_or_make_object, SecureNestedField

class TicketSchema(RebaseSchema):
    id =            fields.Integer()
    created =       fields.DateTime()
    title =         fields.String()
    discriminator = fields.String()

    project =           SecureNestedField('ProjectSchema',          only=('id','name','organization'), allow_null=True)
    skill_requirement = SecureNestedField('SkillRequirementSchema', only=('id','skills'), allow_null=True)
    snapshots =         SecureNestedField('TicketSnapshotSchema',   only=('id','bid_limit'), many=True)
    comments =          SecureNestedField('CommentSchema',          only=('id','content','user'), many=True)

    def make_object(self, data):
        from rebase.models import Ticket
        return get_or_make_object(Ticket, data)

serializer =            TicketSchema(skip_missing=True)
deserializer =          TicketSchema(only=('id', 'title'), skip_missing=True, strict=True)
update_deserializer =   TicketSchema()
update_deserializer.make_object = lambda data: data
