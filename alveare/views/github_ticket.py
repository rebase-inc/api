from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.models.github_ticket import GithubTicket
from alveare.models.project import Project
from alveare.views.skill_requirement import SkillRequirementSchema
from flask.ext.restful import abort
from alveare.common.database import get_or_make_object

class GithubTicketSchema(AlveareSchema):
    id =          fields.Integer()
    title =       fields.String()
    description = fields.String()
    project =     fields.Nested('ProjectSchema', only=('id',))
    number =      fields.Integer()

    skill_requirement =    fields.Nested(SkillRequirementSchema,  only=('id',))
    snapshots =             fields.Nested('TicketSnapshotSchema',   only=('id',), many=True)
    comments =              fields.Nested('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        from alveare.models import GithubTicket
        return get_or_make_object(GithubTicket, data) 

serializer =            GithubTicketSchema()
deserializer =          GithubTicketSchema()
update_deserializer =   GithubTicketSchema()
update_deserializer.make_object = lambda data: data 
