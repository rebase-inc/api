from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.models.github_ticket import GithubTicket
from alveare.common.database import get_or_make_object, SecureNestedField

class GithubTicketSchema(AlveareSchema):
    id =            fields.Integer()
    title =         fields.String()
    description =   fields.String()
    number =        fields.Integer()
    discriminator = fields.String()

    project =           SecureNestedField('ProjectSchema',          only=('id',), allow_null=True)
    skill_requirement = SecureNestedField('SkillRequirementSchema', only=('id',), allow_null=True)
    snapshots =         SecureNestedField('TicketSnapshotSchema',   only=('id',), many=True)
    comments =          SecureNestedField('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        from alveare.models import GithubTicket
        return get_or_make_object(GithubTicket, data)

serializer =            GithubTicketSchema(skip_missing=True)
deserializer =          GithubTicketSchema(strict=True)
update_deserializer =   GithubTicketSchema()
update_deserializer.make_object = lambda data: data
