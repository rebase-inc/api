from logging import getLogger
from urllib.parse import urljoin, urlparse
from uuid import uuid1
from rq import Queue
from redis import StrictRedis

from flask import redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user, login_user
from redis import StrictRedis

from ..common.database import DB
from ..common.exceptions import NotFoundError
from ..common import config
from ..models import (
    Contractor,
    GithubAccount,
    GithubUser,
    RemoteWorkHistory,
    SkillSet,
    User
)

from .notifications import get_notification
from .oauth_apps import apps
from .scanners import import_github_repos, extract_repos_info
from .session import make_session


logger = getLogger()


def analyze_contractor_skills(app, github_account):
    contractor = next(filter(lambda r: r.type == 'contractor', current_user.roles), None)
    if contractor:
        remote_work_history = RemoteWorkHistory.query_by_user(current_user).first() or RemoteWorkHistory(contractor)
        remote_work_history.github_accounts.append(github_account)
        remote_work_history.analyzing = True
        DB.session.add(remote_work_history)
        DB.session.commit()
        queue = Queue('private_crawler', connection = StrictRedis(connection_pool = app.redis_pool))
        queue.enqueue_call(
            func = 'scanner.scan_all_repos',
            args = (github_account.access_token, contractor.skill_set.id),
            timeout = 3600
        )


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
    @app.route(app.config['API_URL_PREFIX'] + 'github', methods=['GET'])
    @login_required
    def login():
        github_apps = apps(app)
        oauth_app_hostname = get_oauth_app_hostname(request)
        return github_apps[oauth_app_hostname].authorize(callback=url_for('authorized', _external=True))

    @app.route(app.config['API_URL_PREFIX'] + 'github/verify', methods=['GET'])
    @login_required
    def verify_all_github_tokens():
        logger.debug('request.environ:')
        logger.debug('%s', request.environ)
        for account in current_user.github_accounts:
            logger.debug('Verifying Github account '+account.github_user.login)
            make_session(account, app, current_user)
        return jsonify({'success':'complete'})

    @app.route(app.config['API_URL_PREFIX'] + 'github/logout', methods=['GET'])
    @login_required
    def logout():
        session.pop('github_token', None)
        return redirect(url_for('login'))

    @app.route(app.config['API_URL_PREFIX'] + 'github/authorized', methods=['GET'])
    def authorized():
        github_app = apps(app)[get_oauth_app_hostname(request)]
        response = github_app.authorized_response()
        if response is None:
            return 'Access denied: reason={error} error={error_description}'.format(**request.args)
        elif 'error' in response:
            return redirect(url_for('github_login')) if response['error'] == 'bad_verification_code' else 'Unknown error: {}'.format(response['error'])

        # if we got to this point, GitHub auth was successful
        access_token = response['access_token']
        github_user_data = github_app.get('user', token = (access_token, '')).data
        github_user = GithubUser.query.get(github_user_data['id'])

        # slightly different object for use below
        github_app = github_app.github_app

        if not github_user:
            # this github user has never been introduced to Rebase before, so we need to build the models
            github_user = GithubUser(github_user_data['id'], github_user_data['login'], github_user_data['name'])
            user = User(
                github_user_data['name'],
                github_user_data['email'] if github_user_data['email'] else '__phony_address__@rebase.com',
                uuid1().hex
            )
            Contractor(user)
            github_account = GithubAccount(github_app, github_user, user, access_token)
        else:
            # this github user has been introduce to rebase, so we're going to try to find their Rebase user
            user = GithubAccount.query.filter_by(app_id = github_app.client_id, github_user_id = github_user.id ).first().user
            github_account = GithubAccount.query.filter_by(
                app_id = github_app.client_id,
                github_user_id = github_user.id,
                user_id = user.id
            ).first() or GithubAccount(github_app, github_user, user, access_token)
            github_account.access_token = access_token

        # whether we've created a new user or found an existing user, we need to log them in
        role_id = int(request.cookies.get('role_id', 0))
        login_user(user, remember=True)
        current_role = user.set_role(role_id)

        DB.session.add(github_account)
        DB.session.commit()
        analyze_contractor_skills(app, github_account)
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
        session = make_session(account, app, current_user)
        return jsonify({ 'repos': extract_repos_info(session) })

    @app.route('/api/v1/github_accounts/<int:github_user_id>/import/<int:project_id>', methods=['POST'])
    @login_required
    def import_project(github_user_id, project_id):
        github_apps = apps(app)
        oauth_app_hostname = get_oauth_app_hostname(request)
        github = github_apps[oauth_app_hostname]
        account = GithubAccount.query.get_or_404((github.github_app.client_id, github_user_id, current_user.id))
        session = make_session(account, app, current_user)
        repo = next(filter(lambda repo: repo['id']==project_id, extract_repos_info(session)), None)
        if not repo:
            raise NotFoundError('Github Project', project_id)
        new_mgr_roles = import_github_repos({ repo['id']: repo }, current_user, DB.session)
        return jsonify({'roles': new_mgr_roles});

    @app.route('/api/v1/github/analyze_skills')
    @login_required
    def _analyze_skills():
        for account in current_user.github_accounts:
            queue(app, 'default').enqueue_call(
                'rebase.github.languages.scan_public_and_private_repos',
                args=(account.id,),
                timeout=3600,
            )
        return jsonify({'status':'Skills detection started'})

    @app.route('/api/v1/github/crawl_status')
    @login_required
    def crawl_status():
        return jsonify(
            get_notification(
                StrictRedis(connection_pool=app.redis_pool),
                Contractor.query.filter_by(user_id=current_user.id).one().id
            )
        )

    @app.route('/api/v1/github/update_rankings')
    @login_required
    def update_rankings():
        for account in current_user.github_accounts:
            queue(app, 'population').enqueue_call(
                'rebase.db_jobs.contractor.update_user_rankings',
                args=(account.github_user.login,)
            )
        return jsonify({
            'status': 'update_user_rankings jobs launched'
        })
