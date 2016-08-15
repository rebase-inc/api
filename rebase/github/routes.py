from logging import getLogger
from urllib.parse import urljoin, urlparse

from flask import redirect, url_for, request, jsonify, current_app
from flask.ext.login import login_required, current_user

from rebase.common.database import DB
from rebase.common.exceptions import NotFoundError
from rebase.github.oauth_apps import apps

from rebase.github.scanners import (
    import_github_repos,
    extract_repos_info,
)
from rebase.github.session import make_session
from rebase.models import (
    Contractor,
    GithubAccount,
    GithubUser,
    RemoteWorkHistory,
    SkillSet,
    User
)


logger = getLogger()


def analyze_contractor_skills(github_account):
    contractor = next(filter(lambda r: r.type == 'contractor', current_user.roles), None)
    if contractor:
        remote_work_history = RemoteWorkHistory.query_by_user(current_user).first() or RemoteWorkHistory(contractor)
        remote_work_history.github_accounts.append(github_account)
        remote_work_history.analyzing = True
        DB.session.add(remote_work_history)
        DB.session.commit()
        current_app.default_queue.enqueue_call(func='rebase.github.languages.detect_languages', args=(github_account.id,), timeout=3600 ) # timeout = 1h


def get_oauth_app_hostname(request):
    host = request.environ['HTTP_HOST'] 
    if not host.startswith('http'):
        host2 = '//'+host
    else:
        host2 = host
    oauth_app_hostname = urlparse(host2).hostname
    #logger.debug('oauth_app_hostname: %s', oauth_app_hostname)
    return oauth_app_hostname


def register_github_routes(app):
    @app.route('/api/v1/github', methods=['GET'])
    @login_required
    def login():
        github_apps = apps(app)
        oauth_app_hostname = get_oauth_app_hostname(request)
        return github_apps[oauth_app_hostname].authorize(callback=url_for('authorized', _external=True))

    @app.route('/api/v1/github/verify')
    @login_required
    def verify_all_github_tokens():
        logger.debug('request.environ:')
        logger.debug('%s', request.environ)
        for account in current_user.github_accounts:
            logger.debug('Verifying Github account '+account.github_user.login)
            make_session(account, current_app, current_user)
        return jsonify({'success':'complete'})

    @app.route('/api/v1/github/logout')
    @login_required
    def logout():
        session.pop('github_token', None)
        return redirect(url_for('login'))

    @app.route('/api/v1/github/authorized')
    @login_required
    def authorized():
        github_apps = apps(app)
        oauth_app_hostname = get_oauth_app_hostname(request)
        github = github_apps[oauth_app_hostname]
        resp = github.authorized_response()
        if resp is None:
            return 'Access denied: reason={error} error={error_description}'.format(**request.args)
        elif 'error' in resp:
            if resp['error'] == 'bad_verification_code': return redirect(url_for('github_login'))
            else: return 'Unknown error: {}'.format(resp['error'])
        else:
            access_token = resp['access_token']
            _github_user = github.get('user', token=(access_token, '')).data
            github_user = GithubUser.query.get(_github_user['id'])
            if not github_user:
                github_user = GithubUser(*[ _github_user[k] for k in ('id', 'login', 'name') ])
            github_app = github.github_app
            github_account = GithubAccount.query.filter_by(
                app_id=github_app.client_id,
                github_user_id=github_user.id,
                user_id=current_user.id
            ).first()
            if github_account:
                github_account.access_token = access_token
            else:
                github_account = GithubAccount(github_app, github_user, current_user, access_token)
            DB.session.add(github_account)
            DB.session.commit()
            analyze_contractor_skills(github_account)
        return redirect('/')

    @app.route('/api/v1/github/import_repos', methods=['POST'])
    @login_required
    def import_repos():
        new_mgr_roles = import_github_repos(request.json['repos'], current_user, DB.session)
        return jsonify({'roles': new_mgr_roles});

    @app.route('/api/v1/github_accounts/<int:github_user_id>/importable_repos')
    @login_required
    def importable_repos(github_user_id):
        github_apps = apps(app)
        oauth_app_hostname = get_oauth_app_hostname(request)
        github = github_apps[oauth_app_hostname]
        account = GithubAccount.query.get_or_404((github.github_app.client_id, github_user_id, current_user.id))
        session = make_session(account, current_app, current_user)
        return jsonify({ 'repos': extract_repos_info(session) })

    @app.route('/api/v1/github_accounts/<int:github_user_id>/import/<int:project_id>', methods=['POST'])
    @login_required
    def import_project(github_user_id, project_id):
        github_apps = apps(app)
        oauth_app_hostname = get_oauth_app_hostname(request)
        github = github_apps[oauth_app_hostname]
        account = GithubAccount.query.get_or_404((github.github_app.client_id, github_user_id, current_user.id))
        session = make_session(account, current_app, current_user)
        repo = next(filter(lambda repo: repo['id']==project_id, extract_repos_info(session)), None)
        if not repo:
            raise NotFoundError('Github Project', project_id)
        new_mgr_roles = import_github_repos({ repo['id']: repo }, current_user, DB.session)
        return jsonify({'roles': new_mgr_roles});

    @app.route('/api/v1/github/analyze_skills')
    @login_required
    def _analyze_skills():
        for account in current_user.github_accounts:
            current_app.default_queue.enqueue('rebase.github.languages.detect_languages', account.id)
        return jsonify({'status':'Skills detection started'})


