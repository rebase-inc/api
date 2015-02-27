from marshmallow import fields, Schema

from alveare.views import NamespacedSchema
from alveare.views.comment import CommentSchema

    #id =            DB.Column(DB.Integer, primary_key=True)
    #dev_answer =    DB.Column(DB.Integer, nullable=True)
    #client_answer = DB.Column(DB.Integer, nullable=True)
    #timeout =       DB.Column(DB.DateTime, nullable=False)
    #work_id =       DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)
    #state =         DB.Column(DB.String, nullable=False, default='discussion')

class MediationSchema(Schema):
    id = fields.Integer()
    dev_answer = fields.String()
    client_answer = fields.String()
    timeout = fields.DateTime()
    state = fields.String()
    work = fields.Nested('WorkSchema')

    def make_object(self, data):
        from alveare.models import Mediation
        return Mediation(**data)

#serializer = WorkSchema(only=('id','state','review','mediation'))

#deserializer = UserSchema(only=('first_name','last_name','email','password'))

#updater = UserSchema(only=('first_name','last_name','email','password'))
#updater.make_object = lambda data: data

