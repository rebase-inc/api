
from flask import current_app

from rebase.common.keys import make_collection_url, make_resource_url
from rebase.github.rq_jobs import save_comment
from rebase.models.comment import Comment
from rebase.resources import RestfulResource, RestfulCollection
import rebase.views.comment as comment_views


def enqueue_save_comment(new_comment):
    if new_comment.ticket and new_comment.ticket.discriminator == 'github_ticket':
        current_app.default_queue.enqueue(
            save_comment,
            new_comment.ticket.project.organization.accounts[0].account.id,
            new_comment.id
        )
    return new_comment


collection_handlers = {
    'POST': {
        'pre_serialization': enqueue_save_comment
    },
}


CommentResource = RestfulResource(
    Comment,
    comment_views.serializer,
    comment_views.deserializer,
    comment_views.update_deserializer,
)


CommentCollection = RestfulCollection(
    Comment,
    comment_views.serializer,
    comment_views.deserializer,
    handlers=collection_handlers
)


def add_comment_resource(api):
    api.add_resource(CommentCollection, make_collection_url(Comment), endpoint = Comment.__pluralname__)
    api.add_resource(CommentResource, make_resource_url(Comment), endpoint = Comment.__pluralname__ + '_resource')


