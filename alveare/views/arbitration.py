import datetime

from marshmallow import fields, Schema

from alveare.views import NamespacedSchema
from alveare.views.comment import CommentSchema

class ArbitrationSchema(Schema):
    id = fields.Integer()
    mediation = fields.Nested('MediationSchema', only='id', required=True)

    def make_object(self, data):
        ''' This is an admin only procedure '''
        from alveare.models import Mediation, Arbitration
        if data.get('id'):
            arbitration = Arbitration.query.get(data.get('id'))
            if not arbitration:
                raise ValueError('No arbitration with id {id}'.format(**data))
            return arbitration
        return Arbitration(data.get('mediation'))

serializer = ArbitrationSchema(only=('id','mediation'))
deserializer = ArbitrationSchema(only=('mediation',))

#updater = ArbitrationSchema(only=('state','timeout','dev_answer','client_answer'))
#updater.make_object = lambda data: data

