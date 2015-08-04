from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.common.database import DB
from rebase.models.code_clearance import CodeClearance
from rebase.models.project import Project
from rebase.models.contractor import Contractor
from rebase.views.project import ProjectSchema
from rebase.views.contractor import ContractorSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class CodeClearanceSchema(RebaseSchema):
    id =           fields.Integer()
    pre_approved = fields.Boolean()
    project =      SecureNestedField('ProjectSchema', only=('id',), exclude=('code_clearance',), required=True)
    contractor =   SecureNestedField('ContractorSchema', only=('id',), exclude=('code_clearance',), required=True)

    def make_object(self, data):
        from rebase.models import CodeClearance
        return get_or_make_object(CodeClearance, data)

serializer = CodeClearanceSchema(skip_missing=True)

deserializer = CodeClearanceSchema(only=('pre_approved','project','contractor'), strict=True)
deserializer.declared_fields['project'].only = None
deserializer.declared_fields['contractor'].only = None

update_deserializer = CodeClearanceSchema('message',)
update_deserializer.make_object = lambda data: data 
