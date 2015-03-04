from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import credit
from alveare.common.database import DB

class CreditCollection(Resource):

    def get(self):
        all_credits = models.Credit.query.limit(100).all()
        response = jsonify(credits = credit.serializer.dump(all_credits, many=True).data)
        return response

    def post(self):
        ''' admin only '''
        #raise Exception(request.form or request.json)
        new_credit = credit.deserializer.load(request.form or request.json).data
        DB.session.add(new_credit)
        DB.session.commit()

        response = jsonify(credit = credit.serializer.dump(new_credit).data)
        response.status_code = 201
        return response

class CreditResource(Resource):

    def get(self, id):
        single_credit = models.Credit.query.get_or_404(id)
        return jsonify(credit = credit.serializer.dump(single_credit).data)

    def put(self, id):
        single_credit = models.Credit.query.get_or_404(id)

        for field, value in credit.updater.load(request.form or request.json).data.items():
            setattr(single_credit, field, value)
        DB.session.commit()

        return jsonify(credit = credit.serializer.dump(single_credit).data)

    def delete(self, id):
        single_credit = models.Credit.query.get(id)
        DB.session.delete(single_credit)
        DB.session.commit()
        response = jsonify(message = 'Credit succesfully deleted')
        response.status_code = 200
        return response
