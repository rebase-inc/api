# Architecture overview
Rebase is a Flask-based website. Its data are stored on a PostgreSQL database.
Background task are run with RQ which itself relies on Redis.
Supervisord is used to managed rqworker processes.

# Local Development
## Installation

0. Go through https://devcenter.heroku.com/articles/getting-started-with-python
1. Install PostgreSQL locally. On Mac, see http://postgresapp.com
2. ```createdb rebase_web```
3. ```createdb rebase_test```
4. ```brew install redis```
5. ```launchctl load ~/Library/LaunchAgents/homebrew.mxcl.redis.plist```
6. ```easy_install supervisor```
7. ```supervisord -c etc/supervisord.conf```
4. Create and activate a Python Virtual Environment
5. ```pip install -r requirements.txt```
6. ```source setup.sh```
7. ```python manage.py db init```
8. ```python manage.py db migrate```
9. ```python manage.py db upgrade```
10. ```foreman start``` This should launch a server on localhost

## Testing
```bash
nosetests rebase/tests
```
# GitHub Integration
## Register a new GitHub application 
0. Go here: https://github.com/settings/applications/new
1. Save these 2 lines into .github_setup and source it:
```bash
export GITHUB_CLIENT_ID=<your_github_app_id>
export GITHUB_CLIENT_SECRET=<your_github_app_secret_key>
```


# Heroku Development
We are going to create 2 apps. One for production, the other for staging.
So, first you should register 2 more [GitHub applications](https://github.com/settings/applications/new).

## Installation
```bash
# To use SSH when pushing to Heroku, I'd recommend adding your pub key to your Heroku account:
heroku keys:add

# Let's create 2 apps, one for verification the other for production:
heroku create rebase-pro
heroku create rebase-stage

git remote add pro git@heroku.com:rebase-pro.git
git remote add stage git@heroku.com:rebase-stage.git

# To set an environment variable on a remote configuration:
heroku config:set APP_SETTINGS=rebase.common.config.StagingConfig --remote stage
heroku config:set APP_SETTINGS=rebase.common.config.ProductionConfig --remote pro

# Connect the GitHub apps to their respective Heroku apps
heroku config:set GITHUB_CLIENT_ID=<some_key> -a rebase-stage
heroku config:set GITHUB_CLIENT_SECRET=<some_key> -a rebase-stage
heroku config:set GITHUB_CLIENT_ID=<some_key> -a rebase-stage
heroku config:set GITHUB_CLIENT_SECRET=<some_key> -a rebase-stage

# Install the PostGreSQL add-on on both apps:
# the staging app
heroku addons:create heroku-postgresql:hobby-dev --as WEB --app rebase-stage
heroku addons:create heroku-postgresql:hobby-dev --as TEST --app rebase-stage
heroku pg:promote WEB -a rebase-stage
heroku run python manage.py db upgrade --app rebase-stage
git push stage master

# the production app
heroku addons:create heroku-postgresql:hobby-dev --as WEB --app rebase-pro
heroku addons:create heroku-postgresql:hobby-dev --as TEST --app rebase-pro
heroku pg:promote WEB -a rebase-pro
heroku run python manage.py db upgrade --app rebase-pro
git push pro master

# create a first admin unser (optional):
heroku run ./manage create_admin rapha@joinrebase.com supersecretpassword --first Raphael --last Goyran -a rebase-pro
```

## See the final product:
```heroku open -a rebase-pro```

Navigate to http://rebase-pro.herokuapp.com/admin/user to see the list users

## Testing
```bash
heroku run nosetests rebase/tests -a rebase-stage
```

## How to reset the database
```bash
heroku pg:reset DATABASE_URL -a rebase-stage
heroku run ./manage db upgrade -a rebase-stage
```
