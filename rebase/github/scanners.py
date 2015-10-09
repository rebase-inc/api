from collections import namedtuple
from pprint import pprint

from sqlalchemy.orm.collections import InstrumentedList

from rebase.github import create_github_app
from rebase.github.languages import path_to_languages
from rebase.models import (
    GithubAccount,
    GithubRepository,
    GithubOrganization,
    GithubProject,
    Manager,
    Owner,
    User,
)
from rebase.views.organization import serializer as org_serializer
from rebase.views.project import serializer as project_serializer
from rebase.views.code_repository import serializer as repo_serializer

GithubSession = namedtuple('GithubSession', ['api', 'account', 'user', 'DB'])

def make_session(github_account, app, user, db):
    github = create_github_app(app)
    @github.tokengetter
    def get_github_oauth_token():
        return (github_account.access_token, '')
    return GithubSession(github, github_account, user, db)

def make_github_interface(user_id, role, login):
    from rebase import create_app
    app, _, db = create_app()
    user = User.query.get_or_404(user_id)
    user.set_role(role)
    github_account = GithubAccount.query_by_user(user).filter(GithubAccount.login==login).first()
    if not github_account:
        raise RuntimeError('Could not find a GithubAccount with login \'{}\' for user id:{}'.format(login, user_id))
    if not github_account:
        raise RuntimeError('User[id={}] has no GitHub account'.format(user.id))
    return make_session(github_account, app, user, db)

def extract_repos_info(session):
    ''' returns a list of all repos managed by this user '''
    orgs = session.api.get('/user/orgs').data
    with session.DB.session.no_autoflush:
        for org in orgs:
            setattr(session.account, 'orgs', InstrumentedList())
            github_org = None
            repos = session.api.get(org['repos_url']).data
            for repo in repos:
                if repo['permissions']['admin'] and not repo['fork']:
                    if not github_org:
                        github_org = GithubOrganization(
                            org['login'],
                            session.user,
                            org['id'],
                            org['url'],
                            org['description']
                        )
                        setattr(github_org, 'repos', InstrumentedList())
                        setattr(github_org, 'account', session.account)
                        session.account.orgs.append(github_org)
                    github_project = GithubProject(github_org, repo['name'])
                    github_repo = GithubRepository(
                        github_project,
                        repo['name'],
                        repo['id'],
                        repo['url'],
                        repo['description']
                    )
                    setattr(github_repo, 'org', github_org)
                    github_org.repos.append(github_repo)

def import_github_repos(repos, user, db_session):
    '''
        Imports the 'repos' and returns an object with the created or updated CodeRepository, Project and Organization instances
    '''
    new_data = {
        'repos':        [],
        'projects':    [],
        'orgs':         [],
    }
    orgs = {}
    for repo_id, repo in repos.items():
        _org = repo['org']
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
        new_data['projects'].append(_repo.project)
        new_data['repos'].append(_repo)

    db_session.commit()

    # serialize the new data
    new_data['projects'] = list(map(lambda prj: project_serializer.dump(prj).data, new_data['projects']))
    new_data['orgs'] = list(map(lambda org: org_serializer.dump(org).data, new_data['orgs']))
    new_data['repos'] = list(map(lambda repo: repo_serializer.dump(repo).data, new_data['repos']))
    return new_data
