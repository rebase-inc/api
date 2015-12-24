from os.path import join
from subprocess import call, check_call

from flask import current_app

from rebase.models.internal_project import InternalProject


def _create_branch(repo_path, branch):
    check_call(['git', '-C', repo_path, 'branch', branch])

def _create_internal_project_repo(repo_full_path, project_name, user_name, user_email):
    if call(['ls', repo_full_path]) == 0:
        return 'Repo already exists, skipping.'
    check_call(['git', 'init', repo_full_path])
    README = join(repo_full_path, 'README')
    check_call(['touch', README])
    check_call(['echo', '"Project {}"'.format(project_name), '>', README])
    check_call(['git', '-C', repo_full_path, 'add', 'README'])
    check_call(['git', '-C', repo_full_path, 'config', '--local', 'user.name', user_name])
    check_call(['git', '-C', repo_full_path, 'config', '--local', 'user.email', user_email])
    check_call(['git', '-C', repo_full_path, 'commit', '-m', '"Initial commit"'])


class Repo(object):
    def __init__(self, project):
        self.project = project
        self.repo_full_path = project.work_repo.repo_path
        self.enqueue = current_app.git_queue.enqueue

    def create_branch(self, branch_name):
        return self.enqueue(_create_branch, self.repo_full_path, branch_name)

    def create_internal_project_repo(self, user):
        return self.enqueue(
            _create_internal_project_repo,
            self.repo_full_path,
            self.project.name,
            user.name,
            user.email
        )
