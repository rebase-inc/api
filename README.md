# Architecture overview
Rebase is a Flask-based website.
All its backend components are Docker containers.
Its data are stored on a PostgreSQL database.
Background tasks are run with RQ which itself relies on Redis.
All logs are centralized in the rsyslog container.


# How To Connect To Our Production Server
Add this snippet to your ~/.ssh/config file:
```
Host alpha
Hostname alpha.rebaseapp.com
User ubuntu
Port 2222

# for cloning/push to our git repositories:
Host alpha-git
Hostname alpha.rebaseapp.com
User git
```

# Development
## getting up and running with Docker
0. Install docker on your dev machine
1. Go to [Docker Hub](https://hub.docker.com) and register
2. Tell the Rebase organization admin to add your username to the org.
3. ```cd ~/repo/api``
4. ```docker login```
5. ```docker-compose pull```
6. ```docker-compose up```

# Initialize the database
The first time the system is installed, whether in dev or production mode,
we need to install a schema for our models.
And, in the case of dev,

## dev mode
```
. env/docker.bash
_manage data create
_manage data populate
```

## production mode
```
. env/docker.bash
_manage data create
```

## How to update production after a UI change
```bash
ssh alpha
cd ~/repo/react
git pull origin master
cd ../api
. ~/.rebase
. env/docker.bash
_compose ps
# notice how app/code2resume container is Exited
_compose start -d app
# or _compose start -d code2resume
# to see what's going in the Node.JS world:
docker logs -f api_app_1 
# reload the web page for changes to take effect (duh)
```
## Modify /etc/hosts on your machine
Add 2 lines:
```
192.168.29.128 dev
192.168.29.128 c2r
```
Note that the IP should match your docker machine's IP.
If you are running hypervisor or native on linux, just put 127.0.0.1

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
# Make sure the system is up and running (nginx in particular)
$ _compose ps
$ _bash nginx
# Switch Nginx to ACME challenge mode (listen to 80 and respond to 'well-known ACME challenge'
$ listen 80
# Letsencrypt has very strict limits on the number of certs generated per day for one domain.
# So, first, let's test the certificate renewal so we can verify it will work without hurting our rate limit.
$ ./certbot-auto renew --dry-run
# If this succeeds, run the same command without the --dry-run:
$ ./certbot-auto renew
# Switch back to listening for 443 traffic
$ listen 443
# In your web browser, go to https://alpha.rebaseapp.com and verify the certificate expiration date (today+90days).
```

# Manage RQ Workers & Queues
## in development
[RQ Dashboard](http://c2r:4444)
## in production
First you need to tunnel through to the Docker host.
```bash
# assuming your SSH config has an 'alpha' Host defined...
ssh -L 55555:localhost:4444 alpha
```
[RQ Dashboard](http://localhost:55555)


# Data Mining with Jupyter & Apache Spark
## in development
[Jupyter Dev](http://dev:8888)
## in production
First you need to tunnel through to the Docker host.
```bash
# assuming your SSH config has an 'alpha' Host defined...
ssh -L 8888:localhost:8888 alpha
```
[Jupyter Production](http://localhost:8888)
## How crawl a Github user's public repositories
```
from rebase.github.crawl import scan

scan('alex')
scan(['rapha-opensource', 'alex'])
```
