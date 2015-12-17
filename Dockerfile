FROM python:3.4
RUN mkdir /uploads
RUN mkdir /api
WORKDIR /api
ENV APP_SETTINGS=rebase.common.docker.Dev
CMD pip install -r requirements.txt;  python ./manage runserver -h 0.0.0.0 -p 5000
