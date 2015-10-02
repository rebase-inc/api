from functools import wraps

from flask import redirect, url_for, session, request, jsonify
from flask.ext.login import login_required, current_user

from rebase.common.database import DB
from rebase.github import create_github_app
from rebase.github.scanners import import_github_repos
from rebase.models.contractor import Contractor
from rebase.models.github_account import GithubAccount
from rebase.models.remote_work_history import RemoteWorkHistory
from rebase.models.skill_set import SkillSet
from rebase.models.user import User

def save_access_token(github_user, logged_in_user, access_token, db):
    user = User.query.filter(User.id==logged_in_user.id).first()
    github_account = GithubAccount.query_by_user(user).filter(GithubAccount.login==github_user['login']).first()
    if not github_account:
        github_account = GithubAccount(logged_in_user, github_user['id'], github_user['login'], access_token)
    github_account.access_token = access_token
    db.session.add(github_account)
    db.session.commit()

def register_github_routes(app):

    github = create_github_app(app)

    def github_oauth(fn):
        @wraps(fn)
        def _oauthed_fn(*args, **kwargs):
            if 'github_token' in session:
                return fn(*args, **kwargs)
            return github.authorize(callback=url_for('github_authorized', _external=True))
        return _oauthed_fn

    @app.route('/github')
    @login_required
    @github_oauth
    def github_root():
        github_user = github.get('user').data
        return redirect('/app/app.html')

    @app.route('/github/verify')
    @login_required
    def verify_all_github_tokens():
        github_accounts = GithubAccount.query.all()
        for account in github_accounts:
            app.logger.debug('Verifying account for '+account.login)
            token = (account.auth_token, '')
            app.logger.debug('token: '+account.auth_token)
            github = create_github_app(app)
            @github.tokengetter
            def get_github_oauth_token():
                return token
            user = github.get('/user').data
            app.logger.debug(user)

        return jsonify({'success':'complete'})

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
        github_user = github.get('user').data

        save_access_token(github_user, current_user, resp['access_token'], DB)

        return redirect('/app/app.html')

    @github.tokengetter
    def get_github_oauth_token():
        return session.get('github_token')

    @app.route('/github/import_repos', methods=['POST'])
    @login_required
    def import_repos():
        new_data = import_github_repos(request.json['repos'], current_user, DB.session)
        return jsonify(new_data);
