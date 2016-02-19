from functools import wraps
from os.path import join
from pprint import pprint
from subprocess import check_call

from rebase.models import (
    Project,
    SSHKey,
    User
)


def build_query(permission_path, project_id):
    _query = User.query
    for path in reversed(permission_path):
        _query = _query.join(path)
    _query = _query.join(Project)
    return _query.filter_by(id=project_id)


def user_ids(project_id):
    all_manager_users = build_query(Project.as_manager_path, project_id)
    all_contractor_users = build_query(Project.as_contractor_path, project_id)
    all_owner_users = build_query(Project.as_owner_path, project_id)

    user_ids_as_tuple = all_manager_users.union(all_contractor_users).union(all_owner_users).with_entities(User.id).all()
    return map(lambda id_tuple: id_tuple[0], user_ids_as_tuple)

def make_authorized_users_file(project):
    project_id = project.id
    ids = user_ids(project_id)
    authorized_users_path = join(project.work_repo.full_repo_path, '.git', 'authorized_users')
    with open(authorized_users_path, 'w') as authorized_users:
        for user_id in ids:
            authorized_users.write(str(user_id)+'\n')

def generate_authorized_users(project_id):
    from rebase.app import create
    app, _, _ = create()
    project = Project.query.get(project_id)
    if not project:
        return 'Invalid project with id:'+str(project_id)
    make_authorized_users_file(project)

def generate_authorized_users_for_all_projects():
    from rebase.app import create
    app, _, _ = create()
    projects = Project.query.all()
    for project in projects:
        make_authorized_users_file(project)
