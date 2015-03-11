from marshmallow import fields, Schema
from alveare.models.github_ticket import GithubTicket
from alveare.models.project import Project
from alveare.views.skill_requirements import SkillRequirementsSchema
from flask.ext.restful import abort

class GithubTicketSchema(Schema):
    id =            fields.Integer()
    title =         fields.String()
    description =   fields.String()
    project_id =    fields.Integer()
    number =        fields.Integer()

    skill_requirements =    fields.Nested(SkillRequirementsSchema,  only=('id',))
    snapshots =             fields.Nested('TicketSnapshotSchema',   only=('id',), many=True)
    comments =              fields.Nested('CommentSchema',          only=('id',), many=True)

    def make_object(self, data):
        if data.get('id'):
            github_ticket = GithubTicket.query.get_or_404(data['id'])
            data.pop('id')
            for field, value in data.items():
                setattr(github_ticket, field, value)
            return github_ticket
        project = Project.query.get_or_404(data['project_id'])
        new_github_ticket = GithubTicket(project, data['number'])
        return new_github_ticket


deserializer =          GithubTicketSchema(skip_missing=True)
update_deserializer =   GithubTicketSchema()
serializer =            GithubTicketSchema()
