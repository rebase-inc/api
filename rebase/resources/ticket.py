from flask import current_app

from rebase.common.keys import make_collection_url, make_resource_url
from rebase.models.ticket import Ticket
from rebase.resources import RestfulResource, RestfulCollection
import rebase.views.ticket as ticket_views


TicketResource = RestfulResource(
    Ticket,
    ticket_views.serializer,
    ticket_views.deserializer,
    ticket_views.update_deserializer,
)


TicketCollection = RestfulCollection(
    Ticket,
    ticket_views.serializer,
    ticket_views.deserializer,
    cache=True
)


get_all_tickets = TicketCollection.get_all


def add_ticket_resource(api):
    api.add_resource(TicketCollection, make_collection_url(Ticket), endpoint = Ticket.__pluralname__)
    api.add_resource(TicketResource, make_resource_url(Ticket), endpoint = Ticket.__pluralname__ + '_resource')


