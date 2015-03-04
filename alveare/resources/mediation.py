from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import mediation
from alveare.common.database import DB

class MediationCollection(Resource):

    def get(self):
        all_mediations = models.Mediation.query.limit(100).all()
        response = jsonify(mediations = mediation.serializer.dump(all_mediations, many=True).data)
        return response

    def post(self):
        ''' admin only '''
        new_mediation = mediation.deserializer.load(request.form or request.json).data
        DB.session.add(new_mediation)
        DB.session.commit()

        response = jsonify(mediation = mediation.serializer.dump(new_mediation).data)
        response.status_code = 201
        return response

class MediationResource(Resource):

    def get(self, id):
        single_mediation = models.Mediation.query.get_or_404(id)
        return jsonify(mediation = mediation.serializer.dump(single_mediation).data)

    def put(self, id):
        single_mediation = models.Mediation.query.get_or_404(id)

        for field, value in mediation.updater.load(request.form or request.json).data.items():
            setattr(single_mediation, field, value)
        DB.session.commit()

        return jsonify(mediation = mediation.serializer.dump(single_mediation).data)
