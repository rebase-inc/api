# Architecture overview
Rebase is a Flask-based website.
All its backend components are Docker containers.
Its data are stored on a PostgreSQL database.
Background tasks are run with RQ which itself relies on Redis.
All logs are centralized in the rsyslog container.


# Development

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
### Make some change in the models (add a column, etc.)
```bash
source env/docker.bash
# get inside a container that has the api virtualenv
_bash web
/venv/api/bin/alembic current
/venv/api/bin/alembic revision --autogenerate -m "Add account table"
# exit the container (ctrl-d)
```
### Review the generated script! This is very important, as the auto-generation is far from perfect.
```bash
# upgrade your local database to verify the generated script works
_upgrade
```
### ideally, run the unit and functional tests now...
### commit your migration script

