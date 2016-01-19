from flask.ext.cache import Cache
from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user, current_app
from flask import jsonify, make_response, request

from rebase.models import Auction, Role
from rebase.views import auction as auction_views
from rebase.common.database import DB
from rebase.common.state import ManagedState
from rebase.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource


cache = Cache(
    current_app, 
    config = {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_HOST': current_app.config['REDIS_HOST']
    }
)

class AuctionCollection(Resource):
    model = Auction
    serializer = auction_views.serializer
    deserializer = auction_views.deserializer
    url = '/{}'.format(model.__pluralname__)

    @login_required
    def get(self):
        return get_collection(self.model, self.serializer, current_user)

    @login_required
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

class AuctionResource(Resource):
    model = Auction
    serializer = auction_views.serializer
    deserializer = auction_views.deserializer
    update_deserializer = auction_views.update_deserializer
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
        auction_event = auction_views.bid_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(*auction_event)

        DB.session.commit()

        response = jsonify(auction = auction_views.serializer.dump(single_auction).data)
        response.status_code = 201
        return response

class AuctionEndEvents(Resource):

    @login_required
    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = auction_views.end_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction_views.serializer.dump(single_auction).data)
        response.status_code = 201
        return response

class AuctionFailEvents(Resource):

    @login_required
    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = auction_views.fail_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction_views.serializer.dump(single_auction).data)
        response.status_code = 201
        return response
