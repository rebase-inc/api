from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema
from rebase.models.ticket import Ticket
from rebase.common.database import get_or_make_object, SecureNestedField

class TicketSchema(RebaseSchema):
    id =            fields.Integer()
    created =       fields.DateTime()
    title =         fields.String()
    discriminator = fields.String()

    project =           SecureNestedField('ProjectSchema',          only=('id','name','organization', 'work_repo', 'deploy', 'test', 'readme'), allow_null=True)
    skill_requirement = SecureNestedField('SkillRequirementSchema', only=('id','skills'), allow_null=True)
    snapshots =         SecureNestedField('TicketSnapshotSchema',   only=('id','bid_limit'), many=True)
    comments =          SecureNestedField('CommentSchema',          only=('id','content','user', 'created'), many=True)

    @post_load
    def make_ticket(self, data):
        from rebase.models import Ticket
        return self._get_or_make_object(Ticket, data)

serializer =            TicketSchema()
deserializer =          TicketSchema(only=('id', 'title'), strict=True)
update_deserializer =   TicketSchema(context={'raw': True})
