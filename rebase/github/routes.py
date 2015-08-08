from flask import redirect, url_for, session, request, jsonify, render_template
from flask.ext.login import login_required
from flask_oauthlib.client import OAuth

def register_github_routes(app):
    oauth = OAuth(app)
    github = oauth.remote_app(
        'github',
        consumer_key='ccfe7b7be7560c9a112e',
        consumer_secret='1779c1d363dec567c81c01ef266e4d3f30f79a8d',
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
            repos = github.get('user/repos')
            app.logger.debug(repos.data)
            return render_template('github.html', data=me.data, repos=repos.data);
        return github.authorize(callback=url_for('github_authorized', redirect='github_root', _external=True))

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
        app.logger.debug(resp)
        session['github_token'] = (resp['access_token'], '')
        return redirect(url_for(request.args['redirect']))

    @app.route('/github/repos')
    @login_required
    def repos():
        if 'github_token' in session:
            me = github.get('user/repos')
            app.logger.debug(me.data)
            return jsonify({'repos': me.data})
        return redirect(url_for('github_login'))

    @github.tokengetter
    @login_required
    def get_github_oauth_token():
        return session.get('github_token')
