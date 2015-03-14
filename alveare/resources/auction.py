from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from marshmallow.exceptions import UnmarshallingError

from alveare import models
from alveare.views import auction, auction
from alveare.common.database import DB
from alveare.common.state import ManagedState

class AuctionCollection(Resource):

    def get(self):
        all_auctions = models.Auction.query.limit(100).all()
        return jsonify(auctions = auction.serializer.dump(all_auctions, many=True).data)

    def post(self):
        new_auction = auction.deserializer.load(request.form or request.json).data

        DB.session.add(new_auction)
        DB.session.commit()

        response = jsonify(auction = auction.serializer.dump(new_auction).data)
        response.status_code = 201
        return response

class AuctionResource(Resource):
    def get(self, id):
        single_auction = models.Auction.query.get_or_404(id)
        return jsonify(auction = auction.serializer.dump(single_auction).data)

    def delete(self, id):
        auction = models.Auction.query.get_or_404(id)
        DB.session.delete(auction)
        DB.session.commit()
        response = jsonify(message = 'auction succesfully deleted')
        response.status_code = 200
        return response

    def put(self, id):
        single_auction = models.Auction.query.get_or_404(id)

        for field, value in user.updater.load(request.form).data.items():
            setattr(single_user, field, value)
        DB.session.commit()

        return jsonify(users = user.serializer.dump(single_user).data)

class AuctionBidEvents(Resource):

    def post(self, id):
        single_auction = models.Auction.query.get_or_404(id)
        auction_event = auction.bid_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction.serializer.dump(single_auction).data)
        response.status_code = 201
        return response

class AuctionEndEvents(Resource):

    def post(self, id):
        single_auction = models.Auction.query.get_or_404(id)
        auction_event = auction.end_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction.serializer.dump(single_auction).data)
        response.status_code = 201
        return response

class AuctionFailEvents(Resource):

    def post(self, id):
        single_auction = models.Auction.query.get_or_404(id)
        auction_event = auction.fail_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction.serializer.dump(single_auction).data)
        response.status_code = 201
        return response
