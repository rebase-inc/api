# How to install the app for local development

0. Go through https://devcenter.heroku.com/articles/getting-started-with-python
1. Install PostgreSQL locally. On Mac, see http://postgresapp.com
2. ```createdb rebase_dev```
3. Create and activate a Python Virtual Environment
4. ```pip install -r requirements.txt```
5. ```source setup.sh```
6. python manage.py db init
7. python manage.py db migrate
8. python manage.py db upgrade
9. foreman start

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
heroku config:set APP_SETTINGS=alveare.common.config.StagingConfig --remote stage
heroku config:set APP_SETTINGS=alveare.common.config.ProductionConfig --remote pro
```
