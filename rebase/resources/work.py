
from rebase.common.keys import make_collection_url, make_resource_url
from rebase.models.work import Work
from rebase.resources import RestfulResource, RestfulCollection, Event
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


class WorkEventResource(Event):
    model = Work
    serializer = work_views.serializer


class WorkHaltEvent(WorkEventResource):
    deserializer = work_views.halt_event_deserializer


class WorkReviewEvent(WorkEventResource):
    deserializer = work_views.review_event_deserializer


class WorkMediateEvent(WorkEventResource):
    deserializer = work_views.mediate_event_deserializer


class WorkCompleteEvent(WorkEventResource):
    deserializer = work_views.complete_event_deserializer


class WorkResolveEvent(WorkEventResource):
    deserializer = work_views.resolve_event_deserializer


class WorkFailEvent(WorkEventResource):
    deserializer = work_views.fail_event_deserializer


def add_work_resource(api):
    api.add_resource(WorkCollection, make_collection_url(Work), endpoint = Work.__pluralname__)
    api.add_resource(WorkResource, make_resource_url(Work), endpoint = Work.__pluralname__ + '_resource')
    api.add_resource(WorkHaltEvent,     '/works/<int:id>/halt')
    api.add_resource(WorkReviewEvent,   '/works/<int:id>/review')
    api.add_resource(WorkMediateEvent,  '/works/<int:id>/mediate')
    api.add_resource(WorkCompleteEvent, '/works/<int:id>/complete')
    api.add_resource(WorkResolveEvent,  '/works/<int:id>/resolve')
    api.add_resource(WorkFailEvent,     '/works/<int:id>/fail')


