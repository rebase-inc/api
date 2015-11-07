from flask import current_app

from rebase.common.database import make_collection_url, make_resource_url
from rebase.models import CodeClearance
from rebase.resources import RestfulResource, RestfulCollection
from rebase.git.users import generate_authorized_users
import rebase.views.code_clearance as code_clearance_views


def update_git_server_authorized_users(clearance):
    current_app.git_queue.enqueue(generate_authorized_users, clearance.project.id)
    return manager

resource_handlers = {
    'DELETE': {
        'pre_serialization': update_git_server_authorized_users
    },
}

collection_handlers = {
    'POST': {
        'pre_serialization': update_git_server_authorized_users
    },
}

CodeClearanceResource = RestfulResource(
    CodeClearance,
    code_clearance_views.serializer,
    code_clearance_views.deserializer,
    code_clearance_views.update_deserializer,
    handlers=resource_handlers
)

CodeClearanceCollection = RestfulCollection(
    CodeClearance,
    code_clearance_views.serializer,
    code_clearance_views.deserializer,
    handlers=collection_handlers
)


def add_code_clearance_resource(api):
    api.add_resource(CodeClearanceCollection, make_collection_url(CodeClearance), endpoint = CodeClearance.__pluralname__)
    api.add_resource(CodeClearanceResource, make_resource_url(CodeClearance), endpoint = CodeClearance.__pluralname__ + '_resource')
