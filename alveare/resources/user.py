
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import user
from alveare.common.database import DB

class UserCollection(Resource):

    def get(self):
        all_users = models.User.query.all()
        response = jsonify(users = user.serializer.dump(all_users, many=True).data)
        return response

    def post(self):
        new_user = user.deserializer.load(request.form).data

        DB.session.add(new_user)
        DB.session.commit()

        response = jsonify(user = user.serializer.dump(new_user).data)
        response.status_code = 201
        return response

class UserResource(Resource):

    def get(self, id):
        single_user = models.User.query.get(id)
        return jsonify(user = user.serializer.dump(single_user).data)
