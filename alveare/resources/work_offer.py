
from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import work_offer
from alveare.common.database import DB

class WorkOfferCollection(Resource):

    @login_required
    def get(self):
        all_work_offers = models.WorkOffer.query.limit(100).all()
        response = jsonify(work_offers = work_offer.serializer.dump(all_work_offers, many=True).data)
        return response

    @login_required
    def post(self):
        new_work_offer = work_offer.deserializer.load(request.form or request.json).data
        DB.session.add(new_work_offer)
        DB.session.commit()

        response = jsonify(work_offer = work_offer.serializer.dump(new_work_offer).data)
        response.status_code = 201
        return response

class WorkOfferResource(Resource):

    @login_required
    def get(self, id):
        single_work_offer = models.WorkOffer.query.get_or_404(id)
        return jsonify(work_offer = work_offer.serializer.dump(single_work_offer).data)

    @login_required
    def put(self, id):
        single_work_offer = models.WorkOffer.query.get_or_404(id)

        for field, value in work_offer.updater.load(request.form or request.json).data.items():
            setattr(single_work_offer, field, value)
        DB.session.commit()

        return jsonify(work_offer = work_offer.serializer.dump(single_work_offer).data)

    @login_required
    def delete(self, id):
        single_work_offer = models.WorkOffer.query.get(id)
        DB.session.delete(single_work_offer)
        DB.session.commit()
        response = jsonify(message = 'Work offer succesfully deleted')
        response.status_code = 200
        return response
