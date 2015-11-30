from marshmallow import fields, post_load
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

    @post_load
    def make_github_ticket(self, data):
        from rebase.models import GithubTicket
        return get_or_make_object(GithubTicket, data)

serializer =            GithubTicketSchema()
deserializer =          GithubTicketSchema(strict=True)
update_deserializer =   GithubTicketSchema()
update_deserializer.make_object = lambda data: data
