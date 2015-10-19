from collections import namedtuple
from datetime import datetime
from functools import lru_cache

from flask import current_app
from sqlalchemy import and_
from sqlalchemy.orm.collections import InstrumentedList

from rebase.github import create_github_app
from rebase.models import (
    Comment,
    GithubAccount,
    GithubRepository,
    GithubOrganization,
    GithubProject,
    GithubOrgAccount,
    GithubTicket,
    GithubUser,
    Manager,
    Owner,
    SkillRequirement,
    User,
)
from rebase.views.github_organization import serializer as org_serializer
from rebase.views.github_project import serializer as project_serializer
from rebase.views.manager import serializer as mgr_serializer
from rebase.views.github_repository import serializer as repo_serializer

_serializers = {
    'repos':    repo_serializer,
    'projects': project_serializer,
    'orgs':     org_serializer,
    'managers': mgr_serializer
}

_gh_datetime_format = '%Y-%m-%dT%H:%M:%SZ'

class GithubSession(object):
    def __init__(self, api, account, user, DB):
        self.api = api
        self.account = account
        self.user = user
        self.DB = DB

    def __hash__(self):
        return hash('{account_id}_{user_id}'.format(
            account_id=self.account.id, 
            user_id=self.user.id
        ))

def make_session(github_account, app, user, db):
    github = create_github_app(app)
    @github.tokengetter
    def get_github_oauth_token():
        return (github_account.access_token, '')
    return GithubSession(github, github_account, user, db)

def make_admin_github_session(account_id):
    from rebase import create_app
    app, _, db = create_app()
    user = User('RQ', 'RQ', 'RQ', 'RQ')
    user.admin = True
    github_account = GithubAccount.query.filter(GithubAccount.id==account_id).first()
    if not github_account:
        raise RuntimeError('Could not find a GithubAccount with id \'{}\''.format(account_id))
    return make_session(github_account, app, user, db)

def extract_repos_info(session):
    ''' returns a list of all repos managed by this user '''
    orgs = session.api.get('/user/orgs').data
    for org in orgs:
        github_org = None
        repos = session.api.get(org['repos_url']).data
        for repo in repos:
            if repo['permissions']['admin'] and not repo['fork']:
                if not github_org:
                    github_org = GithubOrganization.query.filter(GithubOrganization.org_id==org['id']).first()
                    if not github_org:
                        github_org = GithubOrganization(
                            org['login'],
                            session.user,
                            org['id'],
                            org['url'],
                            org['description']
                        )
                        GithubOrgAccount(github_org, session.account)
                        session.DB.session.add(github_org)
                    Owner(session.user, github_org)
                _repo = GithubRepository.query.filter(GithubRepository.repo_id==repo['id']).first()
                if not _repo:
                    github_project = GithubProject(github_org, repo['name'])
                    _repo = GithubRepository(
                        github_project,
                        repo['name'],
                        repo['id'],
                        repo['url'],
                        repo['description']
                    )
                    session.DB.session.add(_repo)
                mgr = Manager.query.filter(
                    and_(
                        Manager.user==session.user,
                        Manager.project==_repo.project
                    )
                ).first()
                if not mgr:
                    session.DB.session.add(Manager(session.user, _repo.project))
    session.DB.session.commit()
    return session.account

@lru_cache(maxsize=None)
def get_or_make_user(session, user_id, user_login):
    '''
    return a User or GithubUser instance for the 'user_id' and 'user_login' provided
    '''
    account = GithubAccount.query.filter(GithubAccount.account_id==user_id).first()
    if not account:
        _user = GithubUser.query.filter(GithubUser.github_id==user_id).first()
        if not _user:
            gh_user = session.api.get('/users/{username}'.format(username=user_login)).data
            _user = GithubUser(user_id, user_login, gh_user['name'])
    else:
        _user = account.user
    return _user

def import_tickets(project_id, account_id):
    session = make_admin_github_session(account_id)
    project = GithubProject.query.filter(GithubProject.id==project_id).first()
    if not project:
        return 'Unknow project with id: {}'.format(project_id)
    repo_url = '/repos/{owner}/{repo}'.format(
        owner=project.organization.name,
        repo=project.name
    )
    languages = session.api.get(repo_url+'/languages').data
    # Normalize the language values by dividing by the sum of values.
    # Ultimately we want a level of difficulty per language, not a relative distribution of the quantity of code.
    # But this will do for now.
    total = sum(languages.values())
    languages = { language: code_size/total for language, code_size in languages.items() }
    issues = session.api.get(repo_url+'/issues').data
    tickets = []
    komments = []
    for issue in issues:
        ticket = GithubTicket(project, issue['number'], issue['title'], datetime.strptime(issue['created_at'], _gh_datetime_format))
        ticket.skill_requirement.skills = languages
        tickets.append(ticket)
        issue_user = issue['user']
        body = Comment(
            get_or_make_user(
                session,
                issue_user['id'],
                issue_user['login'],
            ),
            issue['body'],
            ticket=ticket
        )
        komments.append(body)
        comments = session.api.get(issue['url']+'/comments').data
        for comment in comments:
            comment_user = comment['user']
            ticket_comment = Comment(
                get_or_make_user(
                    session,
                    comment_user['id'],
                    comment_user['login'],
                ),
                comment['body'],
                ticket=ticket
            )
            komments.append(ticket_comment)
        session.DB.session.add(ticket)
    project.imported = True
    session.DB.session.commit()
    return tickets, komments

def import_github_repos(repos, user, db_session):
    for repo_id, repo in repos.items():
        project = GithubProject.query.filter(GithubProject.id==repo['project']['id']).first()
        if project:
            if project.imported:
                current_app.logger.info('Project with id {} is already imported.'.format(project.id))
            else:
                current_app.default_queue.enqueue(import_tickets, project.id, project.organization.accounts[0].account.id)
        else:
            current_app.logger.info('Project with id {} does not exists in Rebase, not importing.'.format(project.id))
