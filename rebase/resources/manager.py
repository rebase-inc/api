from flask import current_app

from rebase.common.database import make_collection_url, make_resource_url
from rebase.models import Manager
from rebase.resources import RestfulResource, RestfulCollection
from rebase.git.queue import enqueue
from rebase.git.users import generate_authorized_users
import rebase.views.manager as manager_views


BaseManagerResource = RestfulResource(
    Manager,
    manager_views.serializer,
    manager_views.deserializer,
    manager_views.update_deserializer
)

BaseManagerCollection = RestfulCollection(
    Manager,
    manager_views.serializer,
    manager_views.deserializer,
)

class ManagerResource(BaseManagerResource):
    def put(self, id):
        return super().put(id=id)

    def delete(self, id):
        project_id = Manager.query.get_or_404(id).project.id
        response = super().delete(id)
        current_app.git_queue.enqueue(generate_authorized_users, project_id)
        return response


class ManagerCollection(BaseManagerCollection):
    def post(self):
        return super().post()


def add_manager_resource(api):
    api.add_resource(ManagerCollection, make_collection_url(Manager), endpoint = Manager.__pluralname__)
    api.add_resource(ManagerResource, make_resource_url(Manager), endpoint = Manager.__pluralname__ + '_resource')
