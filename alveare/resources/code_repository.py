
from flask.ext.restful import Resource, abort
from flask import jsonify
from alveare.models.code_repository import CodeRepository
from alveare.views.code_repository import serializer
from alveare.common.database import DB

class CodeRepositoryCollection(Resource):

    def get(self):
        code_repositories = CodeRepository.query.all()
        response = jsonify(code_repositories = serializer.dump(code_repositories, many=True).data)
        return response

class CodeRepositoryResource(Resource):

    def get(self, id):
        code_repository = CodeRepository.query.get_or_404(id)
        return jsonify(code_repository = serializer.dump(code_repository).data)
