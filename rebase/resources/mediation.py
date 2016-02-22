
from rebase.common.keys import make_collection_url, make_resource_url
from rebase.models.mediation import Mediation
from rebase.resources import RestfulResource, RestfulCollection, Event
import rebase.views.mediation as mediation_views


MediationResource = RestfulResource(
    Mediation,
    mediation_views.serializer,
    mediation_views.deserializer,
    mediation_views.update_deserializer,
)


MediationCollection = RestfulCollection(
    Mediation,
    mediation_views.serializer,
    mediation_views.deserializer,
)


get_all_mediations = MediationCollection.get_all


class MediationEventResource(Event):
    model = Mediation
    serializer = mediation_views.serializer


class MediationDevAnswerEvent(MediationEventResource):
    deserializer = mediation_views.dev_answer_event_deserializer


class MediationClientAnswerEvent(MediationEventResource):
    deserializer = mediation_views.client_answer_event_deserializer


class MediationTimeoutEvent(MediationEventResource):
    deserializer = mediation_views.timeout_event_deserializer


class MediationTimeoutAnswerEvent(MediationEventResource):
    deserializer = mediation_views.timeout_answer_event_deserializer


class MediationAgreeEvent(MediationEventResource):
    deserializer = mediation_views.agree_event_deserializer


class MediationArbitrateEvent(MediationEventResource):
    deserializer = mediation_views.arbitrate_event_deserializer


def add_mediation_resource(api):
    api.add_resource(MediationCollection, make_collection_url(Mediation), endpoint = Mediation.__pluralname__)
    api.add_resource(MediationResource, make_resource_url(Mediation), endpoint = Mediation.__pluralname__ + '_resource')
    api.add_resource(MediationDevAnswerEvent,       '/mediations/<int:id>/dev_answer')
    api.add_resource(MediationClientAnswerEvent,    '/mediations/<int:id>/client_answer')
    api.add_resource(MediationTimeoutEvent,         '/mediations/<int:id>/timeout')
    api.add_resource(MediationTimeoutAnswerEvent,   '/mediations/<int:id>/timeout_answer')
    api.add_resource(MediationAgreeEvent,           '/mediations/<int:id>/agree')
    api.add_resource(MediationArbitrateEvent,       '/mediations/<int:id>/arbitrate')


