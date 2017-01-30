from logging import getLogger
from urllib.parse import urljoin, urlparse
from uuid import uuid1
from rq import Queue
from redis import StrictRedis

from flask import redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user, login_user, logout_user
from flask_oauthlib.client import OAuth
from github import Github
from redis import StrictRedis

from ..common.database import DB
from ..common import config
from ..models import (
    Contractor,
    GithubAccount,
    GithubOAuthApp,
    GithubUser,
    RemoteWorkHistory,
    User
)

from .session import make_session


OAUTH_SETTINGS = {
    'request_token_params': {'scope': 'user repo'},
    'base_url': 'https://api.github.com/',
    'request_token_url': None,
    'access_token_method': 'POST',
    'access_token_url': 'https://github.com/login/oauth/access_token',
    'authorize_url': 'https://github.com/login/oauth/authorize'
}

logger = getLogger()

def analyze_contractor_skills(app, github_account):
    contractor = next(filter(lambda r: r.type == 'contractor', current_user.roles), None)
    if contractor:
        remote_work_history = RemoteWorkHistory.query_by_user(current_user).first() or RemoteWorkHistory(contractor)
        remote_work_history.github_accounts.append(github_account)
        remote_work_history.analyzing = True
        DB.session.add(remote_work_history)
        DB.session.commit()
        crawler_queue = Queue('private_github_scanner', connection = StrictRedis(connection_pool = app.redis_pool))
        population_queue = Queue('population_analyzer', connection = StrictRedis(connection_pool = app.redis_pool), default_timeout = 3600)
        scan_repos = crawler_queue.enqueue_call(func = 'scanner.scan_authorized_repos', args = (github_account.access_token, ))
        population_queue.enqueue_call(func = 'leaderboard.update_ranking_for_user', args = (github_account.github_user.login,), depends_on = scan_repos)

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

    github_oauth_app = OAuth(app).remote_app(
        'skillgraph', # can we get this from environment?
        consumer_key = app.config['GITHUB_APP_CLIENT_ID'],
        consumer_secret = app.config['GITHUB_APP_CLIENT_SECRET'],
        **OAUTH_SETTINGS
    )

    skillgraph = GithubOAuthApp.query.filter_by(name='skillgraph').first()

    @app.route(app.config['API_URL_PREFIX'] + '/github/login', methods=['GET'])
    def login():
        return github_oauth_app.authorize(callback=url_for('authorized', _external=True))

    @app.route(app.config['API_URL_PREFIX'] + '/github/verify', methods=['GET'])
    @login_required
    def verify_all_github_tokens():
        logger.debug('request.environ:')
        logger.debug('%s', request.environ)
        for account in current_user.github_accounts:
            logger.debug('Verifying Github account '+account.github_user.login)
            make_session(account, app, current_user)
        return jsonify({'success':'complete'})

    @app.route(app.config['API_URL_PREFIX'] + '/github/logout', methods=['GET'])
    @login_required
    def logout():
        logout_user()
        return redirect('/')

    @app.route(app.config['API_URL_PREFIX'] + '/github/authorized', methods=['GET'])
    def authorized():
        github_data = github_oauth_app.authorized_response()
        if github_data is None or 'error' in github_data:
            response = jsonify(message='Invalid GitHub oauth data')
            response.status_code = 401
            return response

        access_token = github_data['access_token']
        github_api = Github(login_or_token=access_token)
        authenticated_user = github_api.get_user()
        github_user = GithubUser.query.get(authenticated_user.id)
        if not github_user:
            emails =  authenticated_user.get_emails()
            logger.debug('emails: %s', emails)
            for email in emails:
                if email['primary']:
                    primary_email = email['email']
                    break
            github_user = GithubUser(authenticated_user.id, authenticated_user.login, authenticated_user.name)
            rebase_user = User(authenticated_user.name, primary_email, uuid1().hex) # TODO: Remove
            rebase_contractor = Contractor(rebase_user) # TODO: Remove
            github_account = GithubAccount(skillgraph, github_user, rebase_user, access_token) # TODO: Refactor models
            DB.session.add(github_account)
            DB.session.commit()
            analyze_contractor_skills(app, github_account)
        else:
            github_account = GithubAccount.query.filter_by(app_id = app.config['GITHUB_APP_CLIENT_ID'], github_user_id = github_user.id).first()
            github_account.access_token = access_token
            DB.session.add(github_account)
            DB.session.commit()

        login_user(github_account.user, remember=True)
        github_account.user.set_role(0) # we don't actually care about the role anymore

        return redirect('/')

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
        return jsonify({'to':'do'})

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
