from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.models.github_ticket import GithubTicket
from rebase.common.database import get_or_make_object, SecureNestedField

class GithubTicketSchema(RebaseSchema):
    id =            fields.Integer()
    created =       fields.DateTime()
    title =         fields.String()
    discriminator = fields.String()
    number =        fields.Integer()

    project =           SecureNestedField('ProjectSchema',          only=('id','name','organization'), allow_null=True)
    skill_requirement = SecureNestedField('SkillRequirementSchema', only=('id','skills'), allow_null=True)
    snapshots =         SecureNestedField('TicketSnapshotSchema',   only=('id','bid_limit'), many=True)
    comments =          SecureNestedField('CommentSchema',          only=('id','content','user'), many=True)

    def make_object(self, data):
        from rebase.models import GithubTicket
        return get_or_make_object(GithubTicket, data)

serializer =            GithubTicketSchema(skip_missing=True)
deserializer =          GithubTicketSchema(strict=True)
update_deserializer =   GithubTicketSchema()
update_deserializer.make_object = lambda data: data
