from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user
from flask import jsonify, make_response, request

from marshmallow.exceptions import UnmarshallingError

from alveare.models import Auction, Role
from alveare.views import auction
from alveare.common.database import DB
from alveare.common.state import ManagedState
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource

class AuctionCollection(Resource):
    model = Auction
    serializer = auction.serializer
    deserializer = auction.deserializer
    url = '/{}'.format(model.__pluralname__)

    @login_required
    def get(self):
        return get_collection(self.model, self.serializer, current_user.auction_query)

    @login_required
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

class AuctionResource(Resource):
    model = Auction
    serializer = auction.serializer
    deserializer = auction.deserializer
    update_deserializer = auction.update_deserializer
    url = '/{}/<int:id>'.format(model.__pluralname__)

    @login_required
    def get(self, id):
        return get_resource(self.model, id, self.serializer)

    @login_required
    def put(self, id):
        return update_resource(self.model, id, self.update_deserializer, self.serializer)

    @login_required
    def delete(self, id):
        return delete_resource(self.model, id)

class AuctionBidEvents(Resource):

    @login_required
    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = auction.bid_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction.serializer.dump(single_auction).data)
        response.status_code = 201
        return response

class AuctionEndEvents(Resource):

    @login_required
    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = auction.end_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction.serializer.dump(single_auction).data)
        response.status_code = 201
        return response

class AuctionFailEvents(Resource):

    @login_required
    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = auction.fail_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction.serializer.dump(single_auction).data)
        response.status_code = 201
        return response
