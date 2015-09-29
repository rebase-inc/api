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
    User,
    SkillSet
)
from rebase.models.skill_set import SkillSet
from rebase.models.contractor import Contractor

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

def save_languages(user, languages, db):
    skill_set = SkillSet.query.join(Contractor).filter(Contractor.user == user).first()
    if not skill_set:
        raise RuntimeError('This contractor should have an associated SkillSet already')
    skill_set.skills = languages
    db.session.add(skill_set)
    db.session.commit()

def detect_languages(session):
    ''' returns a list of all languages spoken by this user '''
    owned_repos = session.api.get('/user/repos').data
    commit_paths = []
    for repo in owned_repos:
        commits = github.get(repo['url']+'/commits', data={ 'author': session.login}).data
        for commit in commits:
            languages = []
            paths = []
            tree = github.get(commit['commit']['tree']['url']).data
            for path_obj in tree['tree']:
                paths.append(path_obj['path'])
            commit_paths.append(paths)
    found_languages = path_to_languages(commit_paths)
    save_languages(session.user, found_languages, session.db)
    return found_languages

def extract_repos_info(session):
    ''' returns a list of all languages spoken by this user '''
    orgs = session.api.get('/user/orgs').data
    with session.DB.session.no_autoflush:
        for org in orgs:
            setattr(session.account, 'orgs', InstrumentedList())
        github_org = None
        repos = session.api.get(org['repos_url']).data
        for repo in repos:
            if repo['permissions']['admin'] and not repo['fork']:
                # first verify this repo isn't imported already:
                imported_repo = GithubRepository.query.filter(GithubRepository.repo_id==repo['id']).first()
                if imported_repo:
                    continue
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

def import_repos(session, repos):
    orgs = {}
    for repo_id, repo in repos.items():
        _org = repo['org']
        if _org['org_id'] not in orgs:
            gh_org = GithubOrganization.query.filter(GithubOrganization.org_id==_org['org_id']).first()
            if not gh_org:
                gh_org = GithubOrganization(
                    _org['login'],
                    session.user,
                    _org['org_id'],
                    _org['url'],
                    _org['description'],
                )
                session.DB.session.add(gh_org)
            orgs[gh_org.org_id] = gh_org
        else:
            gh_org = orgs[_org['org_id']]
        _repo = GithubRepository.query.filter(GithubRepository.repo_id==repo_id).first()
        if not _repo:
            _project = GithubProject(gh_org, repo['name'])
            _repo = GithubRepository(_project, repo['name'], repo_id, repo['url'], repo['description'])
    session.DB.session.commit()

def import_github_repos(user_id, role, login, repos):
    ''' Given a list of Github Repository ids, import them, creating the organization as needed '''
    session = make_github_interface(user_id, role, login)
    import_repos(session, repos)
    return 'OK'


def load_repo_info(user_id, role, login):
    session = make_github_interface(user_id, role, login)
    extract_repos_info(session)
    return 'OK'

def read_repo(user_id, login):
    session = make_github_interface(user_id, login)
    return detect_languages(session)
