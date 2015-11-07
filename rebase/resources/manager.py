from flask import current_app

from rebase.common.database import make_collection_url, make_resource_url
from rebase.models import Manager
from rebase.resources import RestfulResource, RestfulCollection
from rebase.git.users import generate_authorized_users
import rebase.views.manager as manager_views


def update_git_server_authorized_users(manager):
    current_app.git_queue.enqueue(generate_authorized_users, manager.project.id)
    return manager

resource_handlers = {
    'DELETE': {
        'before_delete': update_git_server_authorized_users
    },
}

ManagerResource = RestfulResource(
    Manager,
    manager_views.serializer,
    manager_views.deserializer,
    manager_views.update_deserializer,
    handlers=resource_handlers
)

ManagerCollection = RestfulCollection(
    Manager,
    manager_views.serializer,
    manager_views.deserializer,
)


def add_manager_resource(api):
    api.add_resource(ManagerCollection, make_collection_url(Manager), endpoint = Manager.__pluralname__)
    api.add_resource(ManagerResource, make_resource_url(Manager), endpoint = Manager.__pluralname__ + '_resource')
