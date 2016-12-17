
from rebase.common.keys import make_collection_url, make_resource_url
from rebase.models import Auction
from rebase.resources import RestfulResource, RestfulCollection, Event
from rebase.views import auction as auction_views


AuctionResource = RestfulResource(
    Auction,
    auction_views.serializer,
    auction_views.deserializer,
    auction_views.update_deserializer,
)


AuctionCollection = RestfulCollection(
    Auction,
    auction_views.serializer,
    auction_views.deserializer,
    cache=True
)


get_all_auctions = AuctionCollection.get_all


class AuctionEvent(Event):
    model = Auction
    serializer = auction_views.serializer


class AuctionBidEvent(AuctionEvent):
    deserializer = auction_views.bid_event_deserializer


class AuctionEndEvent(AuctionEvent):
    deserializer = auction_views.end_event_deserializer


class AuctionFailEvent(AuctionEvent):
    deserializer = auction_views.fail_event_deserializer


def add_auction_resource(api):
    api.add_resource(AuctionCollection, make_collection_url(Auction), endpoint = Auction.__pluralname__)
    api.add_resource(AuctionResource, make_resource_url(Auction), endpoint = Auction.__pluralname__ + '_resource')
    api.add_resource(AuctionBidEvent,   '/auctions/<int:id>/bid')
    api.add_resource(AuctionEndEvent,   '/auctions/<int:id>/end')
    api.add_resource(AuctionFailEvent,  '/auctions/<int:id>/fail')


