from marshmallow import Schema
from rebase.common.exceptions import marshmallow_exceptions

class RebaseSchema(Schema):

    def load(self, *args, **kwargs):
        with marshmallow_exceptions(args[0]):
            return super().load(*args, **kwargs)

    def dump(self, *args, **kwargs):
        with marshmallow_exceptions(args[0]):
            return super().dump(*args, **kwargs)
