
from flask.ext.login import login_required, current_user
from flask import jsonify, request, session

from rebase.common.database import make_collection_url, make_resource_url
from rebase.common.rest import (
    delete_resource
)
from rebase.models import Project
from rebase.resources import RestfulResource, RestfulCollection
import rebase.views.project as project_views

BaseProjectResource = RestfulResource(
    Project,
    project_views.serializer,
    project_views.deserializer,
    project_views.update_deserializer
)

class ProjectResource(BaseProjectResource):
    @login_required
    def delete(self, id):
        def pick_a_new_role(response):
            if current_user.current_role.type == 'manager' and current_user.current_role.project.id == id:
                new_role = current_user.set_role(0)
                session['role_id']=new_role.id
            response.set_cookie('role_id', str(session['role_id']))
            return response
        return delete_resource(Project, id, modify_response=pick_a_new_role)

def add_project_resource(api):
    project_collection = RestfulCollection(Project, project_views.serializer, project_views.deserializer)
    api.add_resource(project_collection, make_collection_url(Project), endpoint = Project.__pluralname__)
    api.add_resource(ProjectResource, make_resource_url(Project), endpoint = Project.__pluralname__ + '_resource')
