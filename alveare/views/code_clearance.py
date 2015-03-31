from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import DB
from alveare.models.code_clearance import CodeClearance
from alveare.models.project import Project
from alveare.models.contractor import Contractor
from alveare.views.project import ProjectSchema
from alveare.views.contractor import ContractorSchema
from alveare.common.database import get_or_make_object, SecureNestedField

class CodeClearanceSchema(AlveareSchema):
    id =           fields.Integer()
    pre_approved = fields.Boolean()
    project =      SecureNestedField('ProjectSchema', only=('id',), exclude=('code_clearance',), required=True)
    contractor =   SecureNestedField('ContractorSchema', only=('id',), exclude=('code_clearance',), required=True)

    def make_object(self, data):
        from alveare.models import CodeClearance
        return get_or_make_object(CodeClearance, data)

serializer = CodeClearanceSchema(skip_missing=True)

deserializer = CodeClearanceSchema(only=('pre_approved','project','contractor'), strict=True)
deserializer.declared_fields['project'].only = None
deserializer.declared_fields['contractor'].only = None

update_deserializer = CodeClearanceSchema('message',)
update_deserializer.make_object = lambda data: data 
