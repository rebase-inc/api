from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import auction, bid
from alveare.common.database import DB

class AuctionCollection(Resource):

    def get(self):
        all_auctions = models.Auction.query.limit(100).all()
        return jsonify(auctions = auction.serializer.dump(all_auctions, many=True).data)

    #def post(self):
        #new_bid = bid.deserializer.load(request.form or request.json).data
        #DB.session.add(new_bid)
        #DB.session.commit()

        #response = jsonify(bid = bid.serializer.dump(new_bid).data)
        #response.status_code = 201
        #return response

class AuctionResource(Resource):
    pass
    #def get(self, id):
        #single_bid = models.Bid.query.get_or_404(id)
        #return jsonify(bid = bid.serializer.dump(single_bid).data)

    #def delete(self, id):
        #bid = models.Bid.query.get_or_404(id)
        #DB.session.delete(bid)
        #DB.session.commit()
        #response = jsonify(message = 'Bid succesfully deleted')
        #response.status_code = 200
        #return response

    #def put(self, id):
        #single_user = models.Work.query.get_or_404(id)

        #for field, value in user.updater.load(request.form).data.items():
            #setattr(single_user, field, value)
        #DB.session.commit()

        #return jsonify(users = user.serializer.dump(single_user).data)
