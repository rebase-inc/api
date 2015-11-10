from os.path import join

from flask import current_app

from rebase.common.ssh import SSH


def _create_branch(repo_path, branch):
    from rebase import create_app
    app, _, __ = create_app()
    ssh = SSH('git', app.config['WORK_REPOS_HOST'])
    ssh(['git', '-C', repo_path, 'branch', branch])

class Repo(object):
    def __init__(self, project):
        self.project_id = project.id
        self.repo_full_path = join(current_app.config['WORK_REPOS_ROOT'], project.work_repo.url)

    def create_branch(self, branch_name):
        return current_app.git_queue.enqueue(_create_branch, self.repo_full_path, branch_name)
