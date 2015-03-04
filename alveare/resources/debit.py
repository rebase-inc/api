from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import debit
from alveare.common.database import DB

class DebitCollection(Resource):

    def get(self):
        all_debits = models.Debit.query.limit(100).all()
        response = jsonify(debits = debit.serializer.dump(all_debits, many=True).data)
        return response

    def post(self):
        ''' admin only '''
        #raise Exception(request.form or request.json)
        new_debit = debit.deserializer.load(request.form or request.json).data
        DB.session.add(new_debit)
        DB.session.commit()

        response = jsonify(debit = debit.serializer.dump(new_debit).data)
        response.status_code = 201
        return response

class DebitResource(Resource):

    def get(self, id):
        single_debit = models.Debit.query.get_or_404(id)
        return jsonify(debit = debit.serializer.dump(single_debit).data)

    #def put(self, id):
        #single_mediation = models.Debit.query.get_or_404(id)

        #for field, value in mediation.updater.load(request.form or request.json).data.items():
            #setattr(single_mediation, field, value)
        #DB.session.commit()

        #return jsonify(mediation = mediation.serializer.dump(single_mediation).data)
