from logging import warning

from flask import current_app

from rebase.common.keys import make_collection_url, make_resource_url
from rebase.models.comment import Comment
from rebase.resources import RestfulResource, RestfulCollection
import rebase.views.comment as comment_views


def push_to_github(account_id, comment_id):
    session = make_admin_github_session(account_id)
    new_comment = Comment.query.get(comment_id)
    if not new_comment:
        warning('There is no comment with id %d', comment_id)
    else:
        info('Push new comment to Github: %s', new_comment)
        #session.api.post(repo_url+'/repos/:owner/:repo/issues/:number/comments').data


def enqueue_push_to_github(new_comment):
    if new_comment.ticket and new_comment.ticket.discriminator == 'github_ticket':
        current_app.default_queue.enqueue(
            push_to_github,
            new_comment.ticket.project.organization.accounts[0].account.id,
            new_comment.id
        )
    return new_comment


collection_handlers = {
    'POST': {
        'pre_serialization': enqueue_push_to_github
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


