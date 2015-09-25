from collections import namedtuple
from pprint import pprint

from rebase.github import create_github_app
from rebase.github.languages import path_to_languages
from rebase.models.user import User
from rebase.models.github_account import GithubAccount
from rebase.models.github_repository import GithubRepository
from rebase.models.github_organization import GithubOrganization
from rebase.models.skill_set import SkillSet
from rebase.models.contractor import Contractor

GithubSession = namedtuple('GithubSession', ['api', 'account', 'login', 'user', 'DB'])

def make_github_interface(user_id, role, login):
    from rebase import create_app
    app, _, db = create_app()
    user = User.query.get_or_404(user_id)
    user.set_role(role)
    github_account = GithubAccount.query_by_user(user).filter(GithubAccount.login==login).first()
    if not github_account:
        raise RuntimeError('Could not find a GithubAccount with login \'{}\' for user id:{}'.format(login, user_id))
    github_access_token = (github_account.access_token, '')
    if not github_account:
        raise RuntimeError('User[id={}] has no GitHub account'.format(user.id))
    github = create_github_app(app)
    @github.tokengetter
    def get_github_oauth_token():
        return github_access_token
    return GithubSession(github, github_account, login, user, db)

def save_languages(user, languages, db):
    skill_set = SkillSet.query.join(Contractor).filter(Contractor.user == user).first()
    if not skill_set:
        raise RuntimeError('This contractor should have an associated SkillSet already')
    skill_set.skills = languages
    db.session.add(skill_set)
    db.session.commit()

def detect_languages(session):
    ''' returns a list of all languages spoken by this user '''
    owned_repos = github.get('/user/repos').data
    commit_paths = []
    for repo in owned_repos:
        commits = github.get(repo['url']+'/commits', data={ 'author': login}).data
        for commit in commits:
            languages = []
            paths = []
            tree = github.get(commit['commit']['tree']['url']).data
            for path_obj in tree['tree']:
                paths.append(path_obj['path'])
            commit_paths.append(paths)

    found_languages = path_to_languages(commit_paths)
    save_languages(user, found_languages, db)
    return found_languages

def extract_repos_info(session):
    ''' returns a list of all languages spoken by this user '''
    orgs = session.api.get('/user/orgs').data
    for org in orgs:
        github_org = None
        repos = session.api.get(org['repos_url']).data
        for repo in repos:
            if repo['permissions']['admin'] and not repo['fork']:
                if not github_org:
                    github_org = GithubOrganization(
                        session.account,
                        org['login'],
                        org['id'],
                        org['url'],
                        org['description']
                    )
                    session.DB.session.add(github_org)
                github_repo = GithubRepository(
                    repo['name'],
                    repo['id'],
                    repo['url'],
                    description=repo['description'],
                    org=github_org
                )
                session.DB.session.add(github_repo)
    session.DB.session.commit()
    return 'OK'

def load_repo_info(user_id, role, login):
    session = make_github_interface(user_id, role, login)
    return extract_repos_info(session)

def read_repo(user_id, login):
    session = make_github_interface(user_id, login)
    return detect_languages(session)
