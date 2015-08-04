# How to install the app for local development

0. Go through https://devcenter.heroku.com/articles/getting-started-with-python
1. Install PostgreSQL locally. On Mac, see http://postgresapp.com
2. ```createdb rebase_dev```
2. ```createdb rebase_test```
3. Create and activate a Python Virtual Environment
4. ```pip install -r requirements.txt```
5. ```source setup.sh```
6. or: ```source test_setup.sh``` if you just want to run the unit/functional tests
6. ```python manage.py db init```
7. ```python manage.py db migrate```
8. ```python manage.py db upgrade```
9. ```foreman start```

# How to run the tests
```bash
source test_setup.sh
nosetests rebase/tests
```


# How to install the app on Heroku

```bash
#To use SSH when pushing to Heroku, I'd recommend adding your pub key to your Heroku account:
heroku keys:add

#Let's create 2 apps, one for verification the other for production:
heroku create rebase-pro
heroku create rebase-stage

git remote add pro git@heroku.com:rebase-pro.git
git remote add stage git@heroku.com:rebase-stage.git

#To set an environment variable on a remote configuration:
heroku config:set APP_SETTINGS=rebase.common.config.StagingConfig --remote stage
heroku config:set APP_SETTINGS=rebase.common.config.ProductionConfig --remote pro

# Install the PostGreSQL add-on on both apps:
# the staging app
heroku addons:create heroku-postgresql:hobby-dev --app rebase-stage
git push stage master
heroku run python manage.py db upgrade --app rebase-stage

# the production app
heroku addons:create heroku-postgresql:hobby-dev --app rebase-pro
git push pro master
heroku run python manage.py db upgrade --app rebase-pro
```

# How to reset the database
```bash
heroku pg:reset --confirm rebase-stage DATABASE_URL -a rebase-stage
heroku run ./manage db upgrade -a rebase-stage
```
