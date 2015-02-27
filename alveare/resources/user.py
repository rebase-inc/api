
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import user
from alveare.common.database import DB

class UserCollection(Resource):

    def get(self):
        all_users = models.User.query.all()
        response = jsonify(user.serializer.dump(all_users, many=True).data)
        return response

    def post(self):
        new_user = user.deserializer.load(request.form).data

        DB.session.add(new_user)
        DB.session.commit()

        response = jsonify(user.serializer.dump(new_user).data)
        response.status_code = 201
        return response

class UserResource(Resource):

    def get(self, id):
        single_user = models.User.query.get_or_404(id)
        return jsonify(user.serializer.dump(single_user).data)

    def put(self, id):
        single_user = models.User.query.get_or_404(id)

        for field, value in user.updater.load(request.form).data.items():
            setattr(single_user, field, value)
        DB.session.commit()

        return jsonify(user.serializer.dump(single_user).data)

    def delete(self, id):
        single_user = models.User.query.get(id)
        DB.session.delete(single_user)
        DB.session.commit()
        response = jsonify(message = 'User succesfully deleted')
        response.status_code = 200
        return response
