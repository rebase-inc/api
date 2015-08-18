
from flask import redirect, url_for, session, request, jsonify, render_template
from flask.ext.login import login_required, current_user

from redis import Redis
from requests import post
from rq import Queue

from rebase.common.database import DB
from rebase.github import create_github_app
from rebase.github.scanners import read_repo
from rebase.models.contractor import Contractor
from rebase.models.github_account import GithubAccount
from rebase.models.remote_work_history import RemoteWorkHistory
from rebase.models.skill_set import SkillSet
from rebase.models.user import User

def save_access_token(github_user, logged_in_user, access_token, db):
    user = User.query.filter(User.id==logged_in_user.id).first()
    github_account = GithubAccount.query_by_user(user).filter(GithubAccount.user_name==github_user['login']).first()
    if not github_account:
        remote_work_history = RemoteWorkHistory.query_by_user(user).first()
        if not remote_work_history:
            contractor = Contractor.query_by_user(user).first()
            if not contractor:
                # NOTE we should eventually do a redirect(url_for('register_as_contractor')) or something, or raise something
                #raise NotRegisteredAsContractor(user)
                contractor = Contractor(user)
                skill_set = SkillSet(contractor)
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

    @app.route('/github/')
    @login_required
    def github_root():
        if 'github_token' in session:
            github_user = github.get('user').data
            _ = app.default_queue.enqueue(read_repo, current_user.id, github_user['login'])
            clone_data = {'github_oauth_token': session['github_token'][0]}
            clone_response = post('http://ec2-52-21-89-158.compute-1.amazonaws.com:5001/', json=clone_data)
            app.logger.debug('Clone request status code: {}'.format(clone_response.status_code))
            return render_template('github.html', github_user=github_user);

        return github.authorize(callback=url_for('github_authorized', _external=True))

    @app.route('/github/verify')
    @login_required
    def verify_all_github_tokens():
        github_accounts = GithubAccount.query.all()
        for account in github_accounts:
            app.logger.debug('Verifying account for '+account.user_name)
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

        return redirect(url_for('github_root'))

    @github.tokengetter
    def get_github_oauth_token():
        return session.get('github_token')
