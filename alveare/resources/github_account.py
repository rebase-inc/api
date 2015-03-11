
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare.models.github_account import GithubAccount
from alveare.views.github_account import serializer, deserializer, update_deserializer
from alveare.common.database import DB


class GithubAccountCollection(Resource):

    def get(self):
        github_accounts = GithubAccount.query.all()
        response = jsonify(github_accounts = serializer.dump(github_accounts, many=True).data)
        return response

    def post(self):
        new_account = deserializer.load(request.form or request.json).data

        DB.session.add(new_account)
        DB.session.commit()

        response = jsonify(github_account=serializer.dump(new_account).data)
        response.status_code = 201
        return response


class GithubAccountResource(Resource):

    def get(self, id):
        account = GithubAccount.query.get_or_404(id)
        return jsonify(github_account = serializer.dump(account).data)

    def put(self, id):
        updated_account = update_deserializer.load(request.form or request.json).data

        DB.session.add(updated_account)
        DB.session.commit()

        response = jsonify(github_account=serializer.dump(updated_account).data)
        response.status_code = 200
        return response

    def delete(self, id):
        DB.session.query(GithubAccount).filter_by(id=id).delete()
        DB.session.commit()

        response = jsonify(message = 'GithubAccount succesfully deleted')
        response.status_code = 200
        return response
