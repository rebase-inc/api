from flask import current_app

from rebase.common.keys import make_collection_url, make_resource_url
from rebase.models import Nomination
from rebase.resources import RestfulResource, RestfulCollection
from rebase.git.users import generate_authorized_users
import rebase.views.nomination as nomination_views


def update_git_server_authorized_users(nomination):
    current_app.git_queue.enqueue(generate_authorized_users, nomination.ticket_set.bid_limits[0].ticket_snapshot.ticket.project.id)
    return nomination

resource_handlers = {
    'PUT': {
        'pre_serialization': update_git_server_authorized_users
    },
}

NominationResource = RestfulResource(
    Nomination,
    nomination_views.serializer,
    nomination_views.deserializer,
    nomination_views.update_deserializer,
    handlers=resource_handlers
)

NominationCollection = RestfulCollection(
    Nomination,
    nomination_views.serializer,
    nomination_views.deserializer,
)


def add_nomination_resource(api):
    api.add_resource(NominationCollection, make_collection_url(Nomination), endpoint = Nomination.__pluralname__)
    api.add_resource(NominationResource, make_resource_url(Nomination), endpoint = Nomination.__pluralname__ + '_resource')
