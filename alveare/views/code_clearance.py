from marshmallow import fields, Schema
from alveare.common.database import DB
from alveare.models.code_clearance import CodeClearance
from alveare.models.project import Project
from alveare.models.contractor import Contractor

class CodeClearanceSchema(Schema):
    id =                fields.Integer()
    pre_approved =      fields.Boolean()
    project_id =        fields.Integer(required=True)
    contractor_id =     fields.Integer(required=True)
    project =           fields.Nested('ProjectSchema', only=('id', 'name'))

    def make_object(self, data):
        if data.get('id'):
            # an id is provided, so we're doing an update
            code_clearance = CodeClearance.query.get_or_404(data['id'])
            for field, value in data.items():
                setattr(code_clearance, field, value)
            return code_clearance
        project = Project.query.get_or_404(data['project_id'])
        contractor = Contractor.query.get_or_404(data['contractor_id'])
        code_clearance = CodeClearance(project, contractor, data['pre_approved'])
        return code_clearance

serializer = CodeClearanceSchema()
deserializer = CodeClearanceSchema(skip_missing=True)
update_deserializer = CodeClearanceSchema()
