from os.path import join

from flask import current_app

from rebase.common.ssh import SSH
from rebase.models.internal_project import InternalProject


def _create_branch(repo_path, branch):
    from rebase import create_app
    app, _, __ = create_app()
    ssh = SSH('git', app.config['WORK_REPOS_HOST'])
    ssh(['git', '-C', repo_path, 'branch', branch])

def _create_internal_project_repo(project_id):
    from rebase import create_app
    app, _, __ = create_app()
    ssh = SSH('git', app.config['WORK_REPOS_HOST'])
    project = InternalProject.query.get(project_id)
    if not project:
        return 'Unknow project with id: {}'.format(project_id)
    repo_full_path = join(app.config['WORK_REPOS_ROOT'], project.work_repo.url)
    if ssh(['ls', repo_full_path], check=False) == 0:
        return 'Repo already exists, skipping.'
        #ssh(['rm', '-rf', repo_full_path])
    ssh(['git', 'init', repo_full_path])
    README = join(repo_full_path, 'README')
    ssh(['touch', README])
    ssh(['echo', '"Project {}"'.format(project.name), '>', README])
    ssh(['git', '-C', repo_full_path, 'add', 'README'])
    user = project.managers[0].user
    name = user.first_name+' '+user.last_name
    ssh(['git', '-C', repo_full_path, 'config', '--local', 'user.name', name])
    ssh(['git', '-C', repo_full_path, 'config', '--local', 'user.email', user.email])
    ssh(['git', '-C', repo_full_path, 'commit', '-m', '"Initial commit"'])

class Repo(object):
    def __init__(self, project):
        self.project_id = project.id
        self.repo_full_path = join(current_app.config['WORK_REPOS_ROOT'], project.work_repo.url)

    def create_branch(self, branch_name):
        return current_app.git_queue.enqueue(_create_branch, self.repo_full_path, branch_name)

    def create_internal_project_repo(self):
        return current_app.git_queue.enqueue(_create_internal_project_repo, self.project_id)
