
from rebase.common.database import make_collection_url, make_resource_url
from rebase.models import SSHKey
from rebase.resources import RestfulResource, RestfulCollection
import rebase.views.ssh_key as ssh_key_views


def add_ssh_key_resource(api):
    ssh_key_resource = RestfulResource(SSHKey, ssh_key_views.serializer, ssh_key_views.deserializer, ssh_key_views.update_deserializer)
    ssh_key_collection = RestfulCollection(SSHKey, ssh_key_views.serializer, ssh_key_views.deserializer)
    api.add_resource(ssh_key_collection, make_collection_url(SSHKey), endpoint = SSHKey.__pluralname__)
    api.add_resource(ssh_key_resource, make_resource_url(SSHKey), endpoint = SSHKey.__pluralname__ + '_resource')
