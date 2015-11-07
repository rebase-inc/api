from functools import wraps
from os.path import join
from pprint import pprint
from subprocess import check_call

from rebase.models import (
    Project,
    SSHKey,
    User
)


destination = 'git@{host}:{path}'.format

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

def generate_authorized_users(project_id):
    from rebase import create_app
    app, _, _ = create_app()
    project = Project.query.get(project_id)
    if not project:
        return 'Invalid project with id:'+str(project_id)
    ids = user_ids(project_id)
    tmp_authorized_users = '{path}_{suffix}'.format(path=app.config['TMP_AUTHORIZED_USERS'], suffix=str(project_id))
    with open(tmp_authorized_users, 'w') as authorized_users:
        for user_id in ids:
            authorized_users.write(str(user_id)+'\n')
    authorized_users_path = join(app.config['WORK_REPOS_ROOT'], project.work_repo.url, '.git', 'authorized_users')
    check_call(['scp', tmp_authorized_users, destination(host=app.config['WORK_REPOS_HOST'], path=authorized_users_path)])
