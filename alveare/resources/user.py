
from flask.ext.restful import Resource
from marshmallow import fields, Schema
from flask import jsonify, make_response

from alveare import models

class UserCollection(Resource):

    def get(self):
        users = models.User.query.all()
        response = jsonify(users = userSchema.dump(users, many=True).data)
        return response

class User(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    hashed_password = fields.String()
    last_seen = fields.DateTime()

userSchema = User()

