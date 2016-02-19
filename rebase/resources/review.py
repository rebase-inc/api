from flask import current_app

from rebase.common.keys import make_collection_url, make_resource_url
from rebase.models.review import Review
from rebase.resources import RestfulResource, RestfulCollection
import rebase.views.review as review_views


ReviewResource = RestfulResource(
    Review,
    review_views.serializer,
    review_views.deserializer,
    review_views.update_deserializer,
)


ReviewCollection = RestfulCollection(
    Review,
    review_views.serializer,
    review_views.deserializer,
    cache=True
)


get_all_reviews = ReviewCollection.get_all


def add_review_resource(api):
    api.add_resource(ReviewCollection, make_collection_url(Review), endpoint = Review.__pluralname__)
    api.add_resource(ReviewResource, make_resource_url(Review), endpoint = Review.__pluralname__ + '_resource')


