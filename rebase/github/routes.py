from pprint import pformat
from pickle import dump

from flask import redirect, url_for, session, request, jsonify, render_template
from flask.ext.login import login_required
from flask_oauthlib.client import OAuth

from rebase.github.languages import path_to_languages

def detect_languages(app, github, username):
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

    with open('/tmp/paths.pickle', 'wb') as archive:
        dump(commit_paths, archive)
    return path_to_languages(commit_paths)


def register_github_routes(app):
    oauth = OAuth(app)
    github = oauth.remote_app(
        'github',
        consumer_key=app.config['GITHUB_CLIENT_ID'],
        consumer_secret=app.config['GITHUB_CLIENT_SECRET'],
        request_token_params={'scope': 'user, repo'},
        base_url='https://api.github.com/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize'
    )

    @app.route('/github/')
    @login_required
    def github_root():
        if 'github_token' in session:
            me = github.get('user')
            username = me.data['login']
            blob = pformat(detect_languages(app, github, username))
            repos = github.get('user/repos')
            return render_template('github.html', data=me.data, repos=repos.data, blob = blob);
        return github.authorize(callback=url_for('github_authorized', _external=True))

    @app.route('/github/login')
    @login_required
    def github_login():
        return github.authorize(callback=url_for('github_authorized', _external=True))

    @app.route('/github/logout')
    @login_required
    def github_logout():
        session.pop('github_token', None)
        return redirect(url_for('github_root'))

    @app.route('/github/authorized')
    @login_required
    def github_authorized():
        resp = github.authorized_response()
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error'],
                request.args['error_description']
            )
        elif 'error' in resp:
            if resp['error'] == 'bad_verification_code':
                return redirect(url_for('github_login'))
        session['github_token'] = (resp['access_token'], '')
        return redirect(url_for('github_root'))

    @app.route('/github/repos')
    @login_required
    def repos():
        if 'github_token' in session:
            me = github.get('user/repos')
            return jsonify({'repos': me.data})
        return redirect(url_for('github_login'))

    @github.tokengetter
    @login_required
    def get_github_oauth_token():
        return session.get('github_token')
