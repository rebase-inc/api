from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.common.database import DB
from rebase.models.code_clearance import CodeClearance
from rebase.models.project import Project
from rebase.models.contractor import Contractor
from rebase.views.project import ProjectSchema
from rebase.views.contractor import ContractorSchema


class CodeClearanceSchema(RebaseSchema):
    id =           fields.Integer()
    pre_approved = fields.Boolean()
    project =      SecureNestedField('ProjectSchema', only=('id',), exclude=('code_clearance',), required=True)
    contractor =   SecureNestedField('ContractorSchema', only=('id',), exclude=('code_clearance',), required=True)

    @post_load
    def make_code_clearance(self, data):
        from rebase.models import CodeClearance
        return self._get_or_make_object(CodeClearance, data)


serializer = CodeClearanceSchema()
deserializer = CodeClearanceSchema(only=('pre_approved','project','contractor'), strict=True)
deserializer.declared_fields['project'].only = None
deserializer.declared_fields['contractor'].only = None
update_deserializer = CodeClearanceSchema(context={'raw': True})
