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
1. Save these 2 lines into .github_setup and source it:
```bash
export GITHUB_CLIENT_ID=<your_github_app_id>
export GITHUB_CLIENT_SECRET=<your_github_app_secret_key>
```


