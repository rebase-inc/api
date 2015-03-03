from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import review
from alveare.common.database import DB

class ReviewCollection(Resource):

    def get(self):
        all_reviews = models.Review.query.all()
        response = jsonify(reviews = review.serializer.dump(all_reviews, many=True).data)
        return response

    def post(self):
        new_review = review.deserializer.load(request.form or request.json).data

        DB.session.add(new_review)
        DB.session.commit()

        response = jsonify(review.serializer.dump(new_review).data)
        response.status_code = 201
        return response

class ReviewResource(Resource):

    def get(self, id):
        single_review = models.Review.query.get_or_404(id)
        return jsonify(review = review.serializer.dump(single_review).data)

    def put(self, id):
        single_review = models.Review.query.get_or_404(id)

        for field, value in review.updater.load(request.form or request.json).data.items():
            setattr(single_review, field, value)
        DB.session.commit()

        return jsonify(review = review.serializer.dump(single_review).data)
