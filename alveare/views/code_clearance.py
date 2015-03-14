from marshmallow import fields, Schema
from alveare.common.database import DB
from alveare.models.code_clearance import CodeClearance
from alveare.models.project import Project
from alveare.models.contractor import Contractor
from alveare.views.project import ProjectSchema
from alveare.views.contractor import ContractorSchema
from alveare.common.resource import get_or_make_object, update_object

class CodeClearanceSchema(Schema):
    id =           fields.Integer()
    pre_approved = fields.Boolean()
    project =      fields.Nested('ProjectSchema', only=('id', 'name'), exclude=('code_clearance',), required=True)
    contractor =   fields.Nested('ContractorSchema', only=('id',), exclude=('code_clearance',), required=True)

    def make_object(self, data):
        from alveare.models import CodeClearance
        return get_or_make_object(CodeClearance, data)

    def _update_object(self, data):
        from alveare.models import CodeClearance
        return update_object(CodeClearance, data)

serializer = CodeClearanceSchema(skip_missing=True)

deserializer = CodeClearanceSchema(only=('pre_approved','project','contractor'), strict=True)
deserializer.declared_fields['project'].only = None
deserializer.declared_fields['contractor'].only = None

update_deserializer = CodeClearanceSchema('message',)
update_deserializer.make_object = update_deserializer._update_object