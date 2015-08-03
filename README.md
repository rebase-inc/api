# How to install the app for local development

0. Install PostgreSQL locally. On Mac, see http://postgresapp.com
1. ```createdb rebase_dev```
1. Create and activate a Python Virtual Environment
2. ```pip install -r requirements.txt```
3. ```source setup.sh```
4. python manage.py db init
5. python manage.py db migrate
6. python manage.py db upgrade

# How to install the app on Heroku

(loosely inspired by this: https://realpython.com/blog/python/flask-by-example-part-1-project-setup/)

```bash
#To use SSH when pushing to Heroku, I'd recommend adding your pub key to your Heroku account:
heroku keys:add

#Let's create 2 apps, one for verification the other for production:
heroku create rebase-pro
heroku create rebase-stage

git remote add pro git@heroku.com:rebase-pro.git
git remote add stage git@heroku.com:rebase-stage.git

#To set an environment variable on a remote configuration:
heroku config:set APP_SETTINGS=alveare.common.config.StagingConfig --remote stage --app myapp
heroku config:set APP_SETTINGS=alveare.common.config.ProductionConfig --remote pro --app myapp
```


# api
