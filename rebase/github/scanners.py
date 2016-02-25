from logging import getLogger

from flask import current_app

from rebase.git.users import generate_authorized_users
from rebase.github.rq_jobs import import_tickets, create_work_repo
from rebase.models import (
    GithubAccount,
    GithubRepository,
    GithubOrganization,
    GithubProject,
    GithubOrgAccount,
    Manager,
)
from rebase.views.github_contributed_repo import serializer as contributed_repo_serializer


logger = getLogger()


def extract_repos_info(session):
    ''' returns a list of importable Github repos for the account in session '''
    importable = []
    orgs = session.api.get('/user/orgs').data
    for org in orgs:
        repos = session.api.get(org['repos_url']).data
        for repo in repos:
            repo['owner']['description'] = org['description']
            repo['github_account_id'] = session.account.id
            if repo['permissions']['admin'] and not repo['fork']:
                _repo = GithubRepository.query.filter(GithubRepository.repo_id==repo['id']).first()
                if not _repo:
                    importable.append(repo)
                else:
                    # this repo already exists, so is this user a manager for the repo already?
                    mgr = Manager.query.filter_by(user_id=session.user.id, project_id=_repo.project.id).first()
                    if not mgr:
                        importable.append(repo)
    return importable


def import_github_repos(repos, user, db_session):
    new_mgr_roles = []
    new_mgr_roles_for_existing_projects = []
    new_projects = []
    for repo_id, repo in repos.items():
        github_account = GithubAccount.query.filter(GithubAccount.id==repo['github_account_id']).first()
        if not github_account:
            logger.debug('Cannot find GithubAccount[{}], so we cannot import repo[{}, {}]'.format(
                repo['github_account_id'],
                repo['id'],
                repo['name']
            ))
            continue

        rebase_repo = GithubRepository.query.filter(GithubRepository.repo_id==repo['id']).first()
        if rebase_repo:
            new_mgr = Manager(user, rebase_repo.project)
            db_session.add(new_mgr)
            new_mgr_roles.append(new_mgr)
            new_mgr_roles_for_existing_projects.append(new_mgr)
        else:
            rebase_org = GithubOrganization.query.filter(GithubOrganization.org_id==repo['owner']['id']).first()
            if not rebase_org:
                org = repo['owner']
                rebase_org = GithubOrganization(org['login'], user, org['id'], org['url'], org['description'])
                project_account = GithubOrgAccount(rebase_org, github_account)
                db_session.add(project_account)
            rebase_project = GithubProject(rebase_org, repo['name'], repo['id'], repo['url'], repo['description'])
            db_session.add(rebase_project)
            new_mgr_roles.append(rebase_project.managers[0])
            new_projects.append(rebase_project)
    db_session.commit()
    for project in new_projects:
        current_app.default_queue.enqueue(import_tickets, project.id, project.organization.accounts[0].account.id)
        create_repo_job = current_app.git_queue.enqueue(create_work_repo, project.id, project.organization.accounts[0].account.id)
        current_app.git_queue.enqueue(generate_authorized_users, project.id, depends_on=create_repo_job)
    for role in new_mgr_roles_for_existing_projects:
        current_app.git_queue.enqueue(generate_authorized_users, role.project.id)
    # the import statement is move here to prevent import error related to current
    from rebase.views.manager import serializer as mgr_serializer
    return mgr_serializer.dump(new_mgr_roles, many=True).data


