
from flask.ext.restful import Resource
from marshmallow import fields, Schema
from flask import jsonify, make_response

from alveare import models
from alveare.views import user

class UserCollection(Resource):

    def get(self):
        users = models.User.query.all()
        response = jsonify(users = user.deserializer.dump(users, many=True).data)
        return response
