
from rebase.common.database import make_collection_url, make_resource_url
from rebase.models import SSHKey
from rebase.resources import RestfulResource, RestfulCollection
from rebase.git.keys import generate_authorized_keys
from rebase.git.queue import enqueue
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

class SSHKeyResource(BaseSSHKeyResource):
    put = enqueue(generate_authorized_keys)(BaseSSHKeyResource.put)
    delete = enqueue(generate_authorized_keys)(BaseSSHKeyResource.delete)


class SSHKeyCollection(BaseSSHKeyCollection):
    post = enqueue(generate_authorized_keys)(BaseSSHKeyCollection.post)


def add_ssh_key_resource(api):
    api.add_resource(SSHKeyCollection, make_collection_url(SSHKey), endpoint = SSHKey.__pluralname__)
    api.add_resource(SSHKeyResource, make_resource_url(SSHKey), endpoint = SSHKey.__pluralname__ + '_resource')
