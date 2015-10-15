from collections import namedtuple
from datetime import datetime
from functools import lru_cache

from flask import current_app
from sqlalchemy import and_
from sqlalchemy.orm.collections import InstrumentedList

from rebase.github import create_github_app
from rebase.github.languages import path_to_languages
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
    with session.DB.session.no_autoflush:
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
    issues = session.api.get('/repos/{owner}/{repo}/issues'.format(
        owner=project.organization.name,
        repo=project.name
    )).data
    tickets = []
    komments = []
    for issue in issues:
        ticket = GithubTicket(project, issue['number'], issue['title'], datetime.strptime(issue['created_at'], _gh_datetime_format))
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
        comments = session.api.get('/repos/{owner}/{repo}/issues/{number}/comments'.format(
            owner=project.organization.name,
            repo=project.name,
            number=issue['number']
        )).data
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
    session.DB.session.commit()
    return tickets, komments

def import_github_repos(repos, user, db_session):
    # TODO add GithubOrgAccount instance for each imported GithubOrganization
    '''
        Imports the 'repos' and returns an object with the created or updated GithubRepository, GithubProject and GithubOrganization instances
    '''
    # in new_data we will store the newly created object, e.g. Managers, Organizations, GithubProjects, etc.
    new_data = { k: [] for k in _serializers.keys() }
    orgs = {}
    accounts = {}
    for repo_id, repo in repos.items():
        _org = repo['project']['organization']
        if _org['org_id'] not in orgs:
            gh_org = GithubOrganization.query.filter(GithubOrganization.org_id==_org['org_id']).first()
            if not gh_org:
                gh_org = GithubOrganization(
                    _org['login'],
                    user,
                    _org['org_id'],
                    _org['url'],
                    _org['description'],
                )
                db_session.add(gh_org)
            # go through the GithubOrgAccounts and create them if need be
            _org_accounts = _org['accounts']
            for _account in _org_accounts:
                _account_id = _account['account_id']
                _org_account = GithubOrgAccount.query.filter(
                    and_(
                        GithubOrgAccount.account_id==_account_id,
                        GithubOrgAccount.org_id==_org['id'],
                    )
                ).first()
                if not _org_account:
                    if _account_id not in accounts:
                        account = GithubAccount.query.filter(GithubAccount.id==_account_id).first()
                        if not account:
                            raise ValueError('GithubAccount with id: {} is not found in the database'.format(_account_id))
                        accounts[account.id] = account
                    GithubOrgAccount(gh_org, account)
            new_data['orgs'].append(gh_org)
            orgs[gh_org.org_id] = gh_org
        else:
            gh_org = orgs[_org['org_id']]
            owner = Owner(user, gh_org)
            gh_org.owners.append(owner)
            db_session.add(gh_org)
        _repo = GithubRepository.query.filter(GithubRepository.repo_id==repo_id).first()
        if not _repo:
            _project = GithubProject(gh_org, repo['name'])
            _repo = GithubRepository(_project, repo['name'], repo_id, repo['url'], repo['description'])
        if any(map(lambda mgr: mgr.user == user, _repo.project.managers)):
            continue
        else:
            mgr = Manager(user, _repo.project)
            _repo.project.managers.append(mgr)
            db_session.add(_repo)
            new_data['managers'].append(mgr)
        new_data['projects'].append(_repo.project)
        new_data['repos'].append(_repo)

    db_session.commit()
    
    # start a background task to pull tickets from Github for each repo
    for project in new_data['projects']:
        current_app.default_queue.enqueue(import_tickets, project.id, project.organization.accounts[0].account.id)

    # serialize the new data
    return { key: list(map(lambda elt: _serializers[key].dump(elt).data, value)) for key, value in new_data.items() }
