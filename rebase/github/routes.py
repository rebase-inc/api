
from flask import redirect, url_for, session, request, jsonify, render_template
from flask.ext.login import login_required, current_user

from redis import Redis
from rq import Queue

from rebase.common.database import DB
from rebase.github import create_github_app
from rebase.github.languages import path_to_languages
from rebase.github.scanners import read_repo
from rebase.models.contractor import Contractor
from rebase.models.github_account import GithubAccount
from rebase.models.remote_work_history import RemoteWorkHistory
from rebase.models.user import User

def save_access_token(github_user, logged_in_user, access_token, db):
    user = User.query.filter(User.id==logged_in_user.id).first()
    github_account = GithubAccount.query_by_user(user).filter(GithubAccount.user_name==github_user['login']).first()
    if not github_account:
        remote_work_history = RemoteWorkHistory.query_by_user(user).first()
        if not remote_work_history:
            contractor = Contractor.query_by_user(user).first()
            if not contractor:
                # NOTE we should eventually do a redirect(url_for('register_as_contractor')) or something, instead of raising an exception
                #raise NotRegisteredAsContractor(user)
                contractor = Contractor(user)
            remote_work_history = RemoteWorkHistory(contractor)
        github_account = GithubAccount(
            remote_work_history=remote_work_history,
            user_name=github_user['login'],
            auth_token=access_token
        )
    github_account.access_token = access_token
    db.session.add(github_account)
    db.session.commit()

def register_github_routes(app):

    github = create_github_app(app)
    background_queue = Queue(connection=Redis())

    @app.route('/github/')
    @login_required
    def github_root():
        if 'github_token' in session:
            languages = {'Python': 1}
            repos = [{}]
            github_user = github.get('user').data
            _ = background_queue.enqueue(read_repo, current_user.id, github_user['login'])
            return render_template('github.html', data=github_user, repos=repos, languages = languages);
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
        github_user = github.get('user').data

        save_access_token(github_user, current_user, resp['access_token'], DB)

        return redirect(url_for('github_root'))

    @github.tokengetter
    def get_github_oauth_token():
        return session.get('github_token')
