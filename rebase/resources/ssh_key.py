from flask import current_app

from rebase.common.keys import make_collection_url, make_resource_url
from rebase.models import SSHKey
from rebase.resources import RestfulResource, RestfulCollection
from rebase.git.keys import generate_authorized_keys
import rebase.views.ssh_key as ssh_key_views


def update_keys(instance):
    current_app.git_queue.enqueue(generate_authorized_keys)
    return instance

resource_handlers = {
    'PUT': {
        'pre_serialization': update_keys
    },
    'DELETE': {
        'before_delete': update_keys
    },
}

collection_handlers = {
    'POST': {
        'pre_serialization': update_keys
    },
}

SSHKeyResource = RestfulResource(
    SSHKey,
    ssh_key_views.serializer,
    ssh_key_views.deserializer,
    ssh_key_views.update_deserializer,
    handlers=resource_handlers
)

SSHKeyCollection = RestfulCollection(
    SSHKey,
    ssh_key_views.serializer,
    ssh_key_views.deserializer,
    handlers=collection_handlers
)

def add_ssh_key_resource(api):
    api.add_resource(SSHKeyCollection, make_collection_url(SSHKey), endpoint = SSHKey.__pluralname__)
    api.add_resource(SSHKeyResource, make_resource_url(SSHKey), endpoint = SSHKey.__pluralname__ + '_resource')
