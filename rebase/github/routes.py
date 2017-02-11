import hashlib
from logging import getLogger
from urllib.parse import urljoin, urlparse
from uuid import uuid1
from rq import Queue
from rq.registry import StartedJobRegistry, FinishedJobRegistry, DeferredJobRegistry
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

LOGGER = getLogger()


class SanitizedJob(dict):

    def __init__(self, name, job = None):
        super().__init__()
        self.update(name = name)
        self.update(progress = job.meta or {} if job else {})
        self.update(status = job.get_status() if job else 'finished')
        self.update(id = hashlib.sha256(job.id.encode('utf-8')).hexdigest() if job else None)


class StatusAgnosticQueue(Queue):
    KEY = 'rq:job:*'

    @property
    def started_registry(self):
        if not hasattr(self, '_started_registry'):
            self._started_registry = StartedJobRegistry(name = self.name, connection = self.connection)
        return self._started_registry

    @property
    def finished_registry(self):
        if not hasattr(self, '_finished_registry'):
            self._finished_registry = FinishedJobRegistry(name = self.name, connection = self.connection)
        return self._finished_registry

    @property
    def deferred_registry(self):
        if not hasattr(self, '_deferred_registry'):
            self._deferred_registry = DeferredJobRegistry(name = self.name, connection = self.connection)
        return self._deferred_registry
    
    def find_jobs(self, predicate = lambda job: True):
        job_ids = self.started_registry.get_job_ids()
        job_ids += self.deferred_registry.get_job_ids()
        for job in filter(predicate, (self.fetch_job(job_id) for job_id in job_ids)):
            # if job and job.id in self.deferred_registry.get_job_ids():
            #     job.status = 'deferred' # this is a little sketchy...If you see weird side effects, look here
            yield job 

def scan_github_account(github_account, connection_pool = None):
    contractor = github_account.user.roles[0]
    remote_work_history = RemoteWorkHistory.query.get(contractor.id) or RemoteWorkHistory(contractor)
    remote_work_history.github_accounts.append(github_account)
    remote_work_history.analyzing = True
    DB.session.add(remote_work_history)
    DB.session.commit()
    crawler_queue = Queue('private_github_scanner', connection = StrictRedis(connection_pool = connection_pool), default_timeout = 3600)
    population_queue = Queue('population_analyzer', connection = StrictRedis(connection_pool = connection_pool), default_timeout = 600)
    scan_repos_job = crawler_queue.enqueue_call(func = 'scanner.scan_authorized_repos', args = (github_account.access_token, ))
    update_job = population_queue.enqueue_call(func = 'leaderboard.update_ranking_for_user', args = (github_account.github_user.login,), depends_on = scan_repos_job)
    return (scan_repos_job, update_job)

def get_oauth_app_hostname(request):
    host = request.environ['HTTP_HOST']
    if not host.startswith('http'):
        host2 = '//'+host
    else:
        host2 = host
    oauth_app_hostname = urlparse(host2).hostname
    #LOGGER.debug('oauth_app_hostname: %s', oauth_app_hostname)
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
        LOGGER.debug('request.environ:')
        LOGGER.debug('%s', request.environ)
        for account in current_user.github_accounts:
            LOGGER.debug('Verifying Github account '+account.github_user.login)
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
            LOGGER.debug('emails: %s', emails)
            for email in emails:
                if email['primary']:
                    primary_email = email['email']
                    break
            github_user = GithubUser(authenticated_user.id, authenticated_user.login, authenticated_user.name)
            rebase_user = User(authenticated_user.name or primary_email, primary_email, uuid1().hex) # TODO: Remove
            rebase_contractor = Contractor(rebase_user) # TODO: Remove
            github_account = GithubAccount(skillgraph, github_user, rebase_user, access_token) # TODO: Refactor models
            DB.session.add(github_account)
            DB.session.commit()
            login_user(rebase_user, remember=True)
            github_account.user.set_role(rebase_contractor.id)
            scan_github_account(github_account, app.redis_pool)
        else:
            github_account = GithubAccount.query.filter_by(app_id = app.config['GITHUB_APP_CLIENT_ID'], github_user_id = github_user.id).first()
            github_account.access_token = access_token
            DB.session.add(github_account)
            DB.session.commit()
            login_user(github_account.user, remember=True)
            # unfortunately we still need a current role until we remove the role of roles in queries
            github_account.user.set_role(github_account.user.roles[0].id)

        return redirect('/')

    @app.route('/api/v1/github/scan', methods = ['POST'])
    @login_required
    def scan_user():
        if len(current_user.github_accounts) != 1:
            raise Exception('User does not have exactly one github account!')
        account = current_user.github_accounts[0]
        scan_job, rankings_job = scan_github_account(account, app.redis_pool)
        return jsonify({ 'jobs': [
            SanitizedJob('scan', scan_job),
            SanitizedJob('update', rankings_job),
            ]})

    @app.route('/api/v1/github/update_rankings', methods = ['POST'])
    @login_required
    def update_rankings():
        account = current_user.github_accounts[0]
        connection = StrictRedis(connection_pool = app.redis_pool)
        q = Queue('population_analyzer', connection = connection, default_timeout = 3600)
        job = q.enqueue_call(func = 'leaderboard.update_ranking_for_user', args = (account.github_user.login, ))
        return jsonify({ 'jobs': [ SanitizedJob('update', job) ] })

    @app.route('/api/v1/github/jobs', methods = ['GET'])
    @login_required
    def scan_status():
        github_account = GithubAccount.query.filter_by(user_id = current_user.id).first()
        scan_queue = StatusAgnosticQueue('private_github_scanner', connection = StrictRedis(connection_pool = app.redis_pool))
        pop_queue = StatusAgnosticQueue('population_analyzer', connection = StrictRedis(connection_pool = app.redis_pool))
        scan_jobs = list(SanitizedJob('scan', job) for job in scan_queue.find_jobs(lambda job: job.args[0] == github_account.access_token))
        pop_jobs = list(SanitizedJob('update', job) for job in pop_queue.find_jobs(lambda job: job.args[0] == github_account.github_user.login))
        ze_jobs = list(job for job in pop_queue.find_jobs(lambda job: job.args[0] == github_account.github_user.login))
        return jsonify({ 'jobs': scan_jobs + pop_jobs })

