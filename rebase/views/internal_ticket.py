from marshmallow import fields, post_load, validate

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.internal_ticket import InternalTicket


class InternalTicketSchema(RebaseSchema):
    id =            fields.Integer()
    created =       fields.DateTime()
    title =         fields.String(required=True, validate=validate.Length(min=1, error='Please provide a title for this ticket'))
    discriminator = fields.String()
    first_comment = fields.String()

    project =           SecureNestedField('ProjectSchema',          only=('id','name','organization', 'work_repo', 'deploy', 'test', 'readme'), allow_null=True)
    skill_requirement = SecureNestedField('SkillRequirementSchema', only=('id','skills'), allow_null=True)
    snapshots =         SecureNestedField('TicketSnapshotSchema',   only=('id','bid_limit'), many=True)
    comments =          SecureNestedField('CommentSchema',          only=('id','content','user', 'created'), many=True)

    @post_load
    def make_internal_ticket(self, data):
        from rebase.models import InternalTicket
        return self._get_or_make_object(InternalTicket, data)


serializer =            InternalTicketSchema()
deserializer =          InternalTicketSchema(strict=True)
update_deserializer =   InternalTicketSchema(context={'raw': True})
