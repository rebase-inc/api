from rebase.github import create_github_app
from rebase.github.languages import path_to_languages
from rebase.models.user import User
from rebase.models.github_account import GithubAccount

def detect_languages(github, username):
    ''' returns a list of all languages spoken by this user '''
    owned_repos = github.get('/user/repos'.format(username)).data
    commit_paths = []
    for repo in owned_repos:
        commits = github.get(repo['url']+'/commits', data={ 'author': username}).data
        for commit in commits:
            languages = []
            paths = []
            tree = github.get(commit['commit']['tree']['url']).data
            for path_obj in tree['tree']:
                paths.append(path_obj['path'])
            commit_paths.append(paths)

    return path_to_languages(commit_paths)

def read_repo(user_id, github_username):
    from rebase import create_app
    app, _, db = create_app()
    user = User.query.filter(User.id==user_id).first()
    github_account = GithubAccount.query_by_user(user).filter(GithubAccount.user_name==github_username).first()
    github_access_token = (github_account.auth_token, '')
    if not github_account:
        raise RuntimeError('User[id={}] has no GitHub account'.format(user.id))
    github = create_github_app(app)

    @github.tokengetter
    def get_github_oauth_token():
        return github_access_token

    return detect_languages(github, github_username)
