
from flask.ext.login import current_user
from flask import session, current_app

from rebase.common.keys import make_collection_url, make_resource_url
from rebase.git.repo import Repo
from rebase.models import Project
from rebase.resources import RestfulResource, RestfulCollection
import rebase.views.project as project_views

def pick_a_new_role(response):
    if current_user.current_role.type == 'manager' and current_user.current_role.project.id == id:
        new_role = current_user.set_role(0)
        session['role_id']=new_role.id
        response.set_cookie('role_id', str(session['role_id']), **current_app.config['COOKIE_SECURE_HTTPPONLY'])
    return response

def on_new_project(project):
    repo = Repo(project)
    repo.create_internal_project_repo(project.managers[0].user)
    return project

project_resource_handlers = {
    'DELETE': {
        'modify_response': pick_a_new_role
    }
}

ProjectResource = RestfulResource(
    Project,
    project_views.serializer,
    project_views.deserializer,
    project_views.update_deserializer,
    handlers = project_resource_handlers
)

collection_handlers = {
    'POST': {
        'pre_serialization': on_new_project
    }
}

ProjectCollection = RestfulCollection(
    Project,
    project_views.serializer,
    project_views.deserializer,
    handlers = collection_handlers
)

def add_project_resource(api):
    api.add_resource(ProjectCollection, make_collection_url(Project), endpoint = Project.__pluralname__)
    api.add_resource(ProjectResource, make_resource_url(Project), endpoint = Project.__pluralname__ + '_resource')
