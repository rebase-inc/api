from flask import current_app

from rebase.common.keys import make_collection_url, make_resource_url
from rebase.models.work import Work
from rebase.resources import RestfulResource, RestfulCollection
import rebase.views.work as work_views


WorkResource = RestfulResource(
    Work,
    work_views.serializer,
    work_views.deserializer,
    work_views.update_deserializer,
)


WorkCollection = RestfulCollection(
    Work,
    work_views.serializer,
    work_views.deserializer,
)


get_all_works = WorkCollection.get_all


def add_work_resource(api):
    api.add_resource(WorkCollection, make_collection_url(Work), endpoint = Work.__pluralname__)
    api.add_resource(WorkResource, make_resource_url(Work), endpoint = Work.__pluralname__ + '_resource')


