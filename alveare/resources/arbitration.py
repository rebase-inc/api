from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import arbitration
from alveare.common.database import DB

class ArbitrationCollection(Resource):

    def get(self):
        all_arbitrations = models.Arbitration.query.limit(100).all()
        response = jsonify(arbitrations = arbitration.serializer.dump(all_arbitrations, many=True).data)
        return response

    def post(self):
        ''' admin only '''
        #raise Exception(request.form or request.json)
        new_arbitration = arbitration.deserializer.load(request.form or request.json).data
        DB.session.add(new_arbitration)
        DB.session.commit()

        response = jsonify(arbitration.serializer.dump(new_arbitration).data)
        response.status_code = 201
        return response

class ArbitrationResource(Resource):

    def get(self, id):
        single_arbitration = models.Arbitration.query.get_or_404(id)
        return jsonify(arbitration = arbitration.serializer.dump(single_arbitration).data)

    #def put(self, id):
        #single_mediation = models.Arbitration.query.get_or_404(id)

        #for field, value in mediation.updater.load(request.form or request.json).data.items():
            #setattr(single_mediation, field, value)
        #DB.session.commit()

        #return jsonify(mediation = mediation.serializer.dump(single_mediation).data)
