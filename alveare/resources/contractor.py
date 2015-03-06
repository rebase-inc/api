from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import contractor
from alveare.common.database import DB

class ContractorCollection(Resource):

    def get(self):
        all_contractors = models.Contractor.query.limit(100).all()
        response = jsonify(contractors = contractor.serializer.dump(all_contractors, many=True).data)
        return response

    #def post(self):
        #new_contractor = contractor.deserializer.load(request.form or request.json).data
        #DB.session.add(new_contractor)
        #DB.session.commit()

        #response = jsonify(contractor = contractor.serializer.dump(new_contractor).data)
        #response.status_code = 201
        #return response

class ContractorResource(Resource):
    def get(self, id):
        single_contractor = models.Contractor.query.get_or_404(id)
        return jsonify(contractor = contractor.serializer.dump(single_contractor).data)

    def delete(self, id):
        contractor = models.Contractor.query.get_or_404(id)
        DB.session.delete(contractor)
        DB.session.commit()
        response = jsonify(message = 'Contractor succesfully deleted')
        response.status_code = 200
        return response

    #def put(self, id):
        #single_user = models.Work.query.get_or_404(id)

        #for field, value in user.updater.load(request.form).data.items():
            #setattr(single_user, field, value)
        #DB.session.commit()

        #return jsonify(users = user.serializer.dump(single_user).data)
