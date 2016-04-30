# Architecture overview
Rebase is a Flask-based website.
All its backend components are Docker containers.
Its data are stored on a PostgreSQL database.
Background tasks are run with RQ which itself relies on Redis.
All logs are centralized in the rsyslog container.


# Development
## getting up and running with Docker
0. Install docker on your dev machine
1. Go to [Docker Hub](https://hub.docker.com) and register
2. Tell the Rebase organization admin to add your username to the org.
3. ```cd ~/repo/api``
4. ```docker login```
5. ```docker-compose pull```
6. ```docker-compose up```


## Testing
Testing is currently mostly broken...

```bash
nosetests rebase/tests

# running the tests in parallel:
nosetests --processes=-1 --process-timeout=999 rebase/tests
```
# GitHub Integration
## Register a new GitHub application
0. Go here: https://github.com/settings/applications/new
1. In the field 'Authorization callback URL', copy: 'http://localhost:3000/api/v1/github/authorized'
2. Save these 2 lines into .github_setup and source it:
```bash
export GITHUB_CLIENT_ID=<your_github_app_id>
export GITHUB_CLIENT_SECRET=<your_github_app_secret_key>
```

# Database Migration
## How to create a migration script:
### 1. Make some change in the models (add a column, etc.)
```bash
source env/docker.bash
# get inside a container that has the api virtualenv
_bash web
/venv/api/bin/alembic current
/venv/api/bin/alembic revision --autogenerate -m "Add account table"
# exit the container (ctrl-d)
```
### 2. Review the generated script! This is very important, as the auto-generation is far from perfect.
### 3. Migrate your local DB
```bash
# upgrade your local database to verify the generated script works
_upgrade
```
### 4. Ideally, run the unit and functional tests now...
### 5. Commit your migration script

# Creating/Renewing SSL Certificates
We use LetsEncrypt.org as the Certificate Authority.
Their certificates expires after 90 days.
```bash
$ cd repo/api
$ source env/docker.bash
# Letsencrypt has very strict limits on the number of certs generated per day for one domain.
# So, first, let's test the certificate generation so we can verify it will work without hurting our rate limit.
$ _generate_certificate alpha.rebaseapp.com
# If this succeeds, run the same command with the --production flag
$ _generate_certificate --production alpha.rebaseapp.com
# In your web browser, go to https://alpha.rebaseapp.com and verify the certificate expiration date (today+90days).
```
