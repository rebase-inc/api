from functools import wraps

from flask import current_app

from rebase.common.database import make_collection_url, make_resource_url
from rebase.models import SSHKey
from rebase.resources import RestfulResource, RestfulCollection
from rebase.git.keys import generate_authorized_keys
import rebase.views.ssh_key as ssh_key_views


BaseSSHKeyResource = RestfulResource(
    SSHKey,
    ssh_key_views.serializer,
    ssh_key_views.deserializer,
    ssh_key_views.update_deserializer
)

BaseSSHKeyCollection = RestfulCollection(
    SSHKey,
    ssh_key_views.serializer,
    ssh_key_views.deserializer,
)

def regenerate_git_server_authorized_keys(verb):
    @wraps(verb)
    def _trigger_rq_task(*args, **kwargs):
        response = verb(*args, **kwargs)
        current_app.git_queue.enqueue(generate_authorized_keys)
        return response
    return _trigger_rq_task

class SSHKeyResource(BaseSSHKeyResource):
    @regenerate_git_server_authorized_keys
    def put(self, id):
        return super().put(id)

    @regenerate_git_server_authorized_keys
    def delete(self, id):
        return super().delete(id)


class SSHKeyCollection(BaseSSHKeyCollection):
    @regenerate_git_server_authorized_keys
    def post(self):
        return super().post()


def add_ssh_key_resource(api):
    api.add_resource(SSHKeyCollection, make_collection_url(SSHKey), endpoint = SSHKey.__pluralname__)
    api.add_resource(SSHKeyResource, make_resource_url(SSHKey), endpoint = SSHKey.__pluralname__ + '_resource')
