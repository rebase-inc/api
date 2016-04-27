from functools import wraps
from logging import getLogger

from flask import redirect, url_for, request, jsonify, current_app
from flask.ext.login import login_required, current_user

from rebase.common.database import DB
from rebase.github import create_github_app
from rebase.github.languages import detect_languages
from rebase.github.scanners import (
    import_github_repos,
    extract_repos_info,
)
from rebase.github.session import make_session
from rebase.models.contractor import Contractor
from rebase.models.github_account import GithubAccount
from rebase.models.remote_work_history import RemoteWorkHistory
from rebase.models.skill_set import SkillSet
from rebase.models.user import User


logger = getLogger()


def save_github_account(account_id, login, access_token):
    github_account = GithubAccount.query_by_user(current_user).filter(GithubAccount.login==login).first()
    github_account = github_account or GithubAccount(current_user, account_id, login, access_token)
    github_account.access_token = access_token
    DB.session.add(github_account)
    DB.session.commit()
    return github_account


def analyze_contractor_skills(github_account):
    contractor = next(filter(lambda r: r.type == 'contractor', current_user.roles), None)
    if contractor:
        remote_work_history = RemoteWorkHistory.query_by_user(current_user).first() or RemoteWorkHistory(contractor)
        remote_work_history.github_accounts.append(github_account)
        remote_work_history.analyzing = True
        DB.session.add(remote_work_history)
        DB.session.commit()
        current_app.default_queue.enqueue_call(func=detect_languages, args=(github_account.id,), timeout=360 ) # timeout = 6 minutes


def register_github_routes(app):

    github = create_github_app(app)

    @app.route('/api/v1/github', methods=['GET'])
    @login_required
    def github_root():
        return github.authorize(callback=url_for('github_auth_callback', _external=True))

    @app.route('/api/v1/github/verify')
    @login_required
    def verify_all_github_tokens():
        for account in current_user.github_accounts:
            logger.debug('Verifying Github account '+account.login)
            make_session(account, current_app, current_user, DB)
        return jsonify({'success':'complete'})

    @app.route('/api/v1/github/login')
    @login_required
    def github_login():
        return github.authorize(callback=url_for('github_auth_callback', _external=True))

    @app.route('/api/v1/github/skills_login')
    def github_skills_login():
        return github.authorize(callback=url_for('github_auth_callback', _external=True), redirect_to=url_for('github_skills'))

    @login_required
    def github_skills():
        pass

    @app.route('/api/v1/github/logout')
    @login_required
    def github_logout():
        session.pop('github_token', None)
        return redirect(url_for('github_root'))

    @app.route('/api/v1/github/authorized')
    @login_required
    def github_auth_callback():
        resp = github.authorized_response()
        if resp is None:
            return 'Access denied: reason={error} error={error_description}'.format(**request.args)
        elif 'error' in resp:
            if resp['error'] == 'bad_verification_code': return redirect(url_for('github_login'))
            else: return 'Unknown error: {}'.format(resp['error'])
        else:
            github_user = github.get('user', token=(resp['access_token'], '')).data
            github_account = save_github_account(github_user['id'], github_user['login'], resp['access_token'])
            analyze_contractor_skills(github_account)
        return redirect('/')

    @app.route('/api/v1/github/import_repos', methods=['POST'])
    @login_required
    def import_repos():
        new_mgr_roles = import_github_repos(request.json['repos'], current_user, DB.session)
        return jsonify({'roles': new_mgr_roles});

    @app.route('/api/v1/github_accounts/<int:github_account_id>/importable_repos')
    @login_required
    def importable_repos(github_account_id):
        account = GithubAccount.query.get_or_404(github_account_id)
        session = make_session(account, current_app, current_user, DB)
        return jsonify({ 'repos': extract_repos_info(session) })

    @app.route('/api/v1/github/analyze_skills')
    @login_required
    def _analyze_skills():
        for account in current_user.github_accounts:
            current_app.default_queue.enqueue(detect_languages, account.id)
        return jsonify({'status':'Skills detection started'})


