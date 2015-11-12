from os.path import join

from flask import current_app
from flask.ext.login import current_user

from rebase.common.ssh import SSH
from rebase.models.internal_project import InternalProject


def _create_branch(host, repo_path, branch):
    ssh = SSH('git', host)
    ssh(['git', '-C', repo_path, 'branch', branch])

def _create_internal_project_repo(host, repo_full_path, project_name, user_name, user_email):
    ssh = SSH('git', host)
    if ssh(['ls', repo_full_path], check=False) == 0:
        return 'Repo already exists, skipping.'
        #ssh(['rm', '-rf', repo_full_path])
    ssh(['git', 'init', repo_full_path])
    README = join(repo_full_path, 'README')
    ssh(['touch', README])
    ssh(['echo', '"Project {}"'.format(project_name), '>', README])
    ssh(['git', '-C', repo_full_path, 'add', 'README'])
    ssh(['git', '-C', repo_full_path, 'config', '--local', 'user.name', user_name])
    ssh(['git', '-C', repo_full_path, 'config', '--local', 'user.email', user_email])
    ssh(['git', '-C', repo_full_path, 'commit', '-m', '"Initial commit"'])


class Repo(object):
    def __init__(self, project):
        self.project = project
        self.repo_full_path = join(current_app.config['WORK_REPOS_ROOT'], project.work_repo.url)
        self.host = current_app.config['WORK_REPOS_HOST']
        self.enqueue = current_app.git_queue.enqueue

    def create_branch(self, branch_name):
        return self.enqueue(_create_branch, self.host, self.repo_full_path, branch_name)

    def create_internal_project_repo(self):
        user_name = current_user.first_name+' '+current_user.last_name
        return self.enqueue(
            _create_internal_project_repo,
            self.host,
            self.repo_full_path,
            self.project.name,
            user_name,
            current_user.email
        )
